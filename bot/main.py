import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS", "")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    return str(user_id) in ADMIN_IDS.split(",")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Unauthorized")
        return
    await update.message.reply_text(
        "ZEVRIC BOT ONLINE ✅\n\n"
        "/start - menu\n"
        "/setclan <id> - clan set\n"
        "/status - status"
    )

async def setclan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("Use: /setclan <clan_id>")
        return
    clan_id = context.args[0]
    await update.message.reply_text(f"Clan ID saved: {clan_id}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot running hai, safe mode me ✅")

def main():
    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_TOKEN env var nahi mila")
        return
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setclan", setclan))
    app.add_handler(CommandHandler("status", status))
    print("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
