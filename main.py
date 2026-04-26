import telebot
import random
from telebot import apihelper


from config import (
    LOG_CHANNEL_ID,
    ADMIN_ID,
    BOT_TOKEN,
    FIREBASE_URL,
    TELEGRAM_PROXY_URL,
    cs_stg4,
)
from global_vars import (
    about_bot_msg,
    graduation,
    # كورس أول:
    back_term1,
    term1_Table_of_lectures,
    chose_from,
    algo_lab_title,
    algo_theo_title,
    computer_security_lab_title,
    computer_security_theo_title,
    image_process_lab_title,
    image_process_theo_title,
    operation_systems_lab_title,
    operation_systems_theo_title,
    dis_systems_lab_title,
    dis_systems_theo_title,
    web_prog_title,
    # كورس ثاني:
    back_term2,
    term2_Table_of_lectures,
    cloud_computing_lab_title,
    cloud_computing_theo_title,
    iot_lab_title,
    iot_theo_title,
    design_and_analyze_systems_lab_title,
    design_and_analyze_systems_theo_title,
    mobile_applications_lab_title,
    mobile_applications_theo_title,
    english_title,
    com_skills_title,
)

# استدعائات الكيبورد:
from term1_keyboard import (
    graduation_keys,
    main_term1_keyboard,
    computer_security_lab_buttons,
    computer_security_theo_buttons,
    image_process_lab_buttons,
    image_process_theo_buttons,
    operation_systems_lab_buttons,
    operation_systems_theo_buttons,
    algo_lab_buttons,
    algo_theo_buttons,
    dis_systems_lab_buttons,
    dis_systems_theo_buttons,
    web_prog_buttons,
)
from term2_keyboard import (
    give_rating,
    main_term2_keyboard,
    cloud_computing_lab_buttons,
    cloud_computing_theo_buttons,
    design_and_analyze_systems_lab_buttons,
    design_and_analyze_systems_theo_buttons,
    mobile_applications_theo_buttons,
    iot_lab_buttons,
    iot_theo_buttons,
    english_buttons,
    com_skills_buttons,
    main_term_select,  # إن كنت تريد إظهار القائمة الرئيسية لاحقًا
)
from services.content_registry import ContentRegistry
from services.content_sender import send_content_for_command
from services.message_logger import log_and_forward_message
from services.users_service import (
    deactivate_user as deactivate_firebase_user,
    load_users as load_firebase_users,
    log_user as log_firebase_user,
)

if TELEGRAM_PROXY_URL:
    apihelper.proxy = {"https": TELEGRAM_PROXY_URL}

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
content_registry = ContentRegistry()

# ========== تسجيل بيانات المستخدمين ==========


def log_user(message):
    return log_firebase_user(bot, message, ADMIN_ID, FIREBASE_URL)


def load_users():
    return load_firebase_users(FIREBASE_URL)


# ========== أوامر الإذاعة =============
def deactivate_user(uid):
    return deactivate_firebase_user(uid, FIREBASE_URL)


@bot.message_handler(commands=["bro"])
def broadcast(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "🚫 فقط الأدمن يمكنه استخدام هذا الأمر.")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❗ استخدم الأمر بالرد على الرسالة المراد إرسالها.")
        return
    original = message.reply_to_message
    users = load_users()
    count = 0
    for uid, info in users.items():
        if info.get("banned"):
            continue  # تجاهل المستخدمين المحظورين
        try:
            bot.copy_message(
                chat_id=int(uid),
                from_chat_id=original.chat.id,
                message_id=original.message_id,
            )
            count += 1
        except Exception as e:
            error_message = str(e)
            print(f"فشل الإرسال إلى {uid}: {error_message}")
            if "Forbidden" in error_message:
                deactivate_user(uid)
    bot.reply_to(message, f"✅ تم إرسال البرودكاست إلى {count} مستخدم.")


# ========== بدء المحادثة ==========
@bot.message_handler(commands=["start"])
def send_welcome(message):
    log_user(message)
    log_and_forward(message)

    def respond(msg):
        welcome_text = (
            "<b>• هلا بالخريج مالتنا 🎓✨\n\n"
            "• اختار من القائمة 🎛⚡️\n\n"
            "<blockquote>👨🏻‍💻المطور : @ab0_alhasan</blockquote>\n\n"
            "<blockquote>💻 قناة المشاريع البرمجية : @CodeLabIQ</blockquote></b>"
        )
        bot.reply_to(
            msg, welcome_text, parse_mode="HTML", reply_markup=main_term_select()
        )

    respond(message)


def chose_from_markup(message, reply_markup):
    bot.send_message(message.chat.id, chose_from, parse_mode="HTML", reply_markup=reply_markup)

def reply_with_markup(message, markup_factory):
    """Build a keyboard via markup_factory and send it with the standard prompt."""
    chose_from_markup(message, markup_factory())


# ========== أمر /about وأمر تقييم البوت ==========
@bot.message_handler(commands=["about"])
@bot.message_handler(func=lambda msg: msg.text == "🪧 عن البوت 🪧" or msg.text == "about")
def about_bot(message):
    log_and_forward(message)
    bot.reply_to(message, about_bot_msg, parse_mode="HTML")

@bot.message_handler(commands=["rate"])
@bot.message_handler(func=lambda msg: msg.text == "تقييم البوت" or msg.text == "rate")
def rating_bot(message):
    respond_to_rating(message)


def respond_to_rating(message):
    bot.reply_to(
        message,
        "<b>شنو تقييمك للبوت 👀❔</b>",
        parse_mode="HTML",
        reply_markup=give_rating(),
    )


@bot.message_handler(
    func=lambda msg: msg.text
    in [
        "🎖🏆 واحد عراق 😶‍🌫✋🏻",
        "عاش يسطا 👀🔥",
        "الله على الروقان ✨",
        "جيد 👍🙂",
        "تحجي صدك 🦦؟",
    ]
)
def handle_rating(message):
    rating = message.text
    good_response = ["حبيب اخوك 😇", "حبيبي نورتني ", "صدك جذب تدلل 😊"]
    veryGood_response = [
        "اخويا ياسطا 😎🤙🏻",
        "تسلم يالقالي 😴🫶",
        "نورك هذا لو الشمس؟ عمي منورنا 😔❤️‍🔥",
        "يا هلا وغلا بالعزيز 🫂❤️‍🔥",
        "شهادة اعتزُ بيها 🤝🏻",
        "هاي الوردة تستاهلك 🌹🫴",
    ]
    ok_response = [
        "خوش 🤨",
        "تمام 🙄",
        "ماشي 🙃",
        "اوك 🌚"
    ]
    if rating == "تحجي صدك 🦦؟":
        response_text = (
            "هاي ليش 💔🗿؟ \n" "راسلني وكلي اذا اكو مشكلة بالبوت @ab0_alhasan"
        )
    elif rating == "الله على الروقان ✨":
        response_text = random.choice(good_response)
    elif rating == "جيد 👍🙂":
        response_text = random.choice(ok_response)
    else:
        response_text = random.choice(veryGood_response)
    bot.send_message(message.chat.id, response_text, reply_markup=main_term_select())
    admin_msg = (
        f"📥 تقييم جديد!\n"
        f"👤 من: {message.from_user.first_name or ''} "
        f"@{message.from_user.username or '—'} (ID: {message.from_user.id})\n"
        f"💬 التقييم: {rating}"
    )
    bot.send_message(ADMIN_ID, admin_msg)


# ========== الكورس الأول ==========
@bot.message_handler(commands=["term1"])
@bot.message_handler(func=lambda msg: msg.text in ["الكورس الأول", back_term1])
def to_term1_menu(message):
    log_and_forward(message)
    reply_with_markup(message, main_term1_keyboard)


@bot.message_handler(func=lambda msg: msg.text == graduation)
def graduation_redirect(message):
    log_and_forward(message)
    reply_with_markup(message, graduation_keys)


@bot.message_handler(func=lambda msg: msg.text == computer_security_lab_title)
def comp_sec_lab_redirect(message):
    log_and_forward(message)
    reply_with_markup(message, computer_security_lab_buttons)


@bot.message_handler(func=lambda msg: msg.text == computer_security_theo_title)
def comp_sec_theo_redirect(message):
    log_and_forward(message)
    reply_with_markup(message, computer_security_theo_buttons)


@bot.message_handler(func=lambda msg: msg.text == image_process_lab_title)
def img_proc_lab_redirect(message):
    log_and_forward(message)
    reply_with_markup(message, image_process_lab_buttons)


@bot.message_handler(func=lambda msg: msg.text == image_process_theo_title)
def img_proc_theo_redirect(message):
    log_and_forward(message)
    reply_with_markup(message, image_process_theo_buttons)


@bot.message_handler(func=lambda msg: msg.text == operation_systems_lab_title)
def op_sys_lab_redirect(message):
    log_and_forward(message)
    reply_with_markup(message, operation_systems_lab_buttons)


@bot.message_handler(func=lambda msg: msg.text == operation_systems_theo_title)
def op_sys_theo_redirect(message):
    log_and_forward(message)
    reply_with_markup(message, operation_systems_theo_buttons)


@bot.message_handler(func=lambda msg: msg.text == algo_lab_title)
def algo_lab_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, algo_lab_buttons())

    respond(message)


@bot.message_handler(func=lambda msg: msg.text == algo_theo_title)
def algo_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, algo_theo_buttons())

    respond(message)


@bot.message_handler(func=lambda msg: msg.text == dis_systems_lab_title)
def dis_sys_lab_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, dis_systems_lab_buttons())

    respond(message)


@bot.message_handler(func=lambda msg: msg.text == dis_systems_theo_title)
def dis_sys_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, dis_systems_theo_buttons())

    respond(message)


@bot.message_handler(func=lambda msg: msg.text == web_prog_title)
def web_prog_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, web_prog_buttons())

    respond(message)


# ========== الكورس الثاني ==========
@bot.message_handler(commands=["term2"])
@bot.message_handler(func=lambda msg: msg.text in ["الكورس الثاني", back_term2])
def to_term2_menu(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, main_term2_keyboard())

    respond(message)


@bot.message_handler(func=lambda msg: msg.text == english_title)
def english_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, english_buttons())

    respond(message)


@bot.message_handler(func=lambda msg: msg.text == cloud_computing_lab_title)
def cloud_comp_lab_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, cloud_computing_lab_buttons())

    respond(message)


@bot.message_handler(func=lambda msg: msg.text == cloud_computing_theo_title)
def cloud_comp_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, cloud_computing_theo_buttons())

    respond(message)


@bot.message_handler(func=lambda msg: msg.text == mobile_applications_theo_title)
def mobile_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, mobile_applications_theo_buttons())

    respond(message)


@bot.message_handler(func=lambda msg: msg.text == iot_lab_title)
def iot_lab_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, iot_lab_buttons())

    respond(message)


@bot.message_handler(func=lambda msg: msg.text == iot_theo_title)
def iot_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, iot_theo_buttons())

    respond(message)


@bot.message_handler(func=lambda msg: msg.text == design_and_analyze_systems_lab_title)
def das_lab_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, design_and_analyze_systems_lab_buttons())

    respond(message)


@bot.message_handler(func=lambda msg: msg.text == design_and_analyze_systems_theo_title)
def das_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, design_and_analyze_systems_theo_buttons())

    respond(message)


@bot.message_handler(func=lambda msg: msg.text == com_skills_title)
def com_skills_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, com_skills_buttons())

    respond(message)


# زرّ القائمة الرئيسية أو الخروج من التقييم
@bot.message_handler(
    func=lambda msg: msg.text in ["القائمة الرئيسية", "خروج من التقييم"]
)
def return_to_main_menu(message):
    log_and_forward(message)

    def respond(msg):
        bot.reply_to(
            msg,
            "<b>القائمة الرئيسية</b>",
            parse_mode="HTML",
            reply_markup=main_term_select(),
        )

    respond(message)


# ========== تحميل جدول الأوامر (buttons) ==========
button_to_command = content_registry.button_to_command


@bot.message_handler(func=lambda msg: msg.text in button_to_command.keys())
def handle_button(message):
    log_and_forward(message)
    command = content_registry.get_command_for_button(message.text)
    get_file_command(message, command)


def get_file_command(message, command):
    send_content_for_command(bot, message, content_registry, command)


# ========== تسجيل كل رسالة واردة وإرسالها للإدمن ==========
@bot.message_handler(
    func=lambda message: True,
    content_types=[
        "text",
        "audio",
        "document",
        "photo",
        "sticker",
        "video",
        "voice",
        "video_note",
        "contact",
        "location",
        "new_chat_members",
        "left_chat_member",
        "new_chat_title",
        "new_chat_photo",
        "delete_chat_photo",
        "group_chat_created",
        "supergroup_chat_created",
        "channel_chat_created",
        "migrate_to_chat_id",
        "migrate_from_chat_id",
        "pinned_message",
    ],
)
def log_and_forward(message):
    log_and_forward_message(bot, message, ADMIN_ID, LOG_CHANNEL_ID)


# ========== تشغيل البوت ==========
bot.polling()
