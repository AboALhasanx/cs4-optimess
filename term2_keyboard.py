from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from global_vars import (
    graduation,
    back_term2,
    term1_Table_of_lectures,
    term2_Table_of_lectures,
    cloud_computing_lab_title,
    cloud_computing_theo_title,
    mobile_applications_theo_title,
    iot_lab_title,
    iot_theo_title,
    design_and_analyze_systems_lab_title,
    design_and_analyze_systems_theo_title,
    com_skills_title,
)


def main_term_select():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("الكورس الأول")
    button2 = KeyboardButton("الكورس الثاني")
    button3 = KeyboardButton("تقييم البوت")
    button4 = KeyboardButton("🪧 عن البوت 🪧")
    markup.add(button1)
    markup.add(button2)
    markup.add(button3)
    markup.add(button4)
    return markup


def main_term2_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button0 = KeyboardButton(term1_Table_of_lectures)
    button01 = KeyboardButton(term2_Table_of_lectures)
    button1 = KeyboardButton(cloud_computing_lab_title)
    button2 = KeyboardButton(cloud_computing_theo_title)
    button3 = KeyboardButton(design_and_analyze_systems_lab_title)
    button4 = KeyboardButton(design_and_analyze_systems_theo_title)
    button6 = KeyboardButton(mobile_applications_theo_title)
    button7 = KeyboardButton(iot_lab_title)
    button8 = KeyboardButton(iot_theo_title)
    button09 = KeyboardButton(com_skills_title)
    graduate = KeyboardButton(graduation)
    button10 = KeyboardButton("الكورس الأول")
    button13 = KeyboardButton("تقييم البوت")
    button14 = KeyboardButton("🪧 عن البوت 🪧")
    markup.add(button0)
    markup.add(button01)
    markup.add(button1, button2)
    markup.add(button3, button4)
    markup.add(button7, button8)
    markup.add(button6)
    markup.add(button09)
    markup.add(graduate)
    markup.add(button13, button14, button10)
    return markup


def give_rating():
    button_text = [
        "🎖🏆 واحد عراق 😶‍🌫✋🏻",
        "عاش يسطا 👀🔥",
        "الله على الروقان ✨😌",
        "جيد 👍🙂",
        "تحجي صدك 🦦؟",
        "خروج من التقييم",
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in button_text:
        button = KeyboardButton(text)
        markup.add(button)
    return markup


def graduation_keys():
    button_texts = [
        "فورمة مشروع التخرج الجزء النضري 2023-2024",
        "عناوين مشاريع مقترحة من التدريسيين لسنة 2023-2024",
        "بعض المشاريع -جزء نضري فقط- لسنة 2023-2024",
        "عناوين مشاريع التخرج لسنة 2024-2025",
        back_term2,
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in button_texts:
        button = KeyboardButton(text)
        markup.add(button)
    return markup


def cloud_computing_theo_buttons():
    button_texts = [
        "☁️ المحاضرات في ملف واحد كاملة 📁",
        "☁️ كل جابتر في ملف 🗂",
        "☁️ المحاضرات + الترجمة في ملف واحد كاملة 🇮🇶",
        "☁️ كل جابتر مترجم في ملف 🇮🇶",
        "☁️ محاضرات السنة السابقة 🕐",
        "☁️ ملحقات عشوائية من السنة السابقة 🕐",
        back_term2,
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in button_texts:
        button = KeyboardButton(text)
        markup.add(button)
    return markup


def cloud_computing_lab_buttons():
    button_texts = [
        "☁️ المادة في ملف واحد كاملة 📁",
        "☁️ كل جابتر  بملف 🗂",
        "☁️ البرنامج الي نطبق عليه Cisco Packet Tracer 💻",
        "☁️ مادة السنة السابقة 🕐",
        "☁️ ملحقـات عشوائية من السنة السابقة 🕐",
        back_term2,
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in button_texts:
        button = KeyboardButton(text)
        markup.add(button)
    return markup


def design_and_analyze_systems_theo_buttons():
    button_texts = [
        "📊 المحاضرات في ملف واحد كاملة 📁",
        "📊 كل جابتر  في ملف 🗂",
        "📊 المحاضرات + الترجمة في ملف واحد كاملة 🇮🇶",
        "📊 كل جابتر مترجم في ملف 🇮🇶",
        "📊 ملخصات وتوضيحات 📝",
        "📊 اسئلة وحلول 📝",
        "📊 محاضرات السنة السابقة 🕐",
        "📊 ملحقات عشوائية من السنة السابقة 🕐",
        back_term2,
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in button_texts:
        button = KeyboardButton(text)
        markup.add(button)
    return markup


def design_and_analyze_systems_lab_buttons():
    button_texts = [
        "📊 المادة في ملف واحد كاملة 📁",
        "📊 كل جابتر  بملف 🗂",
        "📊 البرنامج الي نطبق عليه StarUML 💻",
        "📊 مادة السنة السابقة 🕐",
        "📊 كوزات واختبارات 📝",
        back_term2,
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in button_texts:
        button = KeyboardButton(text)
        markup.add(button)
    return markup


def mobile_applications_theo_buttons():
    button_texts = [
        "📱 المحاضرات في ملف واحد كاملة 📁",
        "📱 ملخصات وتوضيحات 📝",
        "📱 اسئلة وحلول 📝",
        "📱 البرنامج الي نطبق عليه Flutter 💻",
        "📱 محاضرات السنة السابقة 🕐",
        "📱 ملحقات عشوائية من السنة السابقة 🕐",
        back_term2,
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in button_texts:
        button = KeyboardButton(text)
        markup.add(button)
    return markup


def iot_theo_buttons():
    button_texts = [
        "🦾 المحاضرات في ملف واحد كاملة 📁",
        "🦾 كل جابتر في ملف 🗂",
        "🦾 المحاضرات + الترجمة في ملف واحد كاملة 🇮🇶",
        "🦾 كل جابتر مترجم في ملف 🇮🇶",
        "🦾 ملخصات وتوضيحات 📝",
        "🦾 اسئلة وحلول 📝",
        "🦾 محاضرات السنة السابقة 🕐",
        "🦾 ملحقات عشوائية من السنة السابقة 🕐",
        back_term2,
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in button_texts:
        button = KeyboardButton(text)
        markup.add(button)
    return markup


def iot_lab_buttons():
    button_texts = [
        "🦾 المادة في ملف واحد كاملة 📁",
        "🦾 كل جابتر  بملف 🗂",
        "🦾 البرنامج الي نطبق عليه Arduino 💻",
        "🦾 مادة السنة السابقة 🕐",
        back_term2,
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in button_texts:
        button = KeyboardButton(text)
        markup.add(button)
    return markup


def english_buttons():
    button_text = [
        "🇬🇧 المحاضرات في ملف واحد كاملة 📁",
        "🇬🇧 كل يونت في ملف 🗂",
        "🇬🇧 حلول كل يونت  في ملف",
        "🇬🇧 محاضرات السنة السابقة 🕐",
        "🇬🇧 ملحقات عشوائية من السنة السابقة 🕐",
        back_term2,
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in button_text:
        button = KeyboardButton(text)
        markup.add(button)
    return markup


def com_skills_buttons():
    button_text = [
        "💬 المحاضرات في ملف واحد كاملة 📁",
        "💬 كل جابتر في ملف 🗂",
        back_term2,
    ]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in button_text:
        button = KeyboardButton(text)
        markup.add(button)
    return markup
