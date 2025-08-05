import telebot
from flask import Flask, request
import os
import subprocess
import uuid

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def home():
    return "Bot is running!", 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "أرسل لي رابط فيديو من YouTube أو Instagram أو Facebook أو TikTok.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text.strip()
    if not any(x in url for x in ['youtube.com', 'youtu.be', 'tiktok.com', 'instagram.com', 'facebook.com']):
        bot.reply_to(message, "رابط غير مدعوم. أرسل رابط من YouTube أو TikTok أو Instagram أو Facebook.")
        return

    bot.reply_to(message, "جارٍ التحميل... ⏳")
    try:
        unique_id = str(uuid.uuid4())
        filename = f"{unique_id}.mp4"

        command = [
            "yt-dlp",
            "-o", filename,
            url
        ]
        subprocess.run(command, check=True)

        if os.path.exists(filename) and os.path.getsize(filename) <= 120 * 1024 * 1024:
            with open(filename, "rb") as video:
                bot.send_video(message.chat.id, video)
        else:
            bot.send_message(message.chat.id, "⚠️ الفيديو كبير جدًا أو فشل في التحميل.")

        os.remove(filename)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حصل خطأ: {e}")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN')}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))