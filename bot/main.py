import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS", "")

logging.basicConfig(level=logging.INFO)

def is_admin(user_id: int) -> bool:
    return str(user_id) in ADMIN_IDS.split(",")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized ❌")
        return
    keyboard = [
        [InlineKeyboardButton("📊 Status", callback_data="status"),
         InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    await update.message.reply_text(
        "ZEVRIC BOT ONLINE ✅\n/setclan <id> | /status | /start",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def setclan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Use: /setclan <clan_id>")
        return
    await update.message.reply_text(f"Clan ID saved: {context.args[0]}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot running hai, safe mode me ✅")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "status":
        await query.message.reply_text("Bot running hai ✅")
    elif query.data == "help":
        await query.message.reply_text("Use: /setclan <id> and /status")

async def main():
    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_TOKEN env var nahi mila")
        return
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setclan", setclan))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot starting...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())
