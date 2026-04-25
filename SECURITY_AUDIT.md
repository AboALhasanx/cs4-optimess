# Security Audit

## Executive Summary

This Telegram bot contains multiple high-risk security and privacy issues. The most serious problems are hardcoded live-looking credentials, misleading privacy messaging, inconsistent access control, unpinned dependencies, synchronous blocking network calls, and fragile message-forwarding rules.

From an engineering security perspective, the project is not production-safe in its current form. It can function as a personal/student utility, but it does not meet professional standards for credential handling, auditability, privacy, or operational resilience.

## Risk Register

| Severity | Area | Finding | Evidence | Impact | Recommendation |
| --- | --- | --- | --- | --- | --- |
| Critical | Secrets | Bot token is hardcoded in source code. | `config.py:2` | Anyone with the file can control or abuse the bot. | Rotate the token immediately and move secrets to environment variables. |
| High | Privacy | User-facing privacy claim conflicts with actual message logging. | `global_vars.py`, `main.py:801` | Users may believe messages are private while the bot forwards/logs them to an admin log channel. | Rewrite privacy notice and implement consent-aware logging. |
| High | Authorization | Forced subscription is not applied to content-forwarding handler. | `main.py:223`, `main.py:738`, `main.py:745` | Users can bypass channel membership by sending exact button text. | Apply authorization middleware before every protected content action. |
| High | Portability/Security | Bot forces a SOCKS proxy at localhost Tor-like port. | `main.py:6` | Runtime depends on hidden local network configuration; failures are opaque. | Move proxy config to optional environment variables. |
| Medium | Dependencies | No dependency manifest or lockfile exists. | Repository root | Impossible to reproduce, audit, or patch consistently. | Add `pyproject.toml` or `requirements.txt` plus lockfile. |
| Medium | Supply Chain | Quiz data is fetched live from GitHub raw URLs without timeout, validation, or caching. | `iot_quiz.py:11`, `mobApp_quiz.py:11`, `des_quiz.py:11` | External file changes can alter bot behavior; outages block quiz flow. | Cache, validate schema, pin trusted source, and add timeouts. |
| Medium | Error Handling | Broad `except Exception` hides root cause and can mask security failures. | `main.py:155`, `main.py:164`, `main.py:210`, `main.py:218`, `main.py:768`, `main.py:832` | Operational failures are swallowed or reduced to vague messages. | Catch specific exceptions and log structured context. |
| Medium | Privacy | Firebase stores user IDs, names, and usernames without local policy or retention controls. | `main.py:119`, `main.py:122` | Personal data collection lacks lifecycle governance. | Define retention, deletion, access policy, and data minimization. |

## Leak Detection

### Hardcoded Bot Token

The Telegram bot token is stored directly in `config.py`.

```python
BOT_TOKEN = "6717052387:AAGJwoObeqfKCnlZR0D6xPCcJqZ_oa8sbfg"
```

This is a critical leak pattern. Even if the token is no longer valid, the correct response is to treat it as compromised, rotate it through BotFather, and remove it from all repository history if this project is ever published.

### Hardcoded Administrative and Channel IDs

The project hardcodes:

```python
ADMIN_ID = 5664798395
cs_stg4 = -1002245627976
cs_stg4_onefile = -1002231449002
cs_stg4_deleted = -1001790832933
cs_apps = -1001802771388
LOG_CHANNEL_ID = -1003040612379
```

Hardcoding numeric Telegram IDs is not as severe as leaking the bot token, but it creates operational coupling and makes deployments unsafe across environments.

### Hardcoded Firebase Endpoint

`main.py` contains:

```python
FIREBASE_URL = "https://csbotproject-60ec6-default-rtdb.firebaseio.com/"
```

No authentication is visible in the code. If Firebase rules are permissive, the user database may be externally readable or writable. This cannot be fully confirmed from static code alone, but the risk is high enough to require a Firebase rules review.

## Privacy Analysis

### User-Facing Claim

The about text says, in effect, that exchanged messages are secret and will not be forwarded or shared with any third party.

### Actual Runtime Behavior

The fallback handler `log_and_forward` forwards/logs all non-admin messages to `LOG_CHANNEL_ID`.

```python
@bot.message_handler(func=lambda message: True, content_types=[...])
def log_and_forward(message):
    ...
    if user_id != ADMIN_ID:
        sent = bot.send_message(LOG_CHANNEL_ID, log_msg)
        if message.content_type == "text":
            bot.send_message(LOG_CHANNEL_ID, message.text, reply_to_message_id=sent.message_id)
        else:
            bot.forward_message(...)
```

This is a material privacy mismatch. It is not merely a wording bug. It is a trust and compliance issue.

## Vulnerability Mapping

### Access Control Bypass

The channel membership check is implemented in `check_and_respond`, but it is manually called only in selected menu handlers. The data-forwarding path does not call it:

```python
@bot.message_handler(func=lambda msg: msg.text in button_to_command.keys())
def handle_button(message):
    log_and_forward(message)
    command = button_to_command.get(message.text)
    get_file_command(message, command)
```

Result: protected file forwarding is not consistently protected. This is effectively a business-logic authorization flaw.

### IDOR-Like Forwarding Risk

The bot forwards Telegram messages by numeric message IDs stored in JSON:

```python
bot.forward_message(message.chat.id, CHANNEL_ID, post_id)
```

Users cannot directly pass arbitrary `post_id`, so this is not a classic user-controlled IDOR. However, the architecture is ID-based and fragile: if mappings are wrong, stale, or maliciously changed, the bot can forward unintended content from channels where the bot has access.

### Dependency Vulnerabilities

No dependency manifest exists, so the deployed dependency versions are unknown. Local environment inspection showed:

| Package | Local Status | Security/Version Note |
| --- | --- | --- |
| `pyTelegramBotAPI` / `telebot` | Not installed locally | Source requires it; latest checked version is `4.33.0` as of Apr 11, 2026. |
| `requests` | `2.31.0` installed locally | Outdated. Safety lists vulnerabilities affecting versions before `2.32.4` and `2.33.0`. |
| `Telethon` | `1.41.2` installed locally | Not imported by project. Latest checked version is `1.43.1` as of Apr 13, 2026. |
| `Pyrogram` | Not installed locally | Not imported by project. Latest checked version is `2.0.106` from Apr 30, 2023. |

Because no lockfile exists, any audit result is only provisional.

## Attack Vectors

### Token Abuse

If the token is valid, an attacker can operate the bot, inspect updates, message users, spam, or disrupt service.

### Privacy Exfiltration

Every user message can be copied to the log channel. Anyone with access to that channel sees user IDs, usernames, message types, text content, and forwarded media.

### External Content Poisoning

Quiz questions are pulled from raw GitHub URLs at runtime. If that repository or branch is changed, the bot consumes the new content immediately.

### Denial of Service

All network calls are synchronous and generally have no timeout. Firebase, GitHub, Telegram API, or proxy failures can block handler execution.

## Immediate Security Actions

1. Rotate the Telegram bot token.
2. Review Firebase database rules.
3. Remove secrets from source and use environment variables.
4. Add dependency pinning and a vulnerability scanner.
5. Fix the privacy notice or stop forwarding user messages.
6. Enforce subscription checks in the content-forwarding path.
7. Add HTTP timeouts to all external requests.
