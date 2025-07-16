import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

# Récupération du token depuis la variable d'environnement
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Initialisation du bot et de Flask
bot = Bot(token=TOKEN)
app = Flask(__name__)

# Configuration du dispatcher
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# Commande /start
def start(update, context):
    update.message.reply_text("✅ Bot en ligne via webhook !")

# Ajout de la commande au dispatcher
dispatcher.add_handler(CommandHandler("start", start))

# Route pour recevoir les requêtes du webhook
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# Route pour test simple
@app.route('/')
def index():
    return "🤖 Bot is running via webhook"

# Lancement de l'app Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

