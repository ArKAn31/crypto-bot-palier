import os
import json
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
import logging

# Configuration du bot
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

# Activer les logs si besoin
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Charger les paliers
with open("paliers.json", encoding="utf-8") as f:
    paliers = json.load(f)

# Fonction d'affichage achat/vente
def get_palier_message(symbole: str, type_zone: str) -> str:
    symbole = symbole.upper()
    if symbole not in paliers:
        return f"❌ Crypto inconnue : {symbole}.\nUtilise un des symboles suivants : {', '.join(paliers.keys())}"
    
    zones = paliers[symbole].get(type_zone, [])
    if not zones:
        return f"Aucune zone de {type_zone} disponible pour {symbole}."
    
    titre = "📉 Zones d'achat" if type_zone == "achat" else "📈 Zones de vente"
    return f"{titre} pour {symbole} :\n\n" + "\n".join(zones)

# Commande /achat
def achat_handler(update: Update, context):
    if context.args:
        symbole = context.args[0]
        message = get_palier_message(symbole, "achat")
    else:
        message = "❗ Utilise la commande comme ceci : /achat BTC"
    update.message.reply_text(message)

# Commande /vente
def vente_handler(update: Update, context):
    if context.args:
        symbole = context.args[0]
        message = get_palier_message(symbole, "vente")
    else:
        message = "❗ Utilise la commande comme ceci : /vente ETH"
    update.message.reply_text(message)

# Ajouter les handlers
dispatcher.add_handler(CommandHandler("achat", achat_handler))
dispatcher.add_handler(CommandHandler("vente", vente_handler))

# Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

# Définir le webhook automatiquement au premier lancement
@app.before_first_request
def setup_webhook():
    public_url = os.environ.get("RENDER_EXTERNAL_URL")
    if public_url:
        bot.set_webhook(f"{public_url}/{TOKEN}")

# Page d’accueil simple
@app.route("/")
def index():
    return "✅ Bot Telegram crypto actif !"


