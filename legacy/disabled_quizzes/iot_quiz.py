import json
import random
import requests
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

user_data = {}

# تحميل جميع أسئلة IoT من GitHub بدون تحديد عدد أو تصفيتها
def load_iot_quiz():
    url = "https://raw.githubusercontent.com/AboALhasanx/json-files/refs/heads/main/iot_quiz.json"
    response = requests.get(url)
    if response.status_code == 200:
        all_data = response.json()
        return all_data  # إرجاع جميع الأسئلة الموجودة
    else:
        print("❌ فشل تحميل ملف الكويز:", response.status_code)
        return []

# كيبورد اختبار إنترنت الأشياء
def handle_iot_quiz_menu(bot, message):
    quiz_menu = ReplyKeyboardMarkup([ 
        [KeyboardButton("▶️ بدء الاختبار (IoT)")],
        [KeyboardButton("🎲 سؤال عشوائي (IoT)")],
        [KeyboardButton("⏹️ خروج من الاختبار")],
        [KeyboardButton("🔙 الرجوع إلى إنترنت الأشياء")]
    ], resize_keyboard=True)
    bot.reply_to(message, "اختر أحد الخيارات للاختبار 💡", reply_markup=quiz_menu)

# إرسال سؤال من الاختبار المتسلسل
def send_iot_question(bot, chat_id, context, index):
    quiz_data = context["iot_quiz"]
    total_questions = len(quiz_data)
    
    if index < total_questions:
        q = quiz_data[index]

        # إرسال السؤال كـ poll
        poll = bot.send_poll(
            chat_id,
            question=q["question"],
            options=q["options"],
            type='quiz',
            correct_option_id=q["correct_option_id"],
            is_anonymous=False
        )

        # تتبع الإجابة الصحيحة (فقط في وضع الاختبار الحقيقي)
        if context.get("tracking"):
            context["current_correct_option"] = q["correct_option_id"]

        # عرض التقدم مع السؤال
        progress_text = f"----[ سؤال {index + 1} من {total_questions} ]----"

        if index + 1 < total_questions:
            keyboard = InlineKeyboardMarkup([ 
                [InlineKeyboardButton(f"➡️ التالي", callback_data="next_iot")]
            ])
            bot.send_message(chat_id, progress_text, reply_markup=keyboard)
        else:
            # عرض النتيجة عند نهاية الاختبار
            if context.get("tracking"):
                score = context.get("score", 0)
                bot.send_message(chat_id, f"✅ تم الانتهاء من جميع الأسئلة!\n📊 نتيجتك: {score} من {total_questions}")
            else:
                bot.send_message(chat_id, "✅ تم الانتهاء من جميع الأسئلة!")

# بدء الاختبار الرسمي (مع التتبع)
def start_iot_test(bot, message):
    chat_id = message.chat.id
    quiz = load_iot_quiz()
    if not quiz:
        bot.send_message(chat_id, "🚫 لا توجد أسئلة متاحة لاختبار إنترنت الأشياء.")
        return
    user_data[chat_id] = {
        "iot_quiz": quiz,
        "index": 0,
        "score": 0,
        "tracking": True
    }
    send_iot_question(bot, chat_id, user_data[chat_id], 0)

# زر التالي في الاختبار
def next_iot_handler(bot, call):
    chat_id = call.message.chat.id
    if chat_id in user_data:
        user_data[chat_id]["index"] += 1
        send_iot_question(bot, chat_id, user_data[chat_id], user_data[chat_id]["index"])
    bot.answer_callback_query(call.id)

# سؤال عشوائي بدون تتبع
def random_iot_question(bot, message):
    quiz = load_iot_quiz()
    if not quiz:
        bot.send_message(message.chat.id, "🚫 لا توجد أسئلة متاحة.")
        return
    q = random.choice(quiz)
    bot.send_poll(
        chat_id=message.chat.id,
        question=q["question"],
        options=q["options"],
        type='quiz',
        correct_option_id=q["correct_option_id"],
        is_anonymous=False
    )

# الخروج من الاختبار (مع عرض النتيجة إذا كانت session تتبع)
def quit_quiz(bot, message, iot_theo_buttons, chose_from_markup):
    chat_id = message.chat.id
    if chat_id in user_data and user_data[chat_id].get("tracking"):
        score = user_data[chat_id].get("score", 0)
        total = len(user_data[chat_id]["iot_quiz"])
        bot.send_message(chat_id, f"📊 تم إنهاء الاختبار.\nنتيجتك: {score} من {total}")
    else:
        bot.send_message(chat_id, "❌ تم الخروج من الاختبار.")
    chose_from_markup(message, iot_theo_buttons())

# معالج Poll Answer (لحساب الإجابات الصحيحة)
def handle_poll_answer(bot, poll_answer):
    user_id = poll_answer.user.id
    selected = poll_answer.option_ids[0]

    if user_id in user_data:
        user = user_data[user_id]
        if user.get("tracking") and "current_correct_option" in user:
            correct = user["current_correct_option"]
            if selected == correct:
                user["score"] += 1
