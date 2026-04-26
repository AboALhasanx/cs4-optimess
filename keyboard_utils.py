from telebot.types import KeyboardButton, ReplyKeyboardMarkup


def build_keyboard(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for row in rows:
        markup.row(*(KeyboardButton(text) for text in row))
    return markup
