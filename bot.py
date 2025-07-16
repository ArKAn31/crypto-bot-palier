import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)
app = Flask(__name__)

dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# Example command
def start(update, context):
    update.message.reply_text("👋 Bot en ligne via webhook !")

dispatcher.add_handler(CommandHandler("start", start))

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route('/')
def index():
    return "Bot is running!"    
