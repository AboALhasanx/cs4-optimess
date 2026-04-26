# Project Simplification Review

## 1. Current Architecture Summary

The project is currently a partially refactored Telegram bot built with `pyTelegramBotAPI/telebot`. The core bot behavior is still the same: users navigate reply-keyboard menus, choose a course/resource button, and the bot forwards one or more Telegram channel messages to the user.

Current flow:

1. `main.py` creates the global `TeleBot` instance and registers all handlers.
2. `config.py` loads runtime configuration from environment variables.
3. `app_paths.py` resolves data files from `data/`, `BOT_DATA_DIR`, or the legacy Android path.
4. `services/content_registry.py` loads content definitions.
5. `services/content_sender.py` forwards content from Telegram channels.
6. `services/message_logger.py` preserves user message logging/forwarding to `LOG_CHANNEL_ID`.
7. `services/users_service.py` handles Firebase user logging and broadcast user loading.
8. `term1_keyboard.py` and `term2_keyboard.py` build reply-keyboard menus.
9. `data/content_items.json` is now the preferred catalog.
10. `data/terms_btn2cmd.json` and `data/terms_cmd2values.json` remain as legacy fallback inputs.

Current content mapping behavior:

- If `data/content_items.json` exists, `ContentRegistry` loads it.
- If `content_items.json` does not exist, the registry falls back to the two legacy JSON files.
- `main.py` still keeps a `button_to_command` variable for handler matching.
- `main.py` delegates forwarding to `send_content_for_command()`.

Important measured state:

| Item | Current Count |
| --- | ---: |
| `content_items.json` entries | 131 |
| Active content items | 110 |
| Items with missing `message_ids` | 21 |
| Items with missing `channel_key` | 1 |
| Duplicate `command_key` values | 0 |
| Duplicate `button_label` values | 0 |
| Active registry buttons reported by validator | 110 |
| Active registry commands reported by validator | 110 |

The current architecture is much cleaner than the old all-in-`main.py` design, but it is still carrying transitional duplication.

## 2. Main Problems

### Critical

| Problem | Evidence | Impact | Recommendation |
| --- | --- | --- | --- |
| Two content systems still coexist. | `data/content_items.json`, `data/terms_btn2cmd.json`, `data/terms_cmd2values.json` | Maintainers can edit the wrong file and wonder why behavior differs. | Declare `content_items.json` as the source of truth, then keep legacy files only as migration input. |
| `content_items.json` contains inactive or incomplete migrated entries. | 131 total entries, 110 active loaded entries, 21 missing message IDs. | The active registry validates cleanly, but the file itself still contains confusing dead/incomplete rows. | Split active usable catalog from archived incomplete records, or mark/organize incomplete records clearly. |
| `main.py` still has many near-identical menu handlers. | Many handlers call `log_and_forward()`, define `respond()`, then call `check_and_respond()`. | High maintenance cost for adding/removing course menus. | Replace repeated subject handlers with small registration helpers or a dictionary-driven dispatch layer. |

### Important

| Problem | Evidence | Impact | Recommendation |
| --- | --- | --- | --- |
| `check_and_respond()` is now a pass-through wrapper. | `main.py` defines it as `response_function(message, *args)`. | It preserves old call shape but adds noise across dozens of handlers. | Keep briefly for safety, then remove once menu handlers are simplified. |
| `button_to_command` is loaded as a module-level snapshot. | `button_to_command = content_registry.button_to_command`. | If registry reload is ever added, handler matching will still use old keys. | Either avoid reload entirely or make the handler query `content_registry` directly in its lambda. |
| `ContentRegistry` validates active loaded maps only. | Validator reports clean because inactive/incomplete rows are skipped. | Incomplete rows inside `content_items.json` are easy to forget. | Add a second validation mode for all catalog entries, including inactive/incomplete items. |
| Channel routing still has fallback suffix logic. | `get_channel_for_command()` supports `channel_key`, then suffixes. | Transitional complexity; command names still imply routing. | Once all active `content_items` have `channel_key`, remove suffix fallback. |
| Quiz legacy exists as disabled files. | `legacy/disabled_quizzes/` and related `.pyc` artifacts. | Low runtime risk, but adds project noise. | Keep source temporarily; delete cache artifacts now; delete legacy source only after a release cycle. |
| Keyboard files still manually repeat `ReplyKeyboardMarkup` patterns. | `term1_keyboard.py`, `term2_keyboard.py`, partial `keyboard_utils.py`. | Adding buttons requires code edits and repeated loops. | Use `build_keyboard()` consistently, but do not move menus to JSON until content catalog is stable. |
| `main.py` still owns broadcast logic. | `/bro` handler loops through users directly. | Not terrible, but it keeps admin workflow mixed with user navigation. | Later extract to `services/broadcast_service.py` if broadcast grows. |

### Minor

| Problem | Impact | Recommendation |
| --- | --- | --- |
| Root contains old audit reports. | Useful but noisy. | Move to `docs/audit/` later. |
| Root still contains legacy JSON duplicates. | Confusing after `data/` exists. | Keep until final fallback removal, then delete or archive. |
| `users.json` appears unused by current runtime. | Data ownership confusion. | Keep until Firebase/local user storage decision is confirmed. |
| Generated `__pycache__` files exist locally. | Worktree clutter. | Delete locally and keep ignored. |

## 3. Simplification Opportunities

### Content Registry

Current registry is the right direction. The next simplification should not be another redesign; it should be reducing transitional paths.

Recommended changes:

- Keep `ContentRegistry`.
- Keep `ContentTarget`.
- Keep `get_command_for_button()`.
- Keep `get_content_for_command()`.
- Add a validator that checks every `content_items.json` row, not only active loaded rows.
- Remove legacy two-file fallback only after `content_items.json` is verified as complete.

Avoid:

- Rewriting content into a database right now.
- Changing button labels while they are still user-facing keys.
- Removing legacy JSON before the unified catalog is proven.

### Commands

Current command keys are still useful as stable internal IDs. They should stay for now.

Problems:

- Some command keys are inherited from suffix conventions.
- Empty/incomplete command rows still exist in migrated catalog.
- Suffix fallback means command names still affect channel routing.

Recommended path:

1. Require every active item to have `channel_key`.
2. Require every active item to have non-empty integer `message_ids`.
3. Treat `command_key` as an ID only, not routing logic.
4. Remove suffix routing after active catalog is complete.

### Buttons

Button labels are still the visible UI and the primary text trigger.

Practical simplification:

- Keep text matching for now.
- Do not introduce callback buttons unless you want a larger UX change.
- Use `content_items.json` to ensure each button label has one canonical command.
- Add validation for duplicate or blank labels.

### IDs

There are several ID categories:

- Telegram channel IDs in config.
- Telegram message IDs in content mappings.
- Command keys in content mappings.
- User IDs for Firebase and admin checks.

Main issue:

- Message IDs and channel IDs are now better organized, but `term1_table_redirect()` and `term2_table_redirect()` still hardcode message IDs `39` and `40` directly in `main.py`.

Recommended improvement:

- Move table-of-lecture entries into `content_items.json`.
- Then remove direct `bot.forward_message(..., 39/40)` special cases from `main.py`.

### Legacy Files

Legacy state:

- Quiz source appears disabled under `legacy/disabled_quizzes/`.
- Old audit files remain in root.
- Root-level `terms_*.json` duplicate `data/terms_*.json`.

Recommended approach:

- Keep disabled quiz source for one release cycle.
- Delete generated `.pyc` files immediately.
- Move audit docs to `docs/audit/` only if you want a cleaner root.
- Keep root legacy JSON until fallback is removed.

### JSON/Data Structure

Current preferred structure is good:

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

Recommended additions:

- `notes` for incomplete items.
- `category` for resource type such as `full`, `lectures`, `old`, `app`.
- Optional `sort_order` if menu generation eventually moves to data.

Do not add these until the current catalog is cleaned. More schema fields too early can make the file harder to maintain.

### Validation Scripts

Current `scripts/validate_content_maps.py` only reports active registry state. Because inactive/incomplete rows are skipped, it can say “validation passed” while `content_items.json` still contains 21 incomplete rows.

Recommended validator modes:

- Default: validate active runtime behavior.
- Strict: validate every catalog item and report inactive/incomplete records.

Suggested command shape:

```powershell
python scripts\validate_content_maps.py
python scripts\validate_content_maps.py --strict
```

## 4. Files to Keep

| File | Keep Reason |
| --- | --- |
| `main.py` | Active entrypoint and handler registration. Keep while simplifying handlers gradually. |
| `config.py` | Environment-based config is necessary. Avoid touching secrets. |
| `app_paths.py` | Correctly centralizes dynamic data path lookup. |
| `global_vars.py` | Stores current UI labels and long text; changing it risks button drift. |
| `term1_keyboard.py` | Active term 1 keyboard source. |
| `term2_keyboard.py` | Active term 2 keyboard source. |
| `keyboard_utils.py` | Useful helper for reducing keyboard duplication. |
| `services/content_registry.py` | Core simplification point for content lookup. |
| `services/content_sender.py` | Keeps forwarding logic outside `main.py`. |
| `services/message_logger.py` | Preserves logging behavior while isolating it. |
| `services/users_service.py` | Keeps Firebase/user logic outside `main.py`. |
| `data/content_items.json` | Preferred content catalog; should become source of truth. |
| `data/terms_btn2cmd.json` | Keep as legacy fallback until catalog is proven. |
| `data/terms_cmd2values.json` | Keep as legacy fallback until catalog is proven. |
| `scripts/validate_content_maps.py` | Keep and improve; useful safety net. |
| `scripts/migrate_content_items.py` | Keep until migration is final and repeatable. |
| `requirements.txt` | Needed for reproducible setup. |
| `.env.example` | Needed for safe setup without secrets. |
| `.gitignore` | Needed to keep `.env`, logs, and caches out of git. |
| `README.md` | Keep as setup guide. |
| `README_REFACTOR_NOTES.md` | Keep temporarily as refactor history. |

## 5. Files to Remove or Merge

| File/Path | Recommendation | Reason | Risk |
| --- | --- | --- | --- |
| `__pycache__/` directories | Delete locally; keep ignored. | Generated Python bytecode. | Low. |
| `logs/*.log` | Do not track; keep runtime-only. | Runtime artifact. | Low. |
| `legacy/disabled_quizzes/` | Keep source temporarily, remove after one stable release. | Confirms quiz removal is safe. | Medium if deleted too soon. |
| Root `terms_btn2cmd.json` | Remove after fallback is removed. | Duplicate of `data/terms_btn2cmd.json`. | Medium if someone still edits root copy. |
| Root `terms_cmd2values.json` | Remove after fallback is removed. | Duplicate of `data/terms_cmd2values.json`. | Medium. |
| `README_REFACTOR_NOTES.md` | Merge into `README.md` or `docs/refactor-notes.md` later. | Root noise. | Low. |
| `SECURITY_AUDIT.md`, `ARCHITECTURE_REPORT.md`, `TECHNICAL_DEBT.md`, `REFACTORING_ROADMAP.md` | Move to `docs/audit/` later. | Keeps root focused. | Low. |
| `check_and_respond()` in `main.py` | Remove after handlers are simplified. | It is now a no-op wrapper. | Low, but many call sites. |
| `get_file_command()` in `main.py` | Inline or rename after `content_sender` is trusted. | It only delegates now. | Low. |
| Direct table handlers in `main.py` | Merge into content catalog. | Hardcoded message IDs should live in data. | Low/Medium; verify IDs first. |

## 6. Recommended Final Architecture

Recommended final architecture should stay close to the current branch, not a full rewrite.

```text
cs4/
  main.py
  config.py
  app_paths.py
  global_vars.py
  keyboard_utils.py
  term1_keyboard.py
  term2_keyboard.py
  services/
    content_registry.py
    content_sender.py
    message_logger.py
    users_service.py
  data/
    content_items.json
  scripts/
    validate_content_maps.py
  legacy/
    disabled_quizzes/
  docs/
    audit/
```

Simpler responsibility split:

- `main.py`: bot creation and handler wiring only.
- `config.py`: environment variables only.
- `app_paths.py`: data path discovery only.
- `content_registry.py`: catalog loading, validation, lookup.
- `content_sender.py`: Telegram forwarding behavior.
- `message_logger.py`: user message log forwarding.
- `users_service.py`: Firebase user registration, user loading, deactivation.
- `term*_keyboard.py`: menu layout only.
- `data/content_items.json`: one source of truth for content button-to-message mapping.

Key final simplifications:

- `content_items.json` becomes the only active content map.
- Legacy two-file JSON is archived or removed.
- Active catalog entries must all have `channel_key` and integer `message_ids`.
- Suffix-based channel fallback is removed.
- No-op `check_and_respond()` is removed.
- Hardcoded table message IDs move into catalog.

## 7. Step-by-Step Refactor Plan

### Step 1: Confirm Current Branch and Baseline

Goal: make sure work continues from `refactor-clean-bot`.

Expected result:

- Git branch is `refactor-clean-bot`.
- Python files compile.
- Current validator passes.

Risk: low.

### Step 2: Clean Generated Files Only

Goal: remove `__pycache__` and log noise from the working tree.

Do not remove source files.

Risk: low.

### Step 3: Add Strict Catalog Validation

Goal: make incomplete `content_items.json` rows visible.

Keep current validator behavior as default. Add strict mode later.

Risk: low.

### Step 4: Clean `content_items.json`

Goal: separate usable active content from incomplete migrated records.

Safe options:

- Keep incomplete records but add `"active": false` and `"notes"`.
- Or move incomplete records to `data/content_items_incomplete.json`.

Do not delete incomplete rows until you confirm they are truly unused.

Risk: medium.

### Step 5: Move Table-of-Lecture Items Into Catalog

Goal: remove hardcoded `39` and `40` forwarding from `main.py`.

Add catalog entries for:

- `term1_Table_of_lectures`
- `term2_Table_of_lectures`

Then route them through `content_sender`.

Risk: low/medium because it touches existing user-visible menu buttons.

### Step 6: Remove No-Op Subscription Wrapper

Goal: remove `check_and_respond()` after handlers are stable.

Safe approach:

- First replace calls one section at a time.
- Compile after each section.

Risk: low, but repetitive.

### Step 7: Simplify Menu Handler Registration

Goal: reduce repeated handler bodies.

Introduce a tiny helper, not a framework rewrite:

```python
def reply_with_markup(message, markup_factory):
    log_and_forward(message)
    chose_from_markup(message, markup_factory())
```

Then apply gradually.

Risk: medium due many handlers.

### Step 8: Finish Keyboard Helper Adoption

Goal: use `build_keyboard()` consistently.

Do not change button text.

Risk: low.

### Step 9: Remove Legacy JSON Fallback

Prerequisites:

- `content_items.json` strict validation is clean.
- All active content comes from catalog.
- Root legacy JSON is no longer edited by anyone.

Then:

- Remove fallback from `ContentRegistry`.
- Archive or delete legacy JSON.
- Keep migration script in `scripts/` for history or remove after one release.

Risk: medium.

### Step 10: Remove Disabled Quiz Source

Prerequisites:

- No active references.
- At least one stable release without quiz files.

Then delete:

- `legacy/disabled_quizzes/`

Risk: low after waiting period.

## 8. Tests / Validation Commands

Run after every step:

```powershell
python -m py_compile main.py config.py app_paths.py global_vars.py term1_keyboard.py term2_keyboard.py keyboard_utils.py
```

Run after service changes:

```powershell
python -m py_compile services\content_registry.py services\content_sender.py services\message_logger.py services\users_service.py
```

Run content validation:

```powershell
python scripts\validate_content_maps.py
```

Run full Python compile:

```powershell
$files = Get-ChildItem -Recurse -Filter *.py | Where-Object { $_.FullName -notmatch '\\.venv\\|\\venv\\' } | ForEach-Object { $_.FullName }
python -m py_compile $files
```

Check for active quiz references:

```powershell
Select-String -Path *.py,services\*.py,term*.py -Pattern "iot_quiz|mobApp_quiz|des_quiz|poll_answer_handler|callback_query_handler"
```

Check for forced subscription remnants:

```powershell
Select-String -Path main.py -Pattern "get_chat_member|is_user_member|check_and_respond"
```

Check for hardcoded Android path usage:

```powershell
Select-String -Path *.py,services\*.py -Pattern "/storage/emulated/0"
```

Manual smoke test after behavior-affecting steps:

1. `/start` opens the main menu.
2. Term 1 menu opens.
3. Term 2 menu opens.
4. One known Term 1 content button forwards content.
5. One known Term 2 content button forwards content.
6. Rating flow still works.
7. Admin broadcast still works.
8. Message logging to `LOG_CHANNEL_ID` still works.
9. Incomplete/unavailable content returns the expected unavailable response.

