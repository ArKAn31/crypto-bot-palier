import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)
app = Flask(__name__)

dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# Commande /start
def start(update, context):
    update.message.reply_text("👋 Bot en ligne via webhook !")

# Commande /paliers
def paliers(update, context):
    msg = (
        "📊 Paliers enregistrés :\n"
        "• ETH ≥ 3545 €\n"
        "• ETH ≥ 4700 €\n"
        "• ETH ≥ 5900 €\n"
        "• ETH ≥ 7100 €\n"
        "• LINK ≥ 16.5 €\n"
        "• LINK ≥ 22 €\n"
        "• LINK ≥ 27 €\n"
        "• FET ≥ 0.96 €\n"
        "• FET ≥ 1.28 €\n"
        "• FET ≥ 1.92 €\n"
        "• SOL ≥ 215 €\n"
        "• SOL ≥ 286 €\n"
        "• SOL ≥ 358 €"
    )
    update.message.reply_text(msg)

# Enregistrement des handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("paliers", paliers))

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route('/')
def index():
    return "Bot is running!"
