import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import os
import json
import asyncio
import re

# Emplacement du fichier de paliers sauvegardés
PALIERS_FILE = "paliers.json"

# Charger les paliers depuis le fichier (ou utiliser {} si fichier absent/corrompu)
def charger_paliers():
    try:
        with open(PALIERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

# Sauvegarder les paliers dans le fichier
def sauvegarder_paliers(paliers):
    with open(PALIERS_FILE, "w") as f:
        json.dump(paliers, f, indent=2, ensure_ascii=False)

# Au démarrage, on charge tous les paliers du fichier JSON
user_paliers = charger_paliers()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

CRYPTO_LIST = ['BTC', 'ETH', 'LINK', 'AVAX', 'TAO', 'SOL', 'ONDO', 'ESX']

def get_crypto_price(symbol):
    mapping = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'LINK': 'chainlink',
        'AVAX': 'avalanche-2',
        'TAO': 'bittensor',
        'SOL': 'solana',
        'ONDO': 'ondo-finance',
        'ESX': 'escoin-token'
    }
    try:
        coin_id = mapping.get(symbol.upper())
        if not coin_id:
            return None
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        resp = requests.get(url).json()
        return resp[coin_id]['usd']
    except Exception:
        return None

# ------------------ ALERTES AUTOMATIQUES ------------------
# Pour éviter de spammer les alertes à chaque boucle
alertes_envoyees = set()

async def surveiller_paliers(app):
    await app.bot.initialize()
    while True:
        for symbole in user_paliers:
            prix_actuel = get_crypto_price(symbole)
            if not prix_actuel:
                continue
            # Vérification des paliers d'achat
            for palier_txt in user_paliers[symbole]["achat"]:
                match = re.search(r"(\d+[ ,]?\d*)", palier_txt)
                if match:
                    palier_val = float(match.group(1).replace(" ", "").replace(",", "."))
                    if prix_actuel <= palier_val and (symbole, "achat", palier_val) not in alertes_envoyees:
                        await app.bot.send_message(
                            chat_id=TON_ID_TELEGRAM,  # Mets ici ton ID Telegram (ex : 123456789)
                            text=f"🔔 ALERTE ACHAT {symbole} : Prix actuel = {prix_actuel}$ ⏬\nPalier atteint : {palier_txt}"
                        )
                        alertes_envoyees.add((symbole, "achat", palier_val))
            # Vérification des paliers de vente
            for palier_txt in user_paliers[symbole]["vente"]:
                match = re.search(r"(\d+[ ,]?\d*)", palier_txt)
                if match:
                    palier_val = float(match.group(1).replace(" ", "").replace(",", "."))
                    if prix_actuel >= palier_val and (symbole, "vente", palier_val) not in alertes_envoyees:
                        await app.bot.send_message(
                            chat_id=TON_ID_TELEGRAM,  # Mets ici ton ID Telegram (ex : 123456789)
                            text=f"🔔 ALERTE VENTE {symbole} : Prix actuel = {prix_actuel}$ ⏫\nPalier atteint : {palier_txt}"
                        )
                        alertes_envoyees.add((symbole, "vente", palier_val))
        await asyncio.sleep(300)  # Toutes les 5 minutes

# ------------------ COMMANDES TELEGRAM ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 *Bienvenue sur le bot d’alertes crypto !*\n\n"
        "Voici les commandes disponibles :\n\n"
        "• /setpalier — Ajouter/modifier un seuil d’achat ou de vente\n"
        "• /paliers — Voir la liste de tes seuils enregistrés\n"
        "• /supprpalier — Supprimer un seuil\n"
        "• /prix — Voir le prix actuel d’une crypto\n"
        "• /help — Revoir cette liste de commandes\n\n"
        "_Exemples d’utilisation :_\n"
        "`/setpalier BTC achat 42000` (ajoute un seuil d’achat BTC à 42 000 $)\n"
        "`/setpalier ETH vente 8000` (ajoute un seuil de vente ETH à 8 000 $)\n"
        "`/prix SOL` (affiche le prix actuel du SOL)\n"
    )
    await update.message.reply_markdown(text)

help = start

async def setpalier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        _, symbole, type_palier, prix = update.message.text.split()
        symbole = symbole.upper()
        type_palier = type_palier.lower()
        prix = float(prix.replace(",", "."))
        if symbole not in CRYPTO_LIST or type_palier not in ["achat", "vente"]:
            await update.message.reply_text("Commande invalide. Exemple : /setpalier BTC achat 42000")
            return

        if symbole not in user_paliers:
            user_paliers[symbole] = {"achat": [], "vente": []}
        if prix not in [float(re.search(r"(\d+[ ,]?\d*)", p).group(1).replace(" ", "").replace(",", ".")) for p in user_paliers[symbole][type_palier] if re.search(r"(\d+[ ,]?\d*)", p)]:
            user_paliers[symbole][type_palier].append(f"{prix} $")
            user_paliers[symbole][type_palier].sort()
            sauvegarder_paliers(user_paliers)
        await update.message.reply_text(f"✅ Palier '{type_palier}' ajouté pour {symbole} à {prix} $")
    except Exception as e:
        await update.message.reply_text("Format incorrect. Exemple : /setpalier BTC achat 42000")

async def paliers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not user_paliers:
        await update.message.reply_text("Aucun palier enregistré. Utilise /setpalier pour en ajouter.")
        return
    text = "📊 *Paliers enregistrés :*\n"
    for symbole, p in user_paliers.items():
        for t in ["achat", "vente"]:
            if p[t]:
                text += f"\n_{symbole}_ — {t} : " + ", ".join([f"{x}" for x in p[t]])
    await update.message.reply_markdown(text)

async def supprpalier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        _, symbole, type_palier, prix = update.message.text.split()
        symbole = symbole.upper()
        type_palier = type_palier.lower()
        prix = float(prix.replace(",", "."))
        paliers = user_paliers.get(symbole, {}).get(type_palier, [])
        for p in paliers:
            match = re.search(r"(\d+[ ,]?\d*)", p)
            if match and float(match.group(1).replace(" ", "").replace(",", ".")) == prix:
                user_paliers[symbole][type_palier].remove(p)
                sauvegarder_paliers(user_paliers)
                await update.message.reply_text(f"❌ Palier supprimé pour {symbole} {type_palier} à {prix} $")
                return
        await update.message.reply_text("Ce palier n’existe pas.")
    except Exception:
        await update.message.reply_text("Format incorrect. Exemple : /supprpalier BTC achat 42000")

async def prix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        _, symbole = update.message.text.split()
        symbole = symbole.upper()
        if symbole not in CRYPTO_LIST:
            await update.message.reply_text("Crypto non reconnue. Essaie BTC, ETH, SOL, AVAX, etc.")
            return
        value = get_crypto_price(symbole)
        if value:
            await update.message.reply_text(f"Le prix actuel de {symbole} est : {value:,} $")
        else:
            await update.message.reply_text("Erreur lors de la récupération du prix.")
    except Exception:
        await update.message.reply_text("Format : /prix BTC")

# ------------------ LANCEMENT BOT ------------------

if __name__ == "__main__":
    TOKEN = "8160338970:AAHb3BwRAmedK4eHbcH_mlKc9LpcAGBBhck"  # <-- Mets ton token ici
    TON_ID_TELEGRAM = 1107884310   # <-- Mets ton ID Telegram ici (ex: 123456789)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("setpalier", setpalier))
    app.add_handler(CommandHandler("paliers", paliers))
    app.add_handler(CommandHandler("supprpalier", supprpalier))
    app.add_handler(CommandHandler("prix", prix))
    print("Bot lancé !")
    loop = asyncio.get_event_loop()
    loop.create_task(surveiller_paliers(app))
    app.run_polling()

