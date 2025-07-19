import os
import json
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Charger les paliers
with open("paliers.json", encoding="utf-8") as f:
    paliers = json.load(f)

# Flask app
app = Flask(__name__)
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Telegram bot app
app_telegram = ApplicationBuilder().token(TOKEN).build()

def get_palier_message(symbole: str, type_zone: str) -> str:
    symbole = symbole.upper()
    if symbole not in paliers:
        return f"❌ Crypto inconnue : {symbole}.\nCommandes valides : {', '.join(paliers.keys())}"
    zones = paliers[symbole].get(type_zone, [])
    if not zones:
        return f"Aucune zone de {type_zone} pour {symbole}."
    titre = "📉 Zones d'achat" if type_zone == "achat" else "📈 Zones de vente"
    # Retour sur une seule ligne pour éviter l'erreur
    return f"{titre} pour {symbole} :\n\n" + "\n".join(zones)

async def achat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        symbole = context.args[0]
        message = get_palier_message(symbole, "achat")
    else:
        message = "❗ Utilise la commande comme ceci : /achat BTC"
    await update.message.reply_text(message)

async def vente_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        symbole = context.args[0]
        message = get_palier_message(symbole, "vente")
    else:
        message = "❗ Utilise la commande comme ceci : /vente ETH"
    await update.message.reply_text(message)

# Ajouter les commandes
app_telegram.add_handler(CommandHandler("achat", achat_command))
app_telegram.add_handler(CommandHandler("vente", vente_command))

# Webhook route
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, app_telegram.bot)
    await app_telegram.process_update(update)
    return "OK"

@app.route("/")
def home():
    return "✅ Bot actif sur Render !"

if __name__ == "__main__":
    public_url = os.environ.get("RENDER_EXTERNAL_URL")
    if public_url:
        app_telegram.bot.set_webhook(f"{public_url}/{TOKEN}")
    app.run(host="0.0.0.0", port=10000)

