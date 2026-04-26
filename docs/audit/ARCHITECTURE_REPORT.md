# Architecture Report

## Executive Summary

The project is a flat, synchronous Telegram bot built around one large `main.py` file and several helper modules for button generation and quiz behavior. It works as a hand-built script, not as a maintainable application architecture.

The strongest architectural smell is that routing, authorization, logging, business rules, data access, UI labels, and deployment configuration are all mixed together. The bot's behavior depends on exact Arabic/emoji button text, absolute Android filesystem paths, remote GitHub JSON, Firebase, Telegram channels, and a locally running SOCKS proxy.

## Project Structure

| File/Directory | Purpose | Notes |
| --- | --- | --- |
| `main.py` | Main bot runtime, handlers, forwarding, logging, Firebase, permissions | 837 lines; 84 functions; about 50 handler markers. |
| `config.py` | Bot token, admin ID, channel IDs | Contains hardcoded secrets/config. |
| `global_vars.py` | Static UI text and course labels | Large Arabic text constants; encoding appears mojibake in terminal output. |
| `term1_keyboard.py` | Reply keyboard builders for term 1 | Repeated button construction. |
| `term2_keyboard.py` | Reply keyboard builders for term 2, ratings, quiz menus | Repeated button construction. |
| `terms_btn2cmd.json` | Maps button text to internal command keys | 131 entries. |
| `terms_cmd2values.json` | Maps internal commands to Telegram message IDs | 122 command entries. |
| `mobApp_quiz.py` | Mobile app quiz logic | Duplicates IoT/DES structure. |
| `iot_quiz.py` | IoT quiz logic | Duplicates mobile/DES structure. |
| `des_quiz.py` | DES quiz logic | Present but not fully wired like the other quiz modules. |
| `users.json` | Local user sample/cache | Not the primary runtime store; Firebase is used. |
| `logs/system_monitor.log` | Historical performance log | Not integrated into visible runtime code. |

## System Flow

```text
Telegram Update
    |
    v
telebot polling in main.py
    |
    +--> command/menu handlers
    |       |
    |       +--> log_and_forward()
    |       +--> check_and_respond()
    |       +--> keyboard builders in term1_keyboard.py / term2_keyboard.py
    |
    +--> button text handler
    |       |
    |       +--> terms_btn2cmd.json: button label -> command
    |       +--> terms_cmd2values.json: command -> post ID(s)
    |       +--> Telegram forward_message() from source channel
    |
    +--> quiz handlers
    |       |
    |       +--> GitHub raw JSON
    |       +--> in-memory user_data dict
    |       +--> Telegram poll/callback handlers
    |
    +--> fallback log handler
            |
            +--> LOG_CHANNEL_ID
```

## Core Data Layers

### Configuration Layer

`config.py` directly stores:

- Telegram bot token.
- Admin user ID.
- Source channel IDs.
- Log channel ID.

This is not environment-aware. There is no development/staging/production separation.

### Static Text Layer

`global_vars.py` stores UI labels and long text. These strings are imported by both `main.py` and keyboard modules. The architecture tightly couples business logic to exact display strings.

### Keyboard Layer

`term1_keyboard.py` and `term2_keyboard.py` manually create `ReplyKeyboardMarkup` objects. Each course has a separate function with a local list of button labels.

This is structurally simple but scales poorly. A new course or category requires code edits instead of data changes.

### JSON Mapping Layer

`terms_btn2cmd.json` maps human-visible button text to internal command names.

`terms_cmd2values.json` maps internal command names to Telegram channel post IDs.

Measured state:

| Metric | Count |
| --- | ---: |
| Button-to-command mappings | 131 |
| Command-to-post mappings | 122 |
| Commands referenced by buttons but missing values | 11 |
| Commands present but unreachable from buttons | 2 |
| Commands with list values | 44 |
| Commands with scalar values | 78 |

This drift is expected in manually maintained JSON maps. The system lacks referential integrity.

## Environment Lock-In

`main.py` uses absolute Android paths:

```python
file_path = "/storage/emulated/0/csbot/cs4/terms_cmd2values.json"
commands_file_path = "/storage/emulated/0/csbot/cs4/terms_btn2cmd.json"
```

This breaks portability. On Windows, Linux servers, Docker, CI, or most VPS environments, these files do not exist. The local project contains the JSON files, but the runtime ignores them.

Impact:

- `button_to_command = load_commands(commands_file_path)` becomes `{}`.
- The generic button handler will not match mapped content buttons.
- Most content-forwarding behavior silently disappears.

This is not a small bug. It is deployment lock-in to the original Android filesystem layout.

## Dependency Review

The project imports:

```python
import telebot
import random
import json
import requests
from telebot import apihelper
```

But there is no:

- `requirements.txt`
- `pyproject.toml`
- `Pipfile`
- `poetry.lock`
- `uv.lock`
- `environment.yml`

The deployed environment cannot be recreated reliably. A professional deployment must explicitly pin `pyTelegramBotAPI`, `requests`, and any proxy extras such as `PySocks`.

## External System Dependencies

| Dependency | Purpose | Risk |
| --- | --- | --- |
| Telegram Bot API | Bot messaging, polling, forwarding | Central runtime dependency. |
| Telegram source channels | Content storage via message IDs | Content is coupled to mutable/deletable Telegram posts. |
| Firebase Realtime Database | User storage and broadcast list | No visible auth/rules in code. |
| GitHub raw URLs | Quiz question source | Runtime behavior controlled by remote JSON. |
| Local SOCKS proxy | Telegram API proxy | Hardcoded `127.0.0.1:9050`; hidden operational requirement. |

## Architectural Assessment

### Strengths

- Simple mental model.
- Easy for one developer to add buttons manually.
- Uses Telegram forwarding instead of hosting files directly.
- Separates some static keyboard code into modules.

### Weaknesses

- `main.py` is a god file.
- Authorization is manually applied and inconsistent.
- Text labels are used as routing keys.
- Runtime data lives partly in local JSON, partly in Firebase, partly in Telegram channels, partly in GitHub.
- No dependency management.
- No testability boundary.
- No repository metadata or deployment contract.

## Recommended Target Architecture

```text
app/
    bot/
        handlers/
            start.py
            courses.py
            content.py
            quizzes.py
            admin.py
        middlewares/
            auth.py
            logging.py
            rate_limit.py
        services/
            content_service.py
            user_service.py
            quiz_service.py
            telegram_forwarder.py
        repositories/
            users.py
            courses.py
            content_items.py
            quiz_sessions.py
        config.py
        main.py
tests/
pyproject.toml
Dockerfile
docker-compose.yml
.env.example
```

The key architectural shift should be from button-text-driven spaghetti to explicit domain objects: courses, resources, users, sessions, channels, and permissions.
