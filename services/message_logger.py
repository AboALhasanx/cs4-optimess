import logging

logger = logging.getLogger(__name__)


def log_and_forward_message(bot, message, admin_id: int, log_channel_id: int) -> None:
    if not log_channel_id:
        logger.warning("LOG_CHANNEL_ID is not configured; message logging skipped")
        return

    user_id = message.from_user.id
    username = message.from_user.username or "NoUsername"
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    full_name = (first_name + " " + last_name).strip()

    log_msg = (
        f"👤 رسالة جديدة:\n"
        f"• الاسم: {full_name}\n"
        f"• اليوزر: @{username}\n"
        f"• الايدي: {user_id}\n"
        f"• نوع الرسالة: {message.content_type}\n"
    )

    if user_id != admin_id:
        sent = bot.send_message(log_channel_id, log_msg)

        if message.content_type == "text":
            bot.send_message(
                log_channel_id, message.text, reply_to_message_id=sent.message_id
            )
        else:
            try:
                bot.forward_message(
                    chat_id=log_channel_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                )
            except Exception as exc:
                logger.exception("Failed to forward message to log channel: %s", exc)
