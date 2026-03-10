import os
import json
import datetime
import glob
import telebot
import yt_dlp
from telebot import types

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 7775541802
LIMIT = 5
DB_FILE = "users.json"

bot = telebot.TeleBot(TOKEN)

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE,"r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE,"w") as f:
        json.dump(db,f)

def check_limit(user_id):
    db = load_db()
    today = str(datetime.date.today())

    user = db.get(str(user_id), {"date":today,"count":0,"lang":"ru"})

    if user["date"] != today:
        user["date"] = today
        user["count"] = 0

    if user["count"] >= LIMIT:
        return False

    user["count"] += 1
    db[str(user_id)] = user
    save_db(db)
    return True

@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Русский 🇷🇺","Тоҷикӣ 🇹🇯")

    bot.send_message(
        message.chat.id,
        "Выберите язык / Забонро интихоб кунед",
        reply_markup=markup
    )

@bot.message_handler(commands=['admin'])
def admin(message):

    if message.from_user.id != ADMIN_ID:
        return

    db = load_db()
    bot.send_message(message.chat.id,f"Пользователей: {len(db)}")

@bot.message_handler(func=lambda m: True)
def download(message):

    user_id = message.from_user.id

    if not check_limit(user_id):
        bot.send_message(message.chat.id,"Лимит 5 скачиваний в день.")
        return

    url = message.text.strip()

    bot.send_message(message.chat.id,"⏳ Скачиваю...")

    ydl_opts = {
        "format": "best",
        "outtmpl": "video.%(ext)s",
        "noplaylist": True
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        files = glob.glob("video.*")

        if len(files) == 0:
            bot.send_message(message.chat.id,"Ошибка файла.")
            return

        video_file = files[0]

        with open(video_file,"rb") as v:
            bot.send_video(message.chat.id,v)

        os.remove(video_file)

    except Exception as e:
        bot.send_message(message.chat.id,"Ошибка загрузки.")

bot.infinity_polling()