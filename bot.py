import os
import glob
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Отправь ссылку из YouTube, Instagram или TikTok"
    )

# ---------- DOWNLOAD ----------
@bot.message_handler(func=lambda m: True)
def download_video(message):

    url = message.text.strip()

    bot.send_message(message.chat.id, "⏳ Скачиваю видео...")

    # удаляем старые файлы
    files = glob.glob(f"{DOWNLOAD_FOLDER}/*")
    for f in files:
        os.remove(f)

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_FOLDER}/video.%(ext)s",
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        files = glob.glob(f"{DOWNLOAD_FOLDER}/*")

        if not files:
            bot.send_message(message.chat.id, "❌ Видео не найдено")
            return

        video_file = files[0]

        with open(video_file, "rb") as video:
            bot.send_video(message.chat.id, video)

    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка загрузки")

# ---------- KEEP ALIVE ----------
@app.route("/")
def home():
    return "Bot is running"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

Thread(target=run).start()

bot.infinity_polling()