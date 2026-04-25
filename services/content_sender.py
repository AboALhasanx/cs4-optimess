import logging

from global_vars import done_forward, not_post_yet
from services.content_registry import ContentRegistry

logger = logging.getLogger(__name__)

CONTENT_UNAVAILABLE_MESSAGE = "عذراً، هذا المحتوى غير متوفر حالياً."


def send_content_for_command(bot, message, registry: ContentRegistry, command: str) -> None:
    target = registry.get_content_for_command(command)
    if not target:
        bot.reply_to(message, not_post_yet)
        return

    try:
        for post_id in target.message_ids:
            bot.forward_message(message.chat.id, target.channel_id, post_id)
        bot.reply_to(message, done_forward)
    except Exception as exc:
        logger.exception("Failed to forward content for command %s", command)
        bot.reply_to(message, CONTENT_UNAVAILABLE_MESSAGE)
