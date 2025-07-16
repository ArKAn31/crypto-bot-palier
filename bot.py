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

# Liste des paliers enregistrés
paliers = {
    "ETH": [3545, 4700, 5900, 7100],
    "LINK": [16.5, 22, 27],
    "FET": [0.96, 1.28, 1.92],
    "SOL": [215, 286, 358]
}

notified = set()
chat_id = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_id
    chat_id = update.effective_chat.id
    await update.message.reply_text("👋 Bot en ligne 24/7 sur Render. Je te préviens dès qu’un palier est atteint !")

async def show_paliers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 Paliers enregistrés :\n"
    for symbol, targets in paliers.items():
        for t in targets:
            msg += f"• {symbol} ≥ {t} €\n"
    await update.message.reply_text(msg)

def run_telegram_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("paliers", show_paliers))
    app_bot.run_polling()

def run_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    run_telegram_bot()
