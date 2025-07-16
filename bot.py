import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot en ligne 24/7 sur Render. Je te préviens dès qu’un palier est atteint !")

def run_telegram_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.run_polling()

def run_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    # Lancer Flask dans un thread à part
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Lancer le bot Telegram
    run_telegram_bot()