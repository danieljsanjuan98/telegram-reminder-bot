from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 🔹 Token del bot
TOKEN = "8337464151:AAGg3yQMl2jh3uNnpDqYSe7yYWxhbgSo6EQ"

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hola! Usa /recordar para activar un recordatorio cada minuto.")

# Función que envía el recordatorio
async def reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=context.job.chat_id, text="⏰ ¡Recordatorio!")

# Comando /recordar
async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    # 🔹 Ahora se usa context.application.job_queue
    context.job_queue.run_repeating(reminder, interval=60, first=5, chat_id=chat_id)
    await update.message.reply_text("✅ Recordatorio activado: recibirás un mensaje cada minuto.")

def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("recordar", set_reminder))

    # Arrancar bot
    app.run_polling()

if __name__ == "__main__":
    main()
