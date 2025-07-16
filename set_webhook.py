import os
from telegram import Bot

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = f"https://crypto-bot-palier.onrender.com/{TOKEN}"

bot = Bot(token=TOKEN)
print(bot.set_webhook(url=WEBHOOK_URL))
