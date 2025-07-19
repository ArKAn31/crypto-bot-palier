import os
import json
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

# Initialisation du bot avec le token
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)

# Flask pour recevoir les webhooks
app = Flask(__name__)

# Dispatcher pour gérer les commandes Telegram
dispatcher = Dispatcher(bot, None, workers=0)

# Chargement des données depuis paliers.json
with open("paliers.json", encoding="utf-8") as f:
    paliers = json.load(f)

# Séparation des paliers en achat et vente selon leur valeur
def get_achat_vente():
    achats = []
    ventes = []
    for palier in paliers:
        ligne = palier.strip()
        if "≥" in ligne:
            achats.append(ligne)
        elif "Vente" in ligne or "≥" not in ligne:
            ventes.append(ligne)
    return achats, ventes

# Commande /achat
def achat_command(update: Update, context):
    achats, _ = get_achat_vente()
    message = "📉 Zones d’achat :\n\n" + "\n".join(achats)
    update.message.reply_text(message)

# Commande /vente
def vente_command(update: Update, context):
    _, ventes = get_achat_vente()
    if ventes:
        message = "📈 Zones de vente :\n\n" + "\n".join(ventes)
    else:
        message = "Aucune zone de vente trouvée dans les données."
    update.message.reply_text(message)

# Ajout des commandes au dispatcher
dispatcher.add_handler(CommandHandler("achat", achat_command))
dispatcher.add_handler(CommandHandler("vente", vente_command))

# Route webhook pour Telegram
@app.route(f'/{TOKEN}', methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

# Configuration automatique du webhook à chaque lancement
@app.before_first_request
def setup_webhook():
    url = os.environ.get("RENDER_EXTERNAL_URL")  # doit être défini dans Render
    if url:
        webhook_url = f"{url}/{TOKEN}"
        bot.set_webhook(webhook_url)

# Route simple pour vérifier que le bot tourne
@app.route("/")
def index():
    return "Bot Telegram crypto actif !"

