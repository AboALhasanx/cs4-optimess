import logging

import requests

logger = logging.getLogger(__name__)


def log_user(bot, message, admin_id: int, firebase_url: str) -> None:
    if not firebase_url:
        logger.warning("FIREBASE_URL is not configured; user logging skipped")
        return

    user_id = str(message.from_user.id)
    current_data = {
        "id": user_id,
        "first_name": message.from_user.first_name or "NoName",
        "username": (
            f"@{message.from_user.username}"
            if message.from_user.username
            else "NoUsername"
        ),
    }
    try:
        response = requests.get(f"{firebase_url}/users/{user_id}.json", timeout=10)
        if response.status_code == 200:
            existing_data = response.json()
            if not existing_data:
                requests.put(
                    f"{firebase_url}/users/{user_id}.json",
                    json=current_data,
                    timeout=10,
                )
                bot.send_message(
                    admin_id,
                    f"🆕 مستخدم جديد:\nID: {user_id}\nUsername: {current_data['username']}",
                )
            elif (
                existing_data.get("first_name") != current_data["first_name"]
                or existing_data.get("username") != current_data["username"]
            ):
                requests.put(
                    f"{firebase_url}/users/{user_id}.json",
                    json=current_data,
                    timeout=10,
                )
                bot.send_message(
                    admin_id,
                    f"🔄 تم تحديث بيانات:\nID: {user_id}\nUsername: {current_data['username']}",
                )
    except Exception as exc:
        logger.exception("Firebase user logging failed: %s", exc)


def load_users(firebase_url: str) -> dict:
    if not firebase_url:
        logger.warning("FIREBASE_URL is not configured; broadcast user list is empty")
        return {}

    try:
        response = requests.get(f"{firebase_url}/users.json", timeout=10)
        if response.status_code == 200:
            return response.json() or {}
    except Exception as exc:
        logger.exception("Failed to load users from Firebase: %s", exc)
    return {}


def deactivate_user(uid: str, firebase_url: str) -> None:
    if not firebase_url:
        return

    try:
        url = f"{firebase_url}/users/{uid}.json"
        response = requests.patch(url, json={"active": False}, timeout=10)
        if response.status_code == 200:
            logger.info("Marked user %s as inactive", uid)
        else:
            logger.warning("Failed to mark user %s inactive: %s", uid, response.status_code)
    except Exception as exc:
        logger.exception("Failed to deactivate user %s: %s", uid, exc)
