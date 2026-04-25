# Refactor Notes

## Current Project Files

Core bot files:

- `main.py`: Main Telegram bot entrypoint, handlers, forwarding, logging, Firebase user tracking, broadcast command, forced subscription checks, and quiz wiring.
- `config.py`: Bot token, admin ID, channel IDs, and log channel ID.
- `global_vars.py`: Shared Arabic UI labels and long text messages.
- `term1_keyboard.py`: Term 1 reply keyboard builders.
- `term2_keyboard.py`: Term 2 reply keyboard builders.

Content mapping files:

- `terms_btn2cmd.json`: Maps visible button labels to internal command keys.
- `terms_cmd2values.json`: Maps command keys to Telegram source message IDs.

Quiz files to remove or isolate later:

- `iot_quiz.py`
- `mobApp_quiz.py`
- `des_quiz.py`

User/log files:

- `users.json`: Local user data sample/cache.
- `logs/system_monitor.log`: Historical system monitoring log.

Audit/report files:

- `SECURITY_AUDIT.md`
- `ARCHITECTURE_REPORT.md`
- `TECHNICAL_DEBT.md`
- `REFACTORING_ROADMAP.md`

## What Will Be Preserved

- The core educational bot behavior.
- Reply keyboard navigation for term 1 and term 2.
- Forwarding educational content from Telegram channels by mapped buttons.
- Admin broadcast behavior.
- User logging/Firebase user tracking unless a later cleanup safely isolates it.
- Message forwarding/logging to the configured log channel.
- Existing content JSON mappings, initially preserved for compatibility.

## What Will Be Removed Or Isolated

- Quiz/test features and related handlers.
- Quiz modules and raw GitHub quiz loading.
- Forced channel subscription checks.
- Hardcoded Android-only data paths as the default behavior.
- Hardcoded secrets from source-controlled configuration.

## Refactor Strategy

The project will be cleaned gradually. Each successful phase should compile, be committed, and be pushed before moving to the next phase. The intent is not to rewrite the bot idea, but to make the existing idea easier to run, safer to configure, and simpler to maintain.
