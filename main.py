import telebot
import random
import json
import requests
from telebot import apihelper
apihelper.proxy = {'https': 'socks5h://127.0.0.1:9050'}


from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import (
    LOG_CHANNEL_ID,
    ADMIN_ID,
    BOT_TOKEN,
    cs_stg4,
    cs_stg4_onefile,
    cs_stg4_deleted,
    cs_apps,
)
from global_vars import (
    done_forward,
    not_post_yet,
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
    mobApp_quiz_menu_buttons,
    mobile_applications_theo_buttons,
    iot_lab_buttons,
    iot_theo_buttons,
    english_buttons,
    com_skills_buttons,
    iot_quiz_menu_buttons,
    main_term_select,  # إن كنت تريد إظهار القائمة الرئيسية لاحقًا
)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

file_path = "/storage/emulated/0/csbot/cs4/terms_cmd2values.json"
commands_file_path = "/storage/emulated/0/csbot/cs4/terms_btn2cmd.json"


def load_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        return {}


def load_commands(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        return {}



# ========== تسجيل بيانات المستخدمين ==========
FIREBASE_URL = "https://csbotproject-60ec6-default-rtdb.firebaseio.com/"


def log_user(message):
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
        response = requests.get(f"{FIREBASE_URL}/users/{user_id}.json")
        if response.status_code == 200:
            existing_data = response.json()
            if not existing_data:
                requests.put(f"{FIREBASE_URL}/users/{user_id}.json", json=current_data)
                bot.send_message(
                    ADMIN_ID,
                    f"🆕 مستخدم جديد:\nID: {user_id}\nUsername: {current_data['username']}",
                )
            else:
                if (
                    existing_data.get("first_name") != current_data["first_name"]
                    or existing_data.get("username") != current_data["username"]
                ):
                    requests.put(
                        f"{FIREBASE_URL}/users/{user_id}.json", json=current_data
                    )
                    bot.send_message(
                        ADMIN_ID,
                        f"🔄 تم تحديث بيانات:\nID: {user_id}\nUsername: {current_data['username']}",
                    )
    except Exception as e:
        print(f"خطأ في Firebase: {e}")


def load_users():
    try:
        response = requests.get(f"{FIREBASE_URL}/users.json")
        if response.status_code == 200:
            return response.json() or {}
    except Exception as e:
        print(f"خطأ في جلب المستخدمين: {e}")
    return {}


# ========== أوامر الإذاعة =============
def deactivate_user(uid):
    """تقوم هذه الدالة بتحديث حالة المستخدم في قاعدة البيانات لتعتبره غير نشط (active=False) في حال لم يستجب للبوت (مثل حالة Forbidden)."""
    try:
        url = f"{FIREBASE_URL}/users/{uid}.json"
        response = requests.patch(url, json={"active": False})
        if response.status_code == 200:
            print(f"تم تحديث حالة المستخدم {uid} إلى غير نشط.")
        else:
            print(f"فشل تحديث حالة المستخدم {uid}: {response.status_code}")
    except Exception as ex:
        print(f"حدث خطأ أثناء تحديث حالة المستخدم {uid}: {ex}")


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


# ========== التحقق من الاشتراك بالقنوات ==========
def is_user_member(user_id, chat_id):
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False


def check_and_respond(message, response_function, *args):
    """دالة وسيطة تتأكد من اشتراك المستخدم بقنوات معينة قبل تنفيذ الدالة الفعلية (response_function)."""
    user = message.from_user
    first_name = user.first_name
    user_id = user.id
    required_channels = ["@cs_stg4"]
    all_membership_valid = all(
        is_user_member(user_id, channel) for channel in required_channels
    )
    if all_membership_valid:
        response_function(message, *args)
    else:
        bot.send_message(
            message.chat.id,
            f"⤦ اوكف {first_name} شو ما مشترك بالقناة ⁉️🫣\n"
            "اشترك وارجع اضغط على /start\n"
            "• قناة الملازم: @cs_stg4\n",
        )


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

    check_and_respond(message, respond)


def chose_from_markup(message, reply_markup):
    bot.reply_to(message, chose_from, parse_mode="HTML", reply_markup=reply_markup)


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

    def respond(msg):
        chose_from_markup(msg, main_term1_keyboard())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == graduation)
def graduation_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, graduation_keys())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == computer_security_lab_title)
def comp_sec_lab_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, computer_security_lab_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == computer_security_theo_title)
def comp_sec_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, computer_security_theo_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == image_process_lab_title)
def img_proc_lab_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, image_process_lab_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == image_process_theo_title)
def img_proc_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, image_process_theo_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == operation_systems_lab_title)
def op_sys_lab_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, operation_systems_lab_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == operation_systems_theo_title)
def op_sys_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, operation_systems_theo_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == algo_lab_title)
def algo_lab_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, algo_lab_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == algo_theo_title)
def algo_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, algo_theo_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == dis_systems_lab_title)
def dis_sys_lab_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, dis_systems_lab_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == dis_systems_theo_title)
def dis_sys_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, dis_systems_theo_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == web_prog_title)
def web_prog_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, web_prog_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == term1_Table_of_lectures)
def term1_table_redirect(message):
    log_and_forward(message)

    def respond(msg):
        bot.forward_message(msg.chat.id, cs_stg4, 39)

    check_and_respond(message, respond)


# ========== الكورس الثاني ==========
@bot.message_handler(commands=["term2"])
@bot.message_handler(func=lambda msg: msg.text in ["الكورس الثاني", back_term2])
def to_term2_menu(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, main_term2_keyboard())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == english_title)
def english_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, english_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == cloud_computing_lab_title)
def cloud_comp_lab_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, cloud_computing_lab_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == cloud_computing_theo_title)
def cloud_comp_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, cloud_computing_theo_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == mobile_applications_theo_title)
def mobile_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, mobile_applications_theo_buttons())

    check_and_respond(message, respond)


# -----------------------------------------------------------------------------------
# ========== اختبارات الكوزات تطبيقات الموبايل==========
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


def send_miniapp_button(message):
    # ننشئ لوحة الأزرار
    kb = InlineKeyboardMarkup()
    # هنا نستخدم WebAppInfo لتمرير رابط الـ Web App
    btn = InlineKeyboardButton(
        text="اضغط هنا للانتقال إلى الاختبار 🚀",
        web_app=WebAppInfo(
            url="https://aboalhasanx.github.io/des-quiz/preliminary.html"
        ),
    )
    kb.add(btn)
    bot.send_message(
        message.chat.id, "لمحاكاة ورقة الامتحان، اضغط على الزر:", reply_markup=kb
    )


@bot.message_handler(func=lambda m: m.text == "▶️ محاكاة ورقة الامتحان 📄")
def handle_start_des(m):
    log_and_forward(m)
    send_miniapp_button(m)


@bot.message_handler(func=lambda msg: msg.text == "📱 اختبارات كوزات 📝")
def handle_quiz_mobApp_menu(message):
    log_and_forward(message)
    bot.send_message(
        message.chat.id, "جاهز للتحدي؟ 😎", reply_markup=mobApp_quiz_menu_buttons()
    )


@bot.message_handler(func=lambda msg: msg.text == "▶️ بدء الاختبار 📱")
def start_quiz_mobApp(message):
    log_and_forward(message)
    from mobApp_quiz import start_mobApp_test

    start_mobApp_test(bot, message)


@bot.message_handler(func=lambda msg: msg.text == "🎲 سؤال عشوائي 📱")
def random_quiz_mobApp(message):
    log_and_forward(message)
    from mobApp_quiz import random_mobApp_question

    random_mobApp_question(bot, message)


@bot.message_handler(func=lambda msg: msg.text == "⏹️ خروج من الاختبار 📱")
def exit_quiz_mobApp(message):
    log_and_forward(message)
    from mobApp_quiz import quit_quiz

    quit_quiz(bot, message, mobile_applications_theo_buttons, chose_from_markup)


@bot.poll_answer_handler()
def on_poll_answer(poll_answer):
    from mobApp_quiz import handle_poll_answer

    handle_poll_answer(bot, poll_answer)


@bot.callback_query_handler(func=lambda call: call.data == "next_mobApp")
def handle_next_q(call):
    from mobApp_quiz import next_mobApp_handler

    next_mobApp_handler(bot, call)


# -----------------------------------------------------------------------------------


@bot.message_handler(func=lambda msg: msg.text == iot_lab_title)
def iot_lab_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, iot_lab_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == iot_theo_title)
def iot_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, iot_theo_buttons())

    check_and_respond(message, respond)


# ======================= اختبارات الكوزات إنترنت الأشياء =========================
@bot.message_handler(func=lambda msg: msg.text == "🦾 اختبارات كوزات 📝")
def handle_quiz_iot_menu(message):
    log_and_forward(message)
    bot.send_message(
        message.chat.id, "جاهز للتحدي؟ 😎", reply_markup=iot_quiz_menu_buttons()
    )


@bot.message_handler(func=lambda msg: msg.text == "▶️ بدء الاختبار 🦾")
def start_quiz_iot(message):
    log_and_forward(message)
    from iot_quiz import start_iot_test

    start_iot_test(bot, message)


@bot.message_handler(func=lambda msg: msg.text == "🎲 سؤال عشوائي 🦾")
def random_quiz_iot(message):
    log_and_forward(message)
    from iot_quiz import random_iot_question

    random_iot_question(bot, message)


@bot.message_handler(func=lambda msg: msg.text == "⏹️ خروج من الاختبار 🦾")
def exit_quiz_iot(message):
    log_and_forward(message)
    from iot_quiz import quit_quiz

    quit_quiz(bot, message, iot_theo_buttons, chose_from_markup)


@bot.poll_answer_handler()
def on_poll_answer(poll_answer):
    from iot_quiz import handle_poll_answer

    handle_poll_answer(bot, poll_answer)


@bot.callback_query_handler(func=lambda call: call.data == "next_iot")
def handle_next_q(call):
    from iot_quiz import next_iot_handler

    next_iot_handler(bot, call)


# ------------------------------------------------------------------------------------


@bot.message_handler(func=lambda msg: msg.text == design_and_analyze_systems_lab_title)
def das_lab_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, design_and_analyze_systems_lab_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == design_and_analyze_systems_theo_title)
def das_theo_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, design_and_analyze_systems_theo_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == com_skills_title)
def com_skills_redirect(message):
    log_and_forward(message)

    def respond(msg):
        chose_from_markup(msg, com_skills_buttons())

    check_and_respond(message, respond)


@bot.message_handler(func=lambda msg: msg.text == term2_Table_of_lectures)
def term2_table_redirect(message):
    log_and_forward(message)

    def respond(msg):
        bot.forward_message(msg.chat.id, cs_stg4, 40)

    check_and_respond(message, respond)


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

    check_and_respond(message, respond)


# ========== تحميل جدول الأوامر (buttons) من GitHub ==========
button_to_command = load_commands(commands_file_path)


@bot.message_handler(func=lambda msg: msg.text in button_to_command.keys())
def handle_button(message):
    log_and_forward(message)
    command = button_to_command.get(message.text)
    get_file_command(message, command)


def get_file_command(message, command):
    data = load_data(file_path)
    post_id_or_list = data.get("commands", {}).get(command)
    if "_full" in command:
        CHANNEL_ID = cs_stg4
    elif "_lectures" in command:
        CHANNEL_ID = cs_stg4_onefile
    elif "_old" in command:
        CHANNEL_ID = cs_stg4_deleted
    elif "_app" in command:
        CHANNEL_ID = cs_apps
    else:
        bot.reply_to(message, not_post_yet)
        return
    if post_id_or_list:
        try:
            if isinstance(post_id_or_list, list):
                for post_id in post_id_or_list:
                    bot.forward_message(message.chat.id, CHANNEL_ID, post_id)
                bot.reply_to(message, done_forward)
            else:
                bot.forward_message(message.chat.id, CHANNEL_ID, post_id_or_list)
                bot.reply_to(message, done_forward)
        except Exception:
            bot.reply_to(message, "اما تكون الرسالة ممسوحة من القنوات او غير موجودة🚫")
    else:
        bot.reply_to(message, not_post_yet)


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

    if user_id != ADMIN_ID:
        sent = bot.send_message(LOG_CHANNEL_ID, log_msg)

        # لو الرسالة نصية نرسلها كرد على رسالة التفاصيل
        if message.content_type == "text":
            bot.send_message(
                LOG_CHANNEL_ID, message.text, reply_to_message_id=sent.message_id
            )
        else:
            # للملفات والأنواع الأخرى فقط نعيد توجيه الرسالة (بدون رد)
            try:
                bot.forward_message(
                    chat_id=LOG_CHANNEL_ID,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                )
            except Exception as e:
                print(f"خطأ في إعادة توجيه الرسالة إلى القناة: {e}")


# ========== تشغيل البوت ==========
bot.polling()
