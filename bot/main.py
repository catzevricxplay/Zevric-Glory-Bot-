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

# --- 24/7 KEEP ALIVE ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "✨ ZEVRIC BOT LIVE 24/7 🔥✅"

def run_flask():
    port = int(os.getenv('PORT', 10000))
    flask_app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()

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

def find_qr(name):
    for p in [f"bot/{name}.png", f"{name}.png", f"bot/{name}.jpg", f"{name}.jpg", f"bot/{name}.jpeg"]:
        if os.path.exists(p):
            return p
    return None

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
    text = f"""✨━━━━━━━━━━━━━━━━━✨
  🔥 ZEVRIC GLORY STORE 🔥
✨━━━━━━━━━━━━━━━━━✨

👋 Hey, {name}! 😎
💖 Welcome to Zevric Family 💫

💰 Wallet: ₹{user['balance']:.2f} 💵
💸 Earn: Refer & Get ₹0.10 🤑

🔗 Your Referral Link 👇
{ref_link}

💡 Share karo aur kamao! 🚀
🎯 Support 24/7: @{SUPPORT} 💬
✨━━━━━━━━━━━━━━━━━✨
"""
    kb = [
        [InlineKeyboardButton("💳 Add Balance 💰", callback_data="add_balance"),
         InlineKeyboardButton("🛒 Buy Credits 💎", callback_data="buy")],
        [InlineKeyboardButton("👥 My Referrals 🙋", callback_data="refs"),
         InlineKeyboardButton("📊 My Stats ✨", callback_data="stats")],
        [InlineKeyboardButton("🆘 Support / Help 💬", url=f"https://t.me/{SUPPORT}"),
         InlineKeyboardButton("❤️‍🔥 Free Fire Likes 🔥", callback_data="likes")],
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

async def btn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    name = q.from_user.first_name
    user = get_user(uid)
    me = await context.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"

    if q.data=="add_balance":
        caption = f"""💳✨ ZEVRIC PAYMENT ✨💳
━━━━━━━━━━━━━━━━━

💜 UPI Payment 💜
🆔 ID: `{UPI_ID}` 💳
📸 QR Code niche hai 👇
😍 Scan karo aur pay karo 💸

💛 USDT TRON (TRC20) 💛
🔐 Address:
`{USDT_ADDR}`
🌐 Network: TRON only ⚡
📸 QR Code niche hai 👇

📤 Payment karke screenshot 📸
👉 @{SUPPORT} pe bhejo 📩

⚡ 24/7 Auto Check ✅
🚀 Fast Approval 💯
━━━━━━━━━━━━━━━━━
"""
        await q.message.reply_text(caption, parse_mode="Markdown")
        upi_path = find_qr("upi_qr")
        usdt_path = find_qr("usdt_qr")
        if upi_path:
            try:
                await context.bot.send_photo(q.message.chat_id, photo=open(upi_path,"rb"), caption=f"💜 UPI QR 💜\n🆔 {UPI_ID} 💳\n👇 Scan karo 😍")
            except Exception as e:
                print(f"UPI error {e}")
        if usdt_path:
            try:
                await context.bot.send_photo(q.message.chat_id, photo=open(usdt_path,"rb"), caption=f"💛 USDT QR 💛\n🔐 {USDT_ADDR} 🌐")
            except Exception as e:
                print(f"USDT error {e}")

    elif q.data=="buy":
        await q.message.reply_text(f"""🛒✨ Buy Credits ✨🛒
━━━━━━━━━━━━━━━━━

💎 Credits kharidne ke liye 👇
📞 Support pe aao: @{SUPPORT} 💬

⚡ Fast Delivery 🚀
💯 Trusted 100% 🔥
💸 Secure Payment 💳
🕒 24/7 Available ✅

💖 Zevric Family 💫
━━━━━━━━━━━━━━━━━
""")

    elif q.data=="refs":
        await q.message.reply_text(f"""👥✨ Your Referrals ✨👥
━━━━━━━━━━━━━━━━━

🙋 Total Referrals: {user['referrals']} 👥
💰 Earning: ₹{user['referrals']*0.1:.2f} 💵
💸 Per Refer: ₹0.10 🤑

🔗 Your Link 👇
{ref_link}

📢 Dosto ko share karo! 🚀
💸 Aur kamao! 🤑
━━━━━━━━━━━━━━━━━
""")

    elif q.data=="stats":
        await q.message.reply_text(f"""📊✨ Your Stats ✨📊
━━━━━━━━━━━━━━━━━

👤 Name: {name} 😎
💰 Balance: ₹{user['balance']:.2f} 💵
👥 Referrals: {user['referrals']} 🙋
💸 Earned: ₹{user['referrals']*0.1:.2f} 💰
🔗 Code: {user['ref_code']} 🎫

🔥 Keep Growing! 🚀
💖 Zevric Family 💫
━━━━━━━━━━━━━━━━━
""")

    elif q.data=="likes":
        await q.message.reply_text(f"""❤️‍🔥✨ Free Fire Likes ✨❤️‍🔥
━━━━━━━━━━━━━━━━━

🔥 UID bhejo aur likes pao! 😍
⚡ 100% Working ✅
💎 Instant Delivery 🚀
💯 Trusted 🔥

📞 Contact: @{SUPPORT} 💬
💖 Fast Service 💫
━━━━━━━━━━━━━━━━━
""")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"""🆘✨ ZEVRIC SUPPORT ✨🆘
━━━━━━━━━━━━━━━━━

👨‍💻 Support: @{SUPPORT} 💬
💜 UPI: {UPI_ID} 💳
💛 USDT: {USDT_ADDR} 🔐

⚡ 24/7 Online ✅
🚀 Fast Reply 💯
💖 Always Ready to Help 😎
━━━━━━━━━━━━━━━━━
""")

async def support_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await help_cmd(update, context)

async def main():
    while True:
        try:
            if not TOKEN:
                print("❌ ERROR: TELEGRAM_TOKEN not set!")
                await asyncio.sleep(10)
                continue
            app = Application.builder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help_cmd))
            app.add_handler(CommandHandler("support", support_cmd))
            app.add_handler(CallbackQueryHandler(btn_handler))
            print("🔥 ZEVRIC EMOJI BOT starting... ✨")
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print("✅ Bot is Live 24/7 - /start working 🚀💯")
            await asyncio.Event().wait()
        except Exception as e:
            print(f"❌ Bot crashed: {e} 🔄 Restarting in 5 sec...")
            await asyncio.sleep(5)

if __name__=="__main__":
    asyncio.run(main())
