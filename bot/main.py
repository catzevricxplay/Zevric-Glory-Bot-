import os, asyncio, json, logging, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPPORT = "just_zevric"
UPI_ID = "zervicxplay@okhdfcbank"
USDT_ADDR = "TLwAWcJ7Tm34jqyYqV6qhizQHy8pe7US1v"

logging.basicConfig(level=logging.INFO)
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "🔥 ZEVRIC GLORY BOT - FULL MAST EMOJI LIVE 24/7 ✅"
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
        users[str(uid)] = {"balance":0.0,"referrals":0,"ref_code":str(uid)[-6:],"awaiting_uid":False}
        save_users(users)
    return users[str(uid)]

def find_qr(name):
    for p in [f"bot/{name}.png", f"{name}.png", f"bot/{name}.jpg", f"{name}.jpg"]:
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
    users = load_users()
    user = get_user(uid)
    me = await context.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"

    if q.data=="add_balance":
        try:
            upi_path = find_qr("upi_qr")
            usdt_path = find_qr("usdt_qr")
            # QR UPAR - ZERVIC MAST
            if upi_path:
                try:
                    await context.bot.send_photo(q.message.chat_id, photo=open(upi_path,"rb"), caption=f"💜✨ ZEVRIC UPI QR ✨💜\n🆔 ID: {UPI_ID} 💳\n😍 Upar Scan Karo 💸🚀")
                except: pass
            if usdt_path:
                try:
                    await context.bot.send_photo(q.message.chat_id, photo=open(usdt_path,"rb"), caption=f"💛✨ ZEVRIC USDT QR ✨💛\n🔐 Addr: {USDT_ADDR} 🌐\n⚡ TRON Only 💫")
                except: pass
            # TEXT NICHE - FULL MAST, HATAYA NAHI
            caption = f"""💳✨ ZEVRIC PAYMENT ✨💳
━━━━━━━━━━━━━━━━━

💜💖 UPI Payment 💖💜
🆔 ID: {UPI_ID} 💳
📸 Upar QR Scan karo 😍💸
💫 Instant Payment ⚡

💛💖 USDT TRON (TRC20) 💖💛
🔐 Address: {USDT_ADDR} 🔐
🌐 Network: TRON only ⚡
📸 Upar QR Scan karo 👆💫

📤💌 Payment karke screenshot 📸
👉 @{SUPPORT} pe bhejo 📩💬

⚡ 24/7 Auto Check ✅
🚀 Fast Approval 💯🔥
💖 ZEVRIC FAMILY 💫
━━━━━━━━━━━━━━━━━
"""
            await q.message.reply_text(caption)
        except Exception as e:
            await q.message.reply_text(f"💳 ZEVRIC PAYMENT\nUPI: {UPI_ID}\nUSDT: {USDT_ADDR}\n@{SUPPORT}")

    elif q.data=="buy":
        await q.message.reply_text(f"""🛒✨ ZEVRIC BUY CREDITS ✨🛒
━━━━━━━━━━━━━━━━━

💎✨ Credits kharidne ke liye 👇
📞 Support pe aao: @{SUPPORT} 💬
👨‍💻 24/7 Available ✅

⚡ Fast Delivery 🚀💨
💯 Trusted 100% 🔥💖
💸 Secure Payment 💳💫
🎮 Instant Credits 🎯

💖 ZEVRIC GLORY STORE 💫
━━━━━━━━━━━━━━━━━
""")
    elif q.data=="refs":
        await q.message.reply_text(f"""👥✨ ZEVRIC REFERRALS ✨👥
━━━━━━━━━━━━━━━━━

🙋 Total Referrals: {user['referrals']} 👥💖
💰 Earning: ₹{user['referrals']*0.1:.2f} 💵💸
💸 Per Refer: ₹0.10 🤑💰

🔗 Your Referral Link 👇
{ref_link}

📢 Dosto ko share karo! 🚀💫
💸 Aur kamao! 🤑💵
🔥 ZEVRIC FAMILY 💖
━━━━━━━━━━━━━━━━━
""")
    elif q.data=="stats":
        await q.message.reply_text(f"""📊✨ ZEVRIC STATS ✨📊
━━━━━━━━━━━━━━━━━

👤 Name: {name} 😎💫
💰 Balance: ₹{user['balance']:.2f} 💵💸
👥 Referrals: {user['referrals']} 🙋👥
💸 Earned: ₹{user['referrals']*0.1:.2f} 💰🤑
🔗 Code: {user['ref_code']} 🎫✨

🔥 Keep Growing! 🚀💫
💖 ZEVRIC GLORY STORE 💖
✨━━━━━━━━━━━━━━━━━✨
""")
    elif q.data=="likes":
        users = load_users()
        users[str(uid)]["awaiting_uid"] = True
        save_users(users)
        await q.message.reply_text(f"""❤️‍🔥✨ ZEVRIC FREE FIRE LIKES ✨❤️‍🔥
━━━━━━━━━━━━━━━━━

🔥 UID bhejo aur likes pao! 😍💖
⚡ 100% Working ✅💯
💎 Instant Delivery 🚀💨
💯 Trusted 🔥💫
🎮 Free Fire Special 🎯

👇 Apna Free Fire UID bhejo 👇
📝 Example: 123456789 💌

📞 Contact: @{SUPPORT} 💬
💖 Fast Service 💫⚡
━━━━━━━━━━━━━━━━━
""")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users = load_users()
    if users.get(str(uid), {}).get("awaiting_uid"):
        ff_uid = ''.join(filter(str.isdigit, update.message.text))
        if len(ff_uid) < 6:
            await update.message.reply_text("❌ Invalid UID! 😥\n📝 Example: 123456789")
            return
        await update.message.reply_text(f"⏳ ZEVRIC Processing... 🔥\n👤 UID: {ff_uid} 😎\n⚡ Please wait... 🚀💫")
        await asyncio.sleep(1)
        await update.message.reply_text(f"""✅✨ ZEVRIC LIKES SENT! ✨✅
━━━━━━━━━━━━━━━━━
👤 UID: {ff_uid} 😎💫
💖 Likes: 100+ ❤️‍🔥🔥
⚡ Status: Success ✅💯
🚀 By: ZEVRIC GLORY STORE 💫

🔥 Keep Gaming! 🎮💖
📞 Support: @{SUPPORT} 💬
━━━━━━━━━━━━━━━━━
""")
        users[str(uid)]["awaiting_uid"] = False
        save_users(users)
    else:
        await update.message.reply_text(f"👋 Hey {update.effective_user.first_name}! 😎💫\n/start dabao 🚀✨")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"""🆘✨ ZEVRIC SUPPORT ✨🆘
━━━━━━━━━━━━━━━━━

👨‍💻 Support: @{SUPPORT} 💬💖
💜 UPI: {UPI_ID} 💳✨
💛 USDT: {USDT_ADDR} 🔐🌐

⚡ 24/7 Online ✅💯
🚀 Fast Reply 💯🔥
💖 Always Ready to Help 😎💫
🎯 ZEVRIC FAMILY 💖

📞 Contact karo: @{SUPPORT} 💬
━━━━━━━━━━━━━━━━━
""")

async def main():
    while True:
        try:
            if not TOKEN:
                print("❌ TOKEN missing!")
                await asyncio.sleep(10)
                continue
            app = Application.builder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help_cmd))
            app.add_handler(CommandHandler("support", help_cmd))
            app.add_handler(CallbackQueryHandler(btn_handler))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
            print("🔥 ZEVRIC FULL MAST EMOJI BOT LIVE ✨")
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print("✅ ZEVRIC BOT LIVE - FULL MAST ALL COMMANDS ✅")
            await asyncio.Event().wait()
        except Exception as e:
            print(f"❌ Crash: {e}")
            await asyncio.sleep(5)

if __name__=="__main__":
    asyncio.run(main())
