
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = None

tracked_cryptos = {
    "ETH-EUR": [3545, 4700, 5900, 7100],
    "LINK-EUR": [16.5, 22, 27],
    "FET-EUR": [0.96, 1.28, 1.92],
    "SOL-EUR": [215, 286, 358],
}

notified = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    await context.bot.send_message(chat_id=CHAT_ID, text="👋 Bot en ligne 24/7 sur Render. Je te préviens dès qu’un palier est atteint !")

async def check_prices(application):
    bot = application.bot
    while True:
        if CHAT_ID is not None:
            for symbol, targets in tracked_cryptos.items():
                try:
                    price = yf.Ticker(symbol).info['regularMarketPrice']
                    for target in targets:
                        key = f"{symbol}-{target}"
                        if price >= target and key not in notified:
                            crypto_name = symbol.replace("-EUR", "")
                            message = f"🟢 {crypto_name} a atteint {price:.2f} € ! Palier visé : {target} €\n➡️ Action : vends selon ton plan 📈"
                            await bot.send_message(chat_id=CHAT_ID, text=message)
                            notified.add(key)
                except Exception as e:
                    print(f"Erreur pour {symbol} : {e}")
        await asyncio.sleep(1800)

async def on_startup(app):
    app.create_task(check_prices(app))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.post_init = on_startup
    print("🚀 Bot lancé sur Render !")
    app.run_polling()

if __name__ == "__main__":
    main()
