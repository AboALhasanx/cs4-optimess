# CS4 Telegram Bot

Educational Telegram bot for fourth-stage CS students. The bot shows reply-keyboard menus and forwards lectures, files, summaries, programs, and related materials from Telegram channels based on the selected button.

## Setup

1. Create a local environment file:

```bash
cp .env.example .env
```

2. Fill `.env` with your real values. Do not commit `.env`.

```env
BOT_TOKEN=
ADMIN_ID=
LOG_CHANNEL_ID=
CS_STG4_CHANNEL_ID=
CS_STG4_ONEFILE_CHANNEL_ID=
CS_STG4_DELETED_CHANNEL_ID=
CS_APPS_CHANNEL_ID=
FIREBASE_URL=
TELEGRAM_PROXY_URL=
BOT_DATA_DIR=
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the bot:

```bash
python main.py
```

## Data Files

The default data directory is:

```text
data/
```

Important files:

- `data/terms_btn2cmd.json`: maps visible button text to a command key.
- `data/terms_cmd2values.json`: maps command keys to Telegram message IDs.
- `data/content_items.json`: unified catalog generated from the two legacy files.

The bot reads `content_items.json` if it exists. If it is missing, it falls back to the legacy two-file mapping.

## Adding New Content

Legacy method:

1. Add the button label to `data/terms_btn2cmd.json`.
2. Map that label to a `command_key`.
3. Add the same `command_key` to `data/terms_cmd2values.json`.
4. Set the value to a Telegram message ID or list of message IDs.
5. Run:

```bash
python scripts/migrate_content_items.py
python scripts/validate_content_maps.py
```

Preferred method:

Edit `data/content_items.json` and add:

```json
{
  "id": "example_full",
  "button_label": "Visible button text",
  "command_key": "example_full",
  "channel_key": "CS_STG4_CHANNEL_ID",
  "message_ids": [123],
  "active": true
}
```

Supported `channel_key` values:

- `CS_STG4_CHANNEL_ID`
- `CS_STG4_ONEFILE_CHANNEL_ID`
- `CS_STG4_DELETED_CHANNEL_ID`
- `CS_APPS_CHANNEL_ID`

## Data Path Resolution

The bot searches for data files in this order:

1. `data/` inside the project.
2. `BOT_DATA_DIR` from `.env`, if configured.
3. Legacy Android path `/storage/emulated/0/csbot/cs4`, only if it exists.

The Android path is no longer the default.

## Validation

Run:

```bash
python scripts/validate_content_maps.py
```

Warnings are allowed for old incomplete mappings, but missing core data files are errors.

## Removed Features

The interactive quiz/test system was removed from the active bot. Old quiz modules are preserved in:

```text
legacy/disabled_quizzes/
```

Forced channel subscription checks were also removed. Users can open `/start`, use menus, and request content without being blocked by membership checks.

## Message Logging

User message forwarding/logging to `LOG_CHANNEL_ID` is still active. The logic now lives in:

```text
services/message_logger.py
```
