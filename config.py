import os

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()


def _get_int(name: str, default: int = 0) -> int:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Environment variable {name} must be an integer")


BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = _get_int("ADMIN_ID")
LOG_CHANNEL_ID = _get_int("LOG_CHANNEL_ID")

CS_STG4_CHANNEL_ID = _get_int("CS_STG4_CHANNEL_ID")
CS_STG4_ONEFILE_CHANNEL_ID = _get_int("CS_STG4_ONEFILE_CHANNEL_ID")
CS_STG4_DELETED_CHANNEL_ID = _get_int("CS_STG4_DELETED_CHANNEL_ID")
CS_APPS_CHANNEL_ID = _get_int("CS_APPS_CHANNEL_ID")

FIREBASE_URL = os.getenv("FIREBASE_URL", "")
TELEGRAM_PROXY_URL = os.getenv("TELEGRAM_PROXY_URL", "")

# Backward-compatible names used by the legacy main.py.
cs_stg4 = CS_STG4_CHANNEL_ID
cs_stg4_onefile = CS_STG4_ONEFILE_CHANNEL_ID
cs_stg4_deleted = CS_STG4_DELETED_CHANNEL_ID
cs_apps = CS_APPS_CHANNEL_ID
