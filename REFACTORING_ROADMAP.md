# Refactoring Roadmap

## Executive Summary

Do not begin by rewriting random functions. The project needs a controlled migration from a script-style bot into a small production-grade service.

The correct strategy is:

1. Stabilize secrets, dependencies, and deployment.
2. Extract data models from hardcoded strings and JSON.
3. Introduce tests around current behavior.
4. Migrate handlers to an async framework.
5. Replace Telegram-message-ID spreadsheets with a database-backed content catalog.

## Phase 0: Freeze and Preserve Current Behavior

Goal: make the legacy behavior reproducible before changing it.

Tasks:

- Rotate Telegram token.
- Add `.env.example`.
- Create a dependency manifest.
- Pin current working library versions.
- Add a `README.md` with startup instructions.
- Add a smoke test that imports all modules.
- Save current JSON mappings as migration input.
- Document required Telegram channels and bot permissions.

Deliverables:

```text
pyproject.toml
uv.lock or requirements.txt
.env.example
README.md
tests/test_imports.py
```

## Phase 1: Configuration and Runtime Hygiene

Move all environment-specific values out of source code:

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
```

Replace Android-only paths with project-relative paths during the transition:

```python
BASE_DIR = Path(__file__).resolve().parent
COMMANDS_PATH = BASE_DIR / "terms_btn2cmd.json"
VALUES_PATH = BASE_DIR / "terms_cmd2values.json"
```

This is a stabilization step, not the final architecture.

## Phase 2: Introduce Domain Models

Replace magic command suffixes with explicit fields.

Current anti-pattern:

```python
if "_full" in command:
    CHANNEL_ID = cs_stg4
elif "_lectures" in command:
    CHANNEL_ID = cs_stg4_onefile
```

Target concept:

```text
ContentItem
    id
    title
    course_id
    category
    source_channel_id
    telegram_message_ids
    requires_subscription
    is_active
```

Routing should use IDs and metadata, not button labels and substring checks.

## Phase 3: Database Design

Either PostgreSQL or SQLite is suitable at first. PostgreSQL is preferred if the bot will be hosted professionally. SQLite is acceptable for a small single-instance deployment.

### Relational Schema

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    first_name TEXT,
    username TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_banned BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    term INTEGER NOT NULL,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE content_categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL
);

CREATE TABLE source_channels (
    id SERIAL PRIMARY KEY,
    telegram_chat_id BIGINT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    purpose TEXT
);

CREATE TABLE content_items (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id),
    category_id INTEGER REFERENCES content_categories(id),
    source_channel_id INTEGER REFERENCES source_channels(id),
    button_label TEXT NOT NULL,
    command_key TEXT UNIQUE,
    requires_subscription BOOLEAN NOT NULL DEFAULT TRUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    display_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE content_messages (
    id SERIAL PRIMARY KEY,
    content_item_id INTEGER REFERENCES content_items(id) ON DELETE CASCADE,
    telegram_message_id INTEGER NOT NULL,
    position INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE quiz_sets (
    id SERIAL PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    source_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE quiz_questions (
    id SERIAL PRIMARY KEY,
    quiz_set_id INTEGER REFERENCES quiz_sets(id),
    question TEXT NOT NULL,
    options JSONB NOT NULL,
    correct_option_id INTEGER NOT NULL
);

CREATE TABLE quiz_sessions (
    id UUID PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    quiz_set_id INTEGER REFERENCES quiz_sets(id),
    current_index INTEGER NOT NULL DEFAULT 0,
    score INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### NoSQL Alternative

If Firebase remains preferred, use collections like:

```text
users/{telegram_user_id}
courses/{course_id}
content_items/{item_id}
content_items/{item_id}/messages/{message_id}
quiz_sets/{quiz_id}
quiz_sets/{quiz_id}/questions/{question_id}
quiz_sessions/{session_id}
```

Firebase is acceptable for low-ops deployment, but it must have strict rules, authentication, and backups.

## Phase 4: Async Framework Migration

Recommended options:

| Framework | Recommendation | Why |
| --- | --- | --- |
| Aiogram 3.x | Best fit for async-first Telegram bot architecture | Strong routers, middleware, FSM, async design. |
| python-telegram-bot 20+ / 22+ | Also strong | Mature, async-native, healthy ecosystem. |
| pyTelegramBotAPI AsyncTeleBot | Transitional option | Lower migration cost, but less architectural improvement. |

Preferred target: **Aiogram 3.x** if the goal is a clean redesign.

### Migration Steps

1. Create a new async app shell beside legacy code.
2. Implement config loading with Pydantic Settings or equivalent.
3. Add middleware for logging, authorization, and rate limits.
4. Port `/start`, `/about`, and `/rate`.
5. Port course menu rendering from database-backed definitions.
6. Port content forwarding with explicit `content_item_id`.
7. Port quiz engine using persistent sessions.
8. Port admin broadcast as background jobs.
9. Run legacy and new bot in staging with a separate token.
10. Cut over only after behavior is validated.

## Phase 5: Performance Optimization

### Replace Synchronous Network Calls

Use async HTTP clients:

```text
requests -> httpx.AsyncClient or aiohttp
```

Add:

- Timeouts.
- Retries with backoff.
- Circuit breakers for external quiz source.
- Cache for membership checks and quiz files.

### Background Jobs

Broadcast should not run inside an update handler. Use:

- APScheduler for simple jobs.
- Celery/RQ if using Redis.
- Database-backed job table for minimal infrastructure.

### Rate Limiting

Add per-user and global rate limits:

- Content request cooldown.
- Broadcast throttle.
- Quiz callback debounce.
- Admin command confirmation.

## Phase 6: CI/CD and DevOps

### Proposed Repository Layout

```text
app/
    main.py
    config.py
    handlers/
    middlewares/
    services/
    repositories/
    models/
tests/
migrations/
scripts/
Dockerfile
docker-compose.yml
pyproject.toml
.env.example
.github/workflows/ci.yml
```

### Dockerfile

Target deployment should use Docker with environment variables:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev
COPY app ./app
CMD ["uv", "run", "python", "-m", "app.main"]
```

### Docker Compose

```yaml
services:
  bot:
    build: .
    env_file: .env
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: csbot
      POSTGRES_USER: csbot
      POSTGRES_PASSWORD: change-me

  redis:
    image: redis:7
```

### CI Pipeline

CI should run:

```text
ruff check .
ruff format --check .
pytest
pip-audit
detect-secrets scan
```

### Deployment Checklist

- Secrets stored in host/CI secret manager.
- Token rotation procedure documented.
- Logs exclude message text unless explicitly needed.
- Database backups enabled.
- Healthcheck endpoint or heartbeat configured.
- Bot restart policy configured.
- Admin broadcast protected by confirmation flow.

## Final Modernization Target

The finished system should be:

- Async.
- Config-driven.
- Database-backed.
- Test-covered.
- Token-safe.
- Dockerized.
- Observable.
- Permission-consistent.
- Independent of Android paths.
- Free from manually duplicated quiz engines.

This is not overengineering. This is the minimum professional structure needed for a bot that handles real users, private messages, and protected educational content.
