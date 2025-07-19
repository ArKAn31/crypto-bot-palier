import os
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

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
    return f"{titre} pour {symbole} :\n\n" + "\n".join(zones)

# --- Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salut ! Je suis CryptoPalierBot.\n"
        "Utilise `/achat <SYMBOL>` ou `/vente <SYMBOL>` pour obtenir tes paliers."
    )

async def achat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❗️ Usage : `/achat BTC`")
    message = get_palier_message(context.args[0], "achat")
    await update.message.reply_text(message)

async def vente_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❗️ Usage : `/vente ETH`")
    message = get_palier_message(context.args[0], "vente")
    await update.message.reply_text(message)

# --- Démarrage en polling
def main():
    token = os.environ["TELEGRAM_TOKEN"]
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("achat", achat_command))
    app.add_handler(CommandHandler("vente", vente_command))
    app.run_polling()

if __name__ == "__main__":
    main()
