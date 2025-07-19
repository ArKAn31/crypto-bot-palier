def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("⚠️ La variable d’environnement TELEGRAM_TOKEN n’est pas définie.")

    # --- 1. Supprime tout webhook existant pour basculer en mode polling
    from telegram import Bot
    bot = Bot(token=token)
    bot.delete_webhook()
    print("✅ Webhook supprimé, passage en mode polling.")

    # --- 2. Démarre l'application en polling
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("achat", achat_command))
    app.add_handler(CommandHandler("vente", vente_command))
    print("🤖 Bot démarré en polling...")
    app.run_polling()
