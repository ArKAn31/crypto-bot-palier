import os
import json
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Charger les données des paliers
with open("paliers.json", encoding="utf-8") as f:
    paliers = json.load(f)

# Crée l'application Telegram
TOKEN = os.environ.get("TELEGRAM_TOKEN")
app_telegram = ApplicationBuilder().token(TOKEN).build()

# Crée l'app Flask
app = Flask(__name__)

# Fonction pour récupérer les messages achat/vente
def get_palier_message(symbole: str, type_zone: str) -> str:
    symbole = symbole.upper()
    if symbole not in paliers:
        return f"❌ Crypto inconnue : {symbole}.\nCommandes valides : {', '.join(paliers.keys())}"
    zones = paliers[symbole].get(type_zone, [])
    if not zones:
        return f"Aucune zone de {type_zone} disponible pour {symbole}."
    titre = "📉 Zones d'achat" if type_zone == "achat" else "📈 Zones de vente"
    return f"{titre} pour {symbole} :\n\n" + "\n".join(zones)

# Commande /achat
async def achat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        symbole = context.args[0]
        message = get_palier_message(symbole, "achat")
    else:
        message = "❗ Utilise la commande comme ceci : /achat BTC"
    await update.message.reply_text(message)

# Commande /vente
async def vente_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        symbole = context.args[0]
        message = get_palier_message(symbole, "vente")
    else:
        message = "❗ Utilise la commande comme ceci : /vente ETH"
    await update.message.reply_text(message)

# Ajouter les handlers
app_telegram.add_handler(CommandHandler("achat", achat_command))
app_telegram.add_handler(CommandHandler("vente", vente_command))

# Route Flask pour Telegram (webhook)
@app.route(f'/{TOKEN}', methods=['POST'])
async def telegram_webhook():
    data = request.get_json(force=True)
    await app_telegram.update_queue.put(Update.de_json(data, app_telegram.bot))
    return "OK"

# Route d'accueil
@app.route("/")
def home():
    return "✅ Bot Telegram Crypto actif via Render !"

# Lancer l’app Flask
if __name__ == '__main__':
    # Webhook automatique
    public_url = os.environ.get("RENDER_EXTERNAL_URL")
    if public_url:
        app_telegram.bot.set_webhook(f"{public_url}/{TOKEN}")
    app.run(host="0.0.0.0", port=10000)

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


