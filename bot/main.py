import os, asyncio, json, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS", "")
SUPPORT = "just_zevric"
UPI_ID = "zervicxplay@okhdfcbank"
USDT_ADDR = "TLwAWcJ7Tm34jqyYqV6qhizQHy8pe7US1v"

logging.basicConfig(level=logging.INFO)

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

💡 Earn ₹0.1 per referral!
Support: @{SUPPORT}
"""
    kb = [
        [InlineKeyboardButton("➕ Add Balance", callback_data="add_balance"),
         InlineKeyboardButton("🎫 Buy Credits", callback_data="buy")],
        [InlineKeyboardButton("👥 My Referrals", callback_data="refs"),
         InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("📞 Support / Help", url=f"https://t.me/{SUPPORT}")],
        [InlineKeyboardButton("❤️‍🔥 Free Fire Likes", callback_data="likes")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

async def btn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = get_user(q.from_user.id)

    if q.data=="add_balance":
        caption = f"""💳 *ZEVRIC PAYMENT - Add Balance*

*1. UPI PAYMENT (Real QR):*
ID: `{UPI_ID}`
QR niche hai - scan karo

*2. USDT TRON (TRC20):*
Addr: `{USDT_ADDR}`
Network: TRON only
QR niche hai

Payment karke screenshot @{SUPPORT} pe bhejo.
"""
        await q.message.reply_text(caption, parse_mode="Markdown")
        # Real QR bhejo
        try:
            await context.bot.send_photo(chat_id=q.message.chat_id, photo=open("bot/upi_qr.jpg","rb"), caption=f"UPI QR - Scan to Pay - {UPI_ID}")
        except Exception as e:
            print(f"UPI QR error: {e}")
        try:
            await context.bot.send_photo(chat_id=q.message.chat_id, photo=open("bot/usdt_qr.jpg","rb"), caption=f"USDT TRON QR - {USDT_ADDR}")
        except Exception as e:
            print(f"USDT QR error: {e}")

    elif q.data=="buy":
        await q.message.reply_text("Buy karne ke liye Support pe aao.")
    elif q.data=="refs":
        await q.message.reply_text(f"Referrals: {user['referrals']} | Earning: ₹{user['referrals']*0.1:.2f}")
    elif q.data=="stats":
        await q.message.reply_text(f"ZEVRIC Account\nBalance: ₹{user['balance']:.2f}\nReferrals: {user['referrals']}")
    elif q.data=="likes":
        await q.message.reply_text("Free Fire Likes ke liye UID bhejo, Support handle karega.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ZEVRIC SUPPORT\nContact: @{SUPPORT}\nUPI: {UPI_ID}\nUSDT: {USDT_ADDR}")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("support", help_cmd))
    app.add_handler(CallbackQueryHandler(btn_handler))
    print("Zevric Bot starting with Real QR...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__=="__main__":
    asyncio.run(main())
