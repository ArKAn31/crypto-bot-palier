import os
import json
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
    # Construit le message ligne par ligne
    lignes = [f"🪙 *{symbole}* — Zones de *{type_zone}* :"]
    for z in zones:
        lignes.append(f"• {z}")
    return "\n".join(lignes)

# --- Handlers pour les commandes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Bot Crypto*\n\n"
        "Utilisez :\n"
        "/achat `<SYMBOL>` — pour les zones d’achat\n"
        "/vente `<SYMBOL>` — pour les zones de vente\n"
        "Exemple : `/achat BTC`",
        parse_mode="Markdown"
    )

async def achat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❗️ Usage : `/achat BTC`", parse_mode="Markdown")
    symbole = context.args[0].upper()
    msg = get_palier_message(symbole, "achat")
    await update.message.reply_text(msg, parse_mode="Markdown")

async def vente_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❗️ Usage : `/vente BTC`", parse_mode="Markdown")
    symbole = context.args[0].upper()
    msg = get_palier_message(symbole, "vente")
    await update.message.reply_text(msg, parse_mode="Markdown")

# --- Point d’entrée

def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("⚠️ La variable d’environnement TELEGRAM_TOKEN n’est pas définie.")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("achat", achat_command))
    app.add_handler(CommandHandler("vente", vente_command))
    print("🤖 Bot démarré en polling...")
    app.run_polling()

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()


