import logging
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configure le logging pour voir les erreurs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Token de ton bot Telegram
TOKEN = "TON_TOKEN_ICI"  # remplace par ton vrai token

# Charger les paliers depuis le fichier JSON
with open("paliers.json", "r") as f:
    PALIERS = json.load(f)

# Fonction pour formater les paliers en texte
def formater_paliers(paliers):
    lignes = ["📊 Paliers enregistrés :"]
    for crypto, niveaux in paliers.items():
        for niveau in niveaux:
            lignes.append(f"• {crypto} ≥ {niveau} €")
    return "\n".join(lignes)

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot en ligne 24/7 sur Render.\nJe te préviens dès qu’un palier est atteint !\n\n" + formater_paliers(PALIERS))

# Commande /paliers
async def paliers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(formater_paliers(PALIERS))

# Main
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("paliers", paliers))

    app.run_polling()

