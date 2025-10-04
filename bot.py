import os
from datetime import time, timedelta, datetime
from telegram.ext import Application, CommandHandler, ContextTypes

# ⚠️ Tu Chat ID para los recordatorios fijos
MY_CHAT_ID = 5776381212 

# ⚠️ El token lo sacamos de las variables de entorno
TOKEN = os.getenv("TOKEN")

# ---- Handlers ----
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hola! Soy tu bot recordatorio.\n"
        "📌 Tengo 3 recordatorios activos todos los días de 8am a 8pm.\n"
        "⚡ Usa /recordar [tu mensaje] para añadir un recordatorio temporal."
    )

async def stop(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛑 Bot detenido (aunque en Railway seguirá en ejecución).")


# ---- Recordatorios Personalizados ----

async def set_custom_reminder(update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Verificar si el usuario escribió un mensaje
    if not context.args:
        await update.message.reply_text(
            "Por favor, usa el formato: /recordar [tu mensaje]. Ejemplo: /recordar comprar cartulina"
        )
        return

    # 2. Extraer el mensaje del recordatorio y definir la finalización
    reminder_text = " ".join(context.args)
    interval = timedelta(minutes=10)
    
    # Finalización: Hoy a las 10:00 PM (22:00)
    today_date = datetime.now().date()
    end_datetime = datetime.combine(today_date, time(22, 0))

    # Nombre único para el trabajo. Usamos el chat_id como prefijo para que /cancelar lo encuentre.
    job_name = f"custom_reminder_active_{update.effective_chat.id}_{datetime.now().timestamp()}"

    # 3. Verificamos que la hora de finalización no haya pasado
    if end_datetime < datetime.now():
        await update.message.reply_text(
            # ✅ CORRECCIÓN 1: Mensaje de error de hora.
            "⚠️ La hora de finalización (10:00 PM) ya pasó hoy. Intenta con un /recordar después de medianoche."
        )
        return
    
    # 4. Programar el trabajo recurrente
    context.job_queue.run_repeating(
        lambda ctx: ctx.bot.send_message(
            ctx.job.chat_id, 
            f"🚨 **RECORDATORIO CADA 10 MINUTOS:** {reminder_text}"
        ),
        interval=interval,
        last=end_datetime,
        chat_id=update.effective_chat.id,
        name=job_name,
    )

    await update.message.reply_text(
        f"✅ Recordatorio configurado.\n"
        f"**Mensaje:** {reminder_text}\n"
        f"**Frecuencia:** Cada 10 minutos.\n"
        # ✅ CORRECCIÓN 2: Mensaje de confirmación de hora.
        f"**Finaliza:** Hoy a las 22:00 (10 PM)." 
    )

async def cancel_custom_reminders(update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # ✅ CORRECCIÓN 3: Reemplazamos get_jobs_by_chat_id (obsoleto) por jobs() y filtramos manualmente.
    all_jobs = context.job_queue.jobs()
    custom_jobs_cancelled = 0
    
    for job in all_jobs:
        # Verificamos si es un recordatorio personalizado para este chat
        expected_name_prefix = f"custom_reminder_active_{chat_id}"
        if job.name and job.name.startswith(expected_name_prefix):
            job.schedule_removal()
            custom_jobs_cancelled += 1

    if custom_jobs_cancelled > 0:
        await update.message.reply_text(
            f"🛑 Se cancelaron **{custom_jobs_cancelled}** recordatorios temporales (los creados con /recordar)."
        )
    else:
        await update.message.reply_text(
            "ℹ️ No se encontraron recordatorios temporales activos para cancelar."
        )


# ---- Main ----
def main():
    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    # Nuevos comandos de recordatorio
    app.add_handler(CommandHandler("recordar", set_custom_reminder))
    app.add_handler(CommandHandler("cancelar", cancel_custom_reminders))


    # Recordatorios diarios entre 8am y 8pm (CORREGIDO: Incluye MY_CHAT_ID)
    
    # 1) Cada 30 minutos
    app.job_queue.run_repeating(
        lambda ctx: ctx.bot.send_message(ctx.job.chat_id, "📝 Ya anotaste lo que tienes que hacer?"),
        interval=timedelta(minutes=30),
        first=time(8, 0),
        last=time(20, 0),
        chat_id=MY_CHAT_ID, # 👈 CHAT ID AÑADIDO
        name="daily_30min",
    )

    # 2) Cada 40 minutos
    app.job_queue.run_repeating(
        lambda ctx: ctx.bot.send_message(ctx.job.chat_id, "📌 Qué es lo que tienes pendiente para el día de hoy?"),
        interval=timedelta(minutes=40),
        first=time(8, 0),
        last=time(20, 0),
        chat_id=MY_CHAT_ID, # 👈 CHAT ID AÑADIDO
        name="daily_40min",
    )

    # 3) Cada 1 hora
    app.job_queue.run_repeating(
        lambda ctx: ctx.bot.send_message(ctx.job.chat_id, "✅ Ya hiciste lo que tenías pendiente por hacer? Revisa la lista."),
        interval=timedelta(hours=1),
        first=time(8, 0),
        last=time(20, 0),
        chat_id=MY_CHAT_ID, # 👈 CHAT ID AÑADIDO
        name="daily_1hr",
    )

    print("🤖 Bot corriendo en Railway...")
    app.run_polling()

if __name__ == "__main__":
    main()