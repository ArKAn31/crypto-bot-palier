import os
import json
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- Charge tes paliers
with open("paliers.json", encoding="utf-8") as f:
    paliers = json.load(f)

def get_palier_message(symbole: str, type_zone: str) -> str:
    symbole = symbole.upper()
    if symbole not in paliers:
        return f"❌ Crypto inconnue : {symbole}.\nCommandes valides : {', '.join(paliers.keys())}"
    zones = paliers[symbole].get(type_zone, [])
    if not zones:
        return f"Aucune zone de {type_zone} pour {symbole}."
    titre = "📉 Zones d'achat" if type_zone == "achat" else "📈 Zones de vente"
    return titre + f" pour {symbole} :\n\n" + "\n".join(zones)

# --- Handlers Telegram
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salut ! Je suis CryptoPalierBot.\n"
        "Utilise `/achat <SYMBOL>` ou `/vente <SYMBOL>`."
    )

async def achat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❗️ Usage : `/achat BTC`")
    await update.message.reply_text(get_palier_message(context.args[0], "achat"))

async def vente_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❗️ Usage : `/vente ETH`")
    await update.message.reply_text(get_palier_message(context.args[0], "vente"))

# --- Flask + Webhook
app = Flask(__name__)
TOKEN = os.environ["TELEGRAM_TOKEN"]
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("achat", achat_command))
application.add_handler(CommandHandler("vente", vente_command))

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "OK"

@app.route("/")
def home():
    return "✅ Bot actif sur Render !"

if __name__ == "__main__":
    # 1) on attend bien le set_webhook
    public_url = os.environ.get("RENDER_EXTERNAL_URL")
    if public_url:
        webhook_url = f"{public_url}/{TOKEN}"
        asyncio.run(application.bot.set_webhook(webhook_url))

    # 2) écoute du port fourni par Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
