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

- `data/content_items.json`: **source of truth** for content buttons, their command keys, target channel, and forwarded message IDs.
- `data/terms_btn2cmd.json` and `data/terms_cmd2values.json`: legacy migration inputs only — not loaded at runtime.
- `scripts/migrate_content_items.py`: legacy regeneration tool, not part of runtime.

The bot reads `content_items.json` exclusively. If it is missing, the bot will fail with a clear error. The legacy two-file fallback has been removed.

## Adding New Content

Edit `data/content_items.json` and add an entry:

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

Required fields:
- `button_label`: the exact text shown on the reply keyboard button.
- `command_key`: stable internal identifier for the content.
- `channel_key`: which channel the message IDs belong to.
- `message_ids`: one or more Telegram message IDs to forward.

Optional fields:
- `active`: set to `false` to keep the entry in the catalog but hide it from runtime.
- `notes`: document why an entry is inactive or incomplete.

Supported `channel_key` values:

- `CS_STG4_CHANNEL_ID`
- `CS_STG4_ONEFILE_CHANNEL_ID`
- `CS_STG4_DELETED_CHANNEL_ID`
- `CS_APPS_CHANNEL_ID`

Inactive rows (with `"active": false`) are intentionally preserved in the catalog but are ignored at runtime. Each inactive row should have a `notes` field explaining why it is inactive.

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

This validates the loaded (active) content maps. No warnings means every active button has valid message IDs.

To audit **every row** in the catalog, including inactive ones:

```bash
python scripts/validate_content_maps.py --strict
```

This reports counts of inactive items, missing fields, empty message IDs, and duplicates.

For full item-level detail:

```bash
python scripts\validate_content_maps.py --strict --verbose
```

Inactive rows in `content_items.json` are expected and are documented with `notes` fields.

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
