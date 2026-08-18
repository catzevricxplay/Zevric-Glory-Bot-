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
    return "🔥 ZEVRIC - UPI/USDT SELECT LIVE ✅"
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

    # STEP 1: Add Balance click -> 2 options UPI / USDT
    if q.data=="add_balance":
        text = f"""💳✨ ZEVRIC PAYMENT - SELECT METHOD ✨💳
━━━━━━━━━━━━━━━━━

💰 Payment Method Choose Karo 👇

💜 UPI Payment - GPay, PhonePe, Paytm 💸
💛 USDT Payment - TRON TRC20 🌐

👇 Niche se select karo 👇
━━━━━━━━━━━━━━━━━
"""
        kb = [
            [InlineKeyboardButton("💜 UPI Payment 💳", callback_data="pay_upi"),
             InlineKeyboardButton("💛 USDT Payment 🌐", callback_data="pay_usdt")],
            [InlineKeyboardButton("🔙 Back to Menu 🏠", callback_data="back_menu")]
        ]
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

    # STEP 2: UPI selected -> Only UPI details
    elif q.data=="pay_upi":
        try:
            upi_path = find_qr("upi_qr")
            if upi_path:
                try:
                    await context.bot.send_photo(q.message.chat_id, photo=open(upi_path,"rb"), caption=f"💜✨ ZEVRIC UPI PAYMENT ✨💜\n━━━━━━━━━━━━━━━━━\n🆔 UPI ID: {UPI_ID} 💳\n💰 Method: UPI / GPay / PhonePe / Paytm 💸\n📸 Is QR ko UPI app se scan karo 😍🚀\n━━━━━━━━━━━━━━━━━")
                except Exception as e:
                    print(f"UPI error: {e}")
            caption = f"""💜✨ ZEVRIC UPI PAYMENT ✨💜
━━━━━━━━━━━━━━━━━

🆔 UPI ID: {UPI_ID} 💳
💰 GPay / PhonePe / Paytm / UPI 💸
📸 Upar QR ko UPI se scan karo 👆😍

💵 Amount: Aap jitna bhi bhejo 💰
⚡ Instant Add 💫

📤 Payment karke screenshot 📸
👉 @{SUPPORT} pe bhejo 📩💬

⚡ 24/7 Auto Check ✅
🚀 Fast Approval 💯🔥
💖 ZEVRIC FAMILY 💫
━━━━━━━━━━━━━━━━━
"""
            kb = [
                [InlineKeyboardButton("💛 USDT Payment 🌐", callback_data="pay_usdt"),
                 InlineKeyboardButton("🔙 Back 🏠", callback_data="back_menu")]
            ]
            await q.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb))
        except Exception as e:
            print(f"UPI handler error: {e}")

    # STEP 3: USDT selected -> Only USDT details
    elif q.data=="pay_usdt":
        try:
            usdt_path = find_qr("usdt_qr")
            if usdt_path:
                try:
                    await context.bot.send_photo(q.message.chat_id, photo=open(usdt_path,"rb"), caption=f"💛✨ ZEVRIC USDT PAYMENT ✨💛\n━━━━━━━━━━━━━━━━━\n🔐 Address: {USDT_ADDR} 🔐\n🌐 Network: TRON (TRC20) Only ⚡\n📸 Is QR ko USDT wallet se scan karo 👆🚀\n━━━━━━━━━━━━━━━━━")
                except Exception as e:
                    print(f"USDT error: {e}")
            caption = f"""💛✨ ZEVRIC USDT PAYMENT ✨💛
━━━━━━━━━━━━━━━━━

🔐 USDT Address: {USDT_ADDR} 🔐
🌐 Network: TRON (TRC20) Only ⚡
💰 USDT TRC20 Method 🚀

📸 Upar QR ko USDT wallet se scan karo 👆💫
⚠️ Sirf TRON network use karo ⚠️

💵 Amount: Aap jitna bhi bhejo 💰
⚡ Instant Add 💫

📤 Payment karke screenshot + TxID 📸
👉 @{SUPPORT} pe bhejo 📩💬

⚡ 24/7 Auto Check ✅
🚀 Fast Approval 💯🔥
💖 ZEVRIC FAMILY 💫
━━━━━━━━━━━━━━━━━
"""
            kb = [
                [InlineKeyboardButton("💜 UPI Payment 💳", callback_data="pay_upi"),
                 InlineKeyboardButton("🔙 Back 🏠", callback_data="back_menu")]
            ]
            await q.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb))
        except Exception as e:
            print(f"USDT handler error: {e}")

    elif q.data=="back_menu":
        # Wapas start menu
        await start(q, context)

    elif q.data=="buy":
        await q.message.reply_text(f"""🛒✨ ZEVRIC BUY CREDITS ✨🛒
━━━━━━━━━━━━━━━━━
💎 Credits kharidne ke liye 👇
📞 Support: @{SUPPORT} 💬
⚡ Fast Delivery 🚀
💯 Trusted 100% 🔥
━━━━━━━━━━━━━━━━━
""")
    elif q.data=="refs":
        await q.message.reply_text(f"""👥✨ ZEVRIC REFERRALS ✨👥
━━━━━━━━━━━━━━━━━
🙋 Total: {user['referrals']} 👥
💰 Earning: ₹{user['referrals']*0.1:.2f} 💵
🔗 {ref_link}
📢 Share karo! 🚀
━━━━━━━━━━━━━━━━━
""")
    elif q.data=="stats":
        await q.message.reply_text(f"""📊✨ ZEVRIC STATS ✨📊
━━━━━━━━━━━━━━━━━
👤 Name: {name} 😎
💰 Balance: ₹{user['balance']:.2f} 💵
👥 Referrals: {user['referrals']} 🙋
💸 Earned: ₹{user['referrals']*0.1:.2f} 💰
🔗 Code: {user['ref_code']} 🎫
━━━━━━━━━━━━━━━━━
""")
    elif q.data=="likes":
        users = load_users()
        users[str(uid)]["awaiting_uid"] = True
        save_users(users)
        await q.message.reply_text(f"""❤️‍🔥✨ ZEVRIC FREE FIRE LIKES ✨❤️‍🔥
━━━━━━━━━━━━━━━━━
🔥 UID bhejo aur likes pao! 😍
⚡ 100% Working ✅
💎 Instant Delivery 🚀
📞 @{SUPPORT} 💬
━━━━━━━━━━━━━━━━━
""")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users = load_users()
    if users.get(str(uid), {}).get("awaiting_uid"):
        ff_uid = ''.join(filter(str.isdigit, update.message.text))
        await update.message.reply_text(f"⏳ ZEVRIC Processing UID: {ff_uid} 🔥")
        await asyncio.sleep(1)
        await update.message.reply_text(f"✅ ZEVRIC LIKES SENT! 🔥\n👤 UID: {ff_uid} 😎\n💖 100+ Likes ❤️‍🔥\n⚡ ZEVRIC GLORY STORE 💫")
        users[str(uid)]["awaiting_uid"] = False
        save_users(users)
    else:
        await update.message.reply_text(f"👋 Hey {update.effective_user.first_name}! 😎 /start dabao 🚀")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"""🆘✨ ZEVRIC SUPPORT - FULL MAST ✨🆘
━━━━━━━━━━━━━━━━━
👨‍💻 Support: @{SUPPORT} 💬
💜 UPI: {UPI_ID} 💳
💛 USDT: {USDT_ADDR} 🔐
⚡ 24/7 Online ✅
🚀 Fast Reply 💯
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
            print("🔥 ZEVRIC - UPI/USDT SELECT - LIVE ✨")
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print("✅ ZEVRIC BOT LIVE - Add Balance -> UPI/USDT Select ✅")
            await asyncio.Event().wait()
        except Exception as e:
            print(f"❌ Crash: {e}")
            await asyncio.sleep(5)

if __name__=="__main__":
    asyncio.run(main())
