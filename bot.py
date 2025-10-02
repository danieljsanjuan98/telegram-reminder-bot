import os
from datetime import time, timedelta
from telegram.ext import Application, CommandHandler, ContextTypes

# ⚠️ El token lo sacamos de las variables de entorno
TOKEN = os.getenv("TOKEN")

# ---- Handlers ----
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hola! Soy tu bot recordatorio.\n"
        "📌 Tengo 3 recordatorios activos todos los días de 8am a 8pm."
    )

async def stop(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛑 Bot detenido (aunque en Railway seguirá en ejecución).")

# ---- Main ----
def main():
    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))

    # Recordatorios diarios entre 8am y 8pm
    # 1) Cada 30 minutos
    app.job_queue.run_repeating(
        lambda ctx: ctx.bot.send_message(ctx.job.chat_id, "📝 Ya anotaste lo que tienes que hacer?"),
        interval=timedelta(minutes=30),
        first=time(8, 0),
        last=time(20, 0),
    )

    # 2) Cada 40 minutos
    app.job_queue.run_repeating(
        lambda ctx: ctx.bot.send_message(ctx.job.chat_id, "📌 Qué es lo que tienes pendiente para el día de hoy?"),
        interval=timedelta(minutes=40),
        first=time(8, 0),
        last=time(20, 0),
    )

    # 3) Cada 1 hora
    app.job_queue.run_repeating(
        lambda ctx: ctx.bot.send_message(ctx.job.chat_id, "✅ Ya hiciste lo que tenías pendiente por hacer? Revisa la lista."),
        interval=timedelta(hours=1),
        first=time(8, 0),
        last=time(20, 0),
    )

    print("🤖 Bot corriendo en Railway...")
    app.run_polling()

if __name__ == "__main__":
    main()
