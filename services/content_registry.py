import json
from dataclasses import dataclass
from pathlib import Path

from app_paths import DATA_DIR
from config import (
    CS_APPS_CHANNEL_ID,
    CS_STG4_CHANNEL_ID,
    CS_STG4_DELETED_CHANNEL_ID,
    CS_STG4_ONEFILE_CHANNEL_ID,
)


@dataclass(frozen=True)
class ContentTarget:
    command_key: str
    channel_id: int
    message_ids: list[int]


class ContentRegistry:
    def __init__(
        self,
        content_items_path: Path = DATA_DIR / "content_items.json",
    ) -> None:
        self.content_items_path = content_items_path
        self.content_items = []
        self.command_to_channel_key = {}
        if not content_items_path.exists():
            raise FileNotFoundError(
                f"Content catalog not found: {content_items_path}. "
                "The legacy two-file fallback has been removed; "
                "content_items.json is now required."
            )
        self._load_content_items(content_items_path)
        self.validation_report = self.validate()
        self.print_validation_report()

    def _load_json(self, path: Path) -> dict:
        if not path.exists():
            raise FileNotFoundError(f"Required content map is missing: {path}")
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _load_content_items(self, path: Path) -> None:
        with path.open("r", encoding="utf-8") as file:
            self.content_items = json.load(file)

        self.button_to_command = {}
        self.command_to_values = {}
        for item in self.content_items:
            if not item.get("active", True):
                continue
            button_label = item.get("button_label")
            command_key = item.get("command_key")
            if not button_label or not command_key:
                continue
            self.button_to_command[button_label] = command_key
            self.command_to_values[command_key] = item.get("message_ids", [])
            self.command_to_channel_key[command_key] = item.get("channel_key")

    def validate(self) -> dict[str, list[str]]:
        button_commands = set(self.button_to_command.values())
        value_commands = set(self.command_to_values)
        missing_values = sorted(button_commands - value_commands)
        unreachable_values = sorted(value_commands - button_commands)
        empty_values = []
        invalid_message_ids = []

        for command_key, value in self.command_to_values.items():
            values = value if isinstance(value, list) else [value]
            if not values:
                empty_values.append(command_key)
                continue
            for message_id in values:
                if not isinstance(message_id, int):
                    invalid_message_ids.append(command_key)
                    break

        return {
            "missing_values": missing_values,
            "unreachable_values": unreachable_values,
            "empty_values": empty_values,
            "invalid_message_ids": invalid_message_ids,
        }

    def print_validation_report(self) -> None:
        print(
            "[content-registry] "
            f"buttons={len(self.button_to_command)} "
            f"commands={len(self.command_to_values)}"
        )
        for key, values in self.validation_report.items():
            if values:
                print(f"[content-registry] warning: {key}: {values[:20]}")

    def validate_strict(self) -> dict:
        """Validate every row in content_items.json, including inactive items.

        Returns a dict with findings:
          - total_items, catalog_available
          - inactive_items, inactive_ids
          - missing_button_label, missing_command_key
          - empty_message_ids, missing_channel_key
          - duplicate_button_labels, duplicate_command_keys

        Only meaningful when content_items.json is the active source.
        Does NOT replace validate() — this is an additional audit pass.
        """
        report: dict = {
            "total_items": len(self.content_items),
            "catalog_available": bool(self.content_items),
            "inactive_items": 0,
            "inactive_ids": [],
            "missing_button_label": [],
            "missing_command_key": [],
            "empty_message_ids": [],
            "missing_channel_key": [],
            "duplicate_button_labels": {},
            "duplicate_command_keys": {},
        }

        if not self.content_items:
            return report

        seen_labels: dict[str, list[str]] = {}
        seen_commands: dict[str, list[str]] = {}

        for item in self.content_items:
            item_id = item.get("id") or "<no id>"
            active = item.get("active", True)
            button_label = item.get("button_label")
            command_key = item.get("command_key")
            message_ids = item.get("message_ids")
            channel_key = item.get("channel_key")

            # 1. Track inactive items separately (not errors)
            if not active:
                report["inactive_items"] += 1
                report["inactive_ids"].append(item_id)

            # 2. Structural completeness checks
            if not button_label:
                report["missing_button_label"].append(item_id)
            if not command_key:
                report["missing_command_key"].append(item_id)

            # 3. Empty message_ids (empty list, null, or absent)
            if not message_ids or (isinstance(message_ids, list) and len(message_ids) == 0):
                report["empty_message_ids"].append(item_id)

            # 4. Missing channel_key
            if not channel_key:
                report["missing_channel_key"].append(item_id)

            # 5. Track for duplicates
            if button_label:
                if button_label not in seen_labels:
                    seen_labels[button_label] = []
                seen_labels[button_label].append(item_id)
            if command_key:
                if command_key not in seen_commands:
                    seen_commands[command_key] = []
                seen_commands[command_key].append(item_id)

        # Collect only actual duplicates (more than one occurrence)
        for label, ids in seen_labels.items():
            if len(ids) > 1:
                report["duplicate_button_labels"][label] = ids
        for key, ids in seen_commands.items():
            if len(ids) > 1:
                report["duplicate_command_keys"][key] = ids

        return report

    def print_strict_report(self, report: dict, verbose: bool = False) -> None:
        """Print the strict validation report.

        When verbose=False (default), prints only summary counts.
        When verbose=True, prints full item-level detail.
        """
        if not report["catalog_available"]:
            print(
                "[content-registry] strict: content_items.json not available "
                "(using legacy fallback files)"
            )
            return

        print(
            f"[content-registry] strict: scanning all {report['total_items']} "
            f"catalog items ({report['inactive_items']} inactive, "
            f"{report['total_items'] - report['inactive_items']} active)"
        )

        sections: list[tuple[str, str, list | dict]] = [
            ("inactive items (informational)", "inactive_ids", report["inactive_ids"]),
            ("items missing button_label", "missing_button_label", report["missing_button_label"]),
            ("items missing command_key", "missing_command_key", report["missing_command_key"]),
            ("items with empty message_ids", "empty_message_ids", report["empty_message_ids"]),
            ("items missing channel_key", "missing_channel_key", report["missing_channel_key"]),
        ]

        for title, _key, items in sections:
            if items:
                print(f"  [strict] {len(items)} {title}")
                if verbose:
                    for entry in items:
                        print(f"    - {entry}")

        if report["duplicate_button_labels"]:
            count = len(report["duplicate_button_labels"])
            print(f"  [strict] {count} duplicate button_label(s)")
            if verbose:
                for label, ids in report["duplicate_button_labels"].items():
                    print(f"    \"{label}\" appears in: {ids}")

        if report["duplicate_command_keys"]:
            count = len(report["duplicate_command_keys"])
            print(f"  [strict] {count} duplicate command_key(s)")
            if verbose:
                for key, ids in report["duplicate_command_keys"].items():
                    print(f"    \"{key}\" appears in: {ids}")

        if not any((
            report["inactive_ids"],
            report["missing_button_label"],
            report["missing_command_key"],
            report["empty_message_ids"],
            report["missing_channel_key"],
            report["duplicate_button_labels"],
            report["duplicate_command_keys"],
        )):
            print("  [strict] no issues found")

        print("[content-registry] strict: scan complete")

    def get_command_for_button(self, button_text: str) -> str | None:
        return self.button_to_command.get(button_text)

    def get_content_for_command(self, command_key: str) -> ContentTarget | None:
        raw_message_ids = self.command_to_values.get(command_key)
        if not raw_message_ids:
            return None

        message_ids = (
            raw_message_ids if isinstance(raw_message_ids, list) else [raw_message_ids]
        )
        if not all(isinstance(message_id, int) for message_id in message_ids):
            return None

        channel_id = self.get_channel_for_command(command_key)
        if channel_id is None:
            return None

        return ContentTarget(
            command_key=command_key,
            channel_id=channel_id,
            message_ids=message_ids,
        )

    def get_channel_for_command(self, command_key: str) -> int | None:
        channel_key = self.command_to_channel_key.get(command_key)
        if channel_key:
            return {
                "CS_STG4_CHANNEL_ID": CS_STG4_CHANNEL_ID,
                "CS_STG4_ONEFILE_CHANNEL_ID": CS_STG4_ONEFILE_CHANNEL_ID,
                "CS_STG4_DELETED_CHANNEL_ID": CS_STG4_DELETED_CHANNEL_ID,
                "CS_APPS_CHANNEL_ID": CS_APPS_CHANNEL_ID,
            }.get(channel_key)

        # TODO: Replace suffix-based routing with explicit channel metadata.
        if "_full" in command_key:
            return CS_STG4_CHANNEL_ID
        if "_lectures" in command_key:
            return CS_STG4_ONEFILE_CHANNEL_ID
        if "_old" in command_key:
            return CS_STG4_DELETED_CHANNEL_ID
        if "_app" in command_key:
            return CS_APPS_CHANNEL_ID
        return None
