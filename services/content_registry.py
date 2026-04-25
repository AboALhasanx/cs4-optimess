import json
from dataclasses import dataclass
from pathlib import Path

from app_paths import BUTTONS_PATH, DATA_DIR, VALUES_PATH
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
        buttons_path: Path = BUTTONS_PATH,
        values_path: Path = VALUES_PATH,
        content_items_path: Path = DATA_DIR / "content_items.json",
    ) -> None:
        self.buttons_path = buttons_path
        self.values_path = values_path
        self.content_items_path = content_items_path
        self.content_items = []
        self.command_to_channel_key = {}
        if content_items_path.exists():
            self._load_content_items(content_items_path)
        else:
            self.button_to_command = self._load_json(buttons_path)
            values_data = self._load_json(values_path)
            self.command_to_values = values_data.get("commands", {})
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
