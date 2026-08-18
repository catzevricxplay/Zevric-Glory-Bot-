import os, asyncio, json, logging, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS", "")
SUPPORT = "just_zevric"
UPI_ID = "zervicxplay@okhdfcbank"
USDT_ADDR = "TLwAWcJ7Tm34jqyYqV6qhizQHy8pe7US1v"

logging.basicConfig(level=logging.INFO)

# --- 24/7 KEEP ALIVE WEB SERVER ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "ZEVRIC BOT IS LIVE 24/7 ✅"

def run_flask():
    # Render 10000 port deta hai
    flask_app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()

# --- BOT DATA ---
def load_users():
    try:
        with open("users.json","r") as f: return json.load(f)
    except: return {}

def save_users(d):
    with open("users.json","w") as f: json.dump(d,f)

def get_user(uid):
    users = load_users()
    if str(uid) not in users:
        users[str(uid)] = {"balance":0.0,"referrals":0,"ref_code":str(uid)[-6:]}
        save_users(users)
    return users[str(uid)]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.first_name
    users = load_users()
    if context.args:
        for k,v in users.items():
            if v.get("ref_code")==context.args[0] and k!=str(uid):
                users[k]["balance"]+=0.1
                users[k]["referrals"]+=1
                save_users(users)
                break
    user = get_user(uid)
    me = await context.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"
    text = f"""╔════════════════════╗
   ZEVRIC GLORY STORE
╚════════════════════╝

👋 Welcome, Boss {name}!

💵 Wallet Balance: ₹{user['balance']:.2f}
🔗 Referral Link:
{ref_link}

Support: @{SUPPORT} | 24/7 Online ✅
"""
    kb = [
        [InlineKeyboardButton("➕ Add Balance", callback_data="add_balance"),
         InlineKeyboardButton("🎫 Buy Credits", callback_data="buy")],
        [InlineKeyboardButton("👥 My Referrals", callback_data="refs"),
         InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("📞 Support / Help", url=f"https://t.me/{SUPPORT}")],
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

async def btn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = get_user(q.from_user.id)
    if q.data=="add_balance":
        caption = f"""💳 *ZEVRIC PAYMENT*

*1. UPI:*
ID: `{UPI_ID}`

*2. USDT TRON:*
`{USDT_ADDR}`

Screenshot @{SUPPORT} pe bhejo, 24/7 auto check.
"""
        await q.message.reply_text(caption, parse_mode="Markdown")
        try:
            await context.bot.send_photo(q.message.chat_id, photo=open("bot/upi_qr.jpg","rb"), caption=f"UPI QR - {UPI_ID}")
        except: pass
        try:
            await context.bot.send_photo(q.message.chat_id, photo=open("bot/usdt_qr.jpg","rb"), caption=f"USDT QR - {USDT_ADDR}")
        except: pass
    elif q.data=="refs":
        await q.message.reply_text(f"Referrals: {user['referrals']} | Earning: ₹{user['referrals']*0.1:.2f}")
    elif q.data=="stats":
        await q.message.reply_text(f"Balance: ₹{user['balance']:.2f} | Referrals: {user['referrals']}")
    else:
        await q.message.reply_text(f"Contact @{SUPPORT}")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ZEVRIC 24/7 SUPPORT\n@{SUPPORT}\nUPI: {UPI_ID}\nUSDT: {USDT_ADDR}")

async def main():
    while True:
        try:
            app = Application.builder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help_cmd))
            app.add_handler(CommandHandler("support", help_cmd))
            app.add_handler(CallbackQueryHandler(btn_handler))
            print("ZEVRIC 24/7 Bot starting...")
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print("Bot is Live 24/7 ✅")
            await asyncio.Event().wait()
        except Exception as e:
            print(f"Bot crashed, restarting in 5 sec: {e}")
            await asyncio.sleep(5)

if __name__=="__main__":
    asyncio.run(main())
