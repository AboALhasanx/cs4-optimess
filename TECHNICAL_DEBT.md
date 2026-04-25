# Technical Debt Report

## Executive Summary

The project carries heavy technical debt. The code is understandable as a fast personal build, but professionally it is brittle, repetitive, and difficult to verify. The main issue is not that the bot is "bad" in intent; the issue is that the implementation has grown as a pile of handlers and magic strings rather than a system.

Engineering grade: **D+**

It works only because the domain is small and the original maintainer knows the hidden assumptions. That is not maintainability.

## PEP8 and Code Quality Grade

| Category | Grade | Notes |
| --- | --- | --- |
| Naming | C- | Mixed styles, abbreviations, uppercase local variable `CHANNEL_ID`, inconsistent function names. |
| Structure | D | `main.py` is 837 lines and mixes every concern. |
| Imports | C- | Imports appear in the middle of files and inside handlers; unused imports exist in quiz files. |
| Error Handling | D | Broad `except Exception` is common; errors are printed instead of structured logging. |
| Configuration | F | Secrets and environment-specific paths are hardcoded. |
| Testability | F | No tests, no dependency injection, no manifest, no isolated services. |
| Duplication | D | Quiz modules and keyboard builders repeat the same patterns many times. |
| Runtime Safety | D | Blocking network calls, no timeouts, in-memory state, no rate limiting. |

## Logic Redundancy

### Duplicated Quiz Engines

`iot_quiz.py`, `mobApp_quiz.py`, and `des_quiz.py` are near-clones. Each defines:

```python
user_data = {}
def load_*_quiz():
def handle_*_quiz_menu(...):
def send_*_question(...):
def start_*_test(...):
def next_*_handler(...):
def random_*_question(...):
def quit_quiz(...):
def handle_poll_answer(...):
```

This should be one generic quiz service configured by quiz type. The current design guarantees future bugs will be fixed in one quiz module and forgotten in another.

### Duplicate Handler Function Names

`main.py` defines duplicate function names:

| Function Name | Lines |
| --- | --- |
| `on_poll_answer` | `590`, `660` |
| `handle_next_q` | `597`, `667` |

Python allows later function definitions to overwrite earlier names in the module namespace, while the decorators may still retain references. This is confusing and amateurish from a maintainability standpoint. Distinct handler names are cheap; ambiguity here buys nothing.

### Repetitive Keyboard Builders

`term1_keyboard.py` and `term2_keyboard.py` contain many functions that repeat:

```python
markup = ReplyKeyboardMarkup(resize_keyboard=True)
for text in button_texts:
    button = KeyboardButton(text)
    markup.add(button)
return markup
```

This should be a shared helper or data-driven menu renderer.

### Hardcoded Button-to-Command Coupling

The bot uses visible Arabic/emoji button labels as routing keys:

```python
@bot.message_handler(func=lambda msg: msg.text in button_to_command.keys())
def handle_button(message):
    command = button_to_command.get(message.text)
```

This is fragile. A single emoji variation, typo, encoding issue, or label edit can break routing.

Measured mapping drift:

| Mapping Problem | Count |
| --- | ---: |
| Button mappings | 131 |
| Command value mappings | 122 |
| Button commands missing from command-value JSON | 11 |
| Command-value entries unreachable from buttons | 2 |

This is what happens when a database relationship is emulated by hand-edited JSON.

## Logic Bottlenecks

### Re-Reading JSON on Every Content Request

`get_file_command` calls:

```python
data = load_data(file_path)
```

This reloads the JSON mapping for every content request. The file is small, so it is not catastrophic today, but the pattern is wrong. Static mapping should be loaded once and validated at startup, then reloaded intentionally if needed.

### Broadcast Loop Is Naive

The admin broadcast command loops over every user and calls `bot.copy_message` synchronously:

```python
for uid, info in users.items():
    ...
    bot.copy_message(...)
```

There is no batching, backoff, retry policy, Telegram rate-limit handling, job tracking, or progress persistence. At scale this will be slow and failure-prone.

### External HTTP Without Timeouts

Examples:

```python
requests.get(f"{FIREBASE_URL}/users/{user_id}.json")
requests.get(url)
```

No timeout means a network stall can block the bot handler thread.

### Membership Check Performs Live API Calls

`check_and_respond` calls `get_chat_member` for every gated menu request. This is correct in principle but should be cached briefly or middleware-managed if traffic grows.

## Concurrency Issues

### Synchronous TeleBot Runtime

The bot uses:

```python
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
bot.polling()
```

This model is simple but not ideal for high traffic. Every blocking Firebase request, GitHub request, Telegram forward, or broadcast operation competes with update handling.

### In-Memory Quiz State

Quiz state is stored in module-level dictionaries:

```python
user_data = {}
```

Problems:

- State disappears on restart.
- State is not shared across processes.
- No expiration exists.
- Poll answers use `poll_answer.user.id`, while sessions are stored by `message.chat.id`; in private chats those may match, but in group contexts they diverge.
- Multiple simultaneous quizzes can overwrite state.

### Multiple Poll Handlers

Two `@bot.poll_answer_handler()` decorators are registered in `main.py`, one for mobile app and one for IoT. Depending on library behavior, both may process poll answers or the registration order may create confusing behavior. The handler itself has no poll-to-quiz identity mapping.

## Maintainability Problems

### God File

`main.py` has 837 lines and handles:

- Bot setup.
- Proxy setup.
- Firebase.
- Admin broadcast.
- Membership checks.
- Start/about/rating.
- Term 1 navigation.
- Term 2 navigation.
- Quiz routing.
- WebApp buttons.
- Content forwarding.
- Message logging.
- Polling startup.

This violates separation of concerns.

### Magic Suffix Routing

Content channel selection depends on string suffixes:

```python
if "_full" in command:
    CHANNEL_ID = cs_stg4
elif "_lectures" in command:
    CHANNEL_ID = cs_stg4_onefile
elif "_old" in command:
    CHANNEL_ID = cs_stg4_deleted
elif "_app" in command:
    CHANNEL_ID = cs_apps
```

This is brittle because command naming silently controls data source selection. It should be explicit metadata.

### Mojibake/Encoding Risk

Terminal output shows Arabic/emoji text as mojibake in several files. The files may be UTF-8, but the development environment clearly has encoding display problems. Since labels are routing keys, encoding inconsistency can become a functional bug.

## Overall Debt Assessment

This code should not be expanded in its current form. Adding more subjects, channels, quizzes, or admin features will amplify the existing fragility.

The right next step is not cosmetic cleanup. The right next step is architectural extraction:

1. Configuration out of code.
2. Authorization as middleware.
3. Content mapping as database records.
4. Quiz logic as one reusable engine.
5. Async framework or async-compatible runtime.
6. Tests around routing and content lookup.
