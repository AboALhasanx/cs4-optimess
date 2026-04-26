"""
Legacy migration utility — NOT part of normal bot runtime.

This script was used to migrate content from the legacy two-file system
(data/terms_btn2cmd.json + data/terms_cmd2values.json) into the unified
data/content_items.json catalog.

The bot runtime now reads content_items.json directly. The legacy JSON
files are kept on disk for reference but are not loaded at runtime.

Do not run this script unless you intentionally need to regenerate the
catalog from the legacy files.
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app_paths import DATA_DIR

BUTTONS_PATH = DATA_DIR / "terms_btn2cmd.json"
VALUES_PATH = DATA_DIR / "terms_cmd2values.json"


def channel_key_for_command(command_key: str) -> str | None:
    if "_full" in command_key:
        return "CS_STG4_CHANNEL_ID"
    if "_lectures" in command_key:
        return "CS_STG4_ONEFILE_CHANNEL_ID"
    if "_old" in command_key:
        return "CS_STG4_DELETED_CHANNEL_ID"
    if "_app" in command_key:
        return "CS_APPS_CHANNEL_ID"
    return None


def normalize_message_ids(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def main() -> None:
    button_to_command = json.loads(BUTTONS_PATH.read_text(encoding="utf-8"))
    values = json.loads(VALUES_PATH.read_text(encoding="utf-8")).get("commands", {})
    content_items = []

    for index, (button_label, command_key) in enumerate(button_to_command.items()):
        content_items.append(
            {
                "id": command_key or f"unmapped_{index}",
                "button_label": button_label,
                "command_key": command_key,
                "channel_key": channel_key_for_command(command_key),
                "message_ids": normalize_message_ids(values.get(command_key)),
                "active": True,
            }
        )

    output_path = DATA_DIR / "content_items.json"
    output_path.write_text(
        json.dumps(content_items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(content_items)} content items to {output_path}")


if __name__ == "__main__":
    main()
