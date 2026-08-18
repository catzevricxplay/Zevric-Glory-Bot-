import os, asyncio, json, logging, threading, time
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPPORT = "just_zevric"
UPI_ID = "zervicxplay@okhdfcbank"
USDT_ADDR = "TLwAWcJ7Tm34jqyYqV6qhizQHy8pe7US1v"
ADMIN_IDS = os.getenv("ADMIN_IDS", "")

logging.basicConfig(level=logging.INFO)
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "🔥 ZEVRIC GUILD GLORY BOT - LIVE ✅"
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
        users[str(uid)] = {"balance":0.0,"referrals":0,"ref_code":str(uid)[-6:],"awaiting_screenshot":None}
        save_users(users)
    return users[str(uid)]

def load_pending():
    try:
        with open("pending.json","r") as f: return json.load(f)
    except: return {}
def save_pending(d):
    with open("pending.json","w") as f: json.dump(d,f)

def get_admins():
    admins=[]
    if ADMIN_IDS:
        for x in ADMIN_IDS.split(","):
            if x.strip().isdigit():
                admins.append(int(x.strip()))
    return admins

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
    text = f"""✨ ━━━━━━━━━━━━━━━━ ✨
  🎮 𝐙𝐄𝐕𝐑𝐈𝐂 𝐆𝐔𝐈𝐋𝐃 𝐆𝐋𝐎𝐑𝐘 𝐁𝐎𝐓 🎮
✨ ━━━━━━━━━━━━━━━━ ✨

👋 𝐇𝐞𝐲, {name}! 😎💫
🌟 𝒲𝑒𝓁𝒸𝑜𝓂𝑒 𝓉𝑜 𝒵𝑒𝓋𝓇𝒾𝒸 𝐹𝒶𝓂𝒾𝓁𝓎 💖

┏━ 𝐆𝐔𝐈𝐋𝐃 𝐆𝐋𝐎𝐑𝐘 𝐁𝐎𝐓 ━┓
🔥 Auto Custom Room 🏆
⚡ 100% Working | 24/7 🚀
💎 Elite Solo/Duo/Squad 🎯
┗━━━━━━━━━━━━┛

┏━ 𝙔𝙊𝙐𝙍 𝙒𝘼𝙇𝙇𝙀𝙏 ━┓
💰 ₹{user['balance']:.2f} 💵
💸 𝑬𝒂𝒓𝒏 ₹0.10 𝑝𝑒𝓇 𝑅𝑒𝒻𝑒𝓇 🤑
┗━━━━━━━━━━━━┛

🔗 𝒀𝒐𝒖𝒓 𝑳𝒊𝒏𝒌 👇
{ref_link}

💡 𝐁𝐨𝐭 𝐊𝐡𝐚𝐫𝐢𝐝𝐨 𝐀𝐮𝐫 𝐆𝐮𝐢𝐥𝐝 𝐆𝐥𝐨𝐫𝐲 𝐁𝐚𝐝𝐡𝐚𝐨! 🚀🏆
🎯 @{SUPPORT} 💬
✨ ━━━━━━━━━━━━━━━━ ✨
"""
    kb = [
        [InlineKeyboardButton("💳 𝐀𝐝𝐝 𝐁𝐚𝐥𝐚𝐧𝐜𝐞 💰", callback_data="add_balance"),
         InlineKeyboardButton("🛒 𝐁𝐮𝐲 𝐆𝐥𝐨𝐫𝐲 𝐁𝐨𝐭 🤖", callback_data="buy_glory")],
        [InlineKeyboardButton("👥 𝐑𝐞𝐟𝐞𝐫𝐫𝐚𝐥𝐬 🙋", callback_data="refs"),
         InlineKeyboardButton("📊 𝐒𝐭𝐚𝐭𝐬 ✨", callback_data="stats")],
        [InlineKeyboardButton("🏆 𝐆𝐮𝐢𝐥𝐝 𝐆𝐥𝐨𝐫𝐲 𝐏𝐥𝐚𝐧𝐬 📋", callback_data="glory_plans"),
         InlineKeyboardButton("🆘 𝐒𝐮𝐩𝐩𝐨𝐫𝐭 💬", url=f"https://t.me/{SUPPORT}")],
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
        text = f"""💳 𝐙𝐄𝐕𝐑𝐈𝐂 𝐏𝐀𝐘𝐌𝐄𝐍𝐓 💳
━━━━━━━━━━━━━━
💎 𝐌𝐞𝐭𝐡𝐨𝐝 𝐂𝐡𝐨𝐨𝐬𝐞 𝐊𝐚𝐫𝐨 👇
💜 UPI - GPay/PhonePe
💛 USDT - TRON TRC20
━━━━━━━━━━━━━━
"""
        kb = [
            [InlineKeyboardButton("💜 𝐔𝐏𝐈 💳", callback_data="pay_upi"),
             InlineKeyboardButton("💛 𝐔𝐒𝐃𝐓 🌐", callback_data="pay_usdt")],
            [InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤 🏠", callback_data="back_home")]
        ]
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

    elif q.data=="pay_upi":
        upi_path = find_qr("upi_qr")
        # SINGLE DETAIL - NO DOUBLE - QR + DETAILS ONE MESSAGE
        caption = f"""💜 𝐙𝐄𝐕𝐑𝐈𝐂 𝐔𝐏𝐈 𝐏𝐀𝐘𝐌𝐄𝐍𝐓 💜
━━━━━━━━━━━━━━━━━
🆔 𝐔𝐏𝐈 𝐈𝐃: {UPI_ID}
💰 GPay / PhonePe / Paytm
📸 QR Scan Karo Upar 👆

━━━━━━━━━━━━━━━━━
📸 𝐒𝐂𝐑𝐄𝐄𝐍𝐒𝐇𝐎𝐓 𝐘𝐀𝐇𝐈 𝐁𝐇𝐄𝐉𝐎 📸
━━━━━━━━━━━━━━━━━
✅ Payment ke baad isi chat me bhejo
🚫 Support pe mat bhejo

💖 𝐙𝐄𝐕𝐑𝐈𝐂 𝐅𝐀𝐌𝐈𝐋𝐘
"""
        if upi_path:
            await context.bot.send_photo(q.message.chat_id, photo=open(upi_path,"rb"), caption=caption)
        else:
            await q.message.reply_text(caption)
        users[str(uid)]["awaiting_screenshot"] = "UPI"
        save_users(users)

    elif q.data=="pay_usdt":
        usdt_path = find_qr("usdt_qr")
        caption = f"""💛 𝐙𝐄𝐕𝐑𝐈𝐂 𝐔𝐒𝐃𝐓 𝐏𝐀𝐘𝐌𝐄𝐍𝐓 💛
━━━━━━━━━━━━━━━━━
🔐 𝐀𝐝𝐝𝐫𝐞𝐬𝐬: {USDT_ADDR}
🌐 TRON (TRC20) Only
📸 QR Scan Karo Upar 👆
⚠️ Sirf TRON Network

━━━━━━━━━━━━━━━━━
📸 𝐒𝐂𝐑𝐄𝐄𝐍𝐒𝐇𝐎𝐓 + TxID 𝐘𝐀𝐇𝐈 📸
━━━━━━━━━━━━━━━━━
✅ Payment ke baad isi chat me bhejo
🚫 Support pe mat bhejo

💖 𝐙𝐄𝐕𝐑𝐈𝐂 𝐅𝐀𝐌𝐈𝐋𝐘
"""
        if usdt_path:
            await context.bot.send_photo(q.message.chat_id, photo=open(usdt_path,"rb"), caption=caption)
        else:
            await q.message.reply_text(caption)
        users[str(uid)]["awaiting_screenshot"] = "USDT"
        save_users(users)

    elif q.data=="buy_glory" or q.data=="glory_plans":
        text = f"""🤖✨ 𝐙𝐄𝐕𝐑𝐈𝐂 𝐆𝐔𝐈𝐋𝐃 𝐆𝐋𝐎𝐑𝐘 𝐁𝐎𝐓 ✨🤖
━━━━━━━━━━━━━━━━━

🏆 𝐏𝐥𝐚𝐧𝐬 & 𝐏𝐫𝐢𝐜𝐢𝐧𝐠 🏆

💜 𝐁𝐚𝐬𝐢𝐜 𝐏𝐥𝐚𝐧 - ₹299
• 1 Month Access 📅
• Auto Room Create 🏠
• Solo/Duo/Squad 🎯

💛 𝐏𝐫𝐨 𝐏𝐥𝐚𝐧 - ₹599 🔥 BEST
• 3 Months Access 📅
• Unlimited Rooms ♾️
• 24/7 Support 🆘
• Priority Setup ⚡

💎 𝐋𝐢𝐟𝐞𝐭𝐢𝐦𝐞 - ₹999 💖
• Lifetime Access ♾️
• All Features 🔓
• Custom Branding 🎨

━━━━━━━━━━━━━━━━━
💳 𝐁𝐮𝐲 𝐊𝐚𝐫𝐧𝐞 𝐊𝐞 𝐋𝐢𝐲𝐞 👇
💜 UPI / 💛 USDT se pay karo
📸 Screenshot yahi bhejo
⚡ Instant Setup 🚀

🎯 @{SUPPORT} 💬
━━━━━━━━━━━━━━━━━
"""
        kb = [
            [InlineKeyboardButton("💜 𝐁𝐮𝐲 𝐖𝐢𝐭𝐡 𝐔𝐏𝐈 💳", callback_data="pay_upi"),
             InlineKeyboardButton("💛 𝐁𝐮𝐲 𝐖𝐢𝐭𝐡 𝐔𝐒𝐃𝐓 🌐", callback_data="pay_usdt")],
            [InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤 🏠", callback_data="back_home")]
        ]
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

    elif q.data.startswith("approve_"):
        pid = q.data.replace("approve_","")
        pending = load_pending()
        if pid in pending:
            user_id = pending[pid]["user_id"]
            users = load_users()
            if str(user_id) in users:
                users[str(user_id)]["balance"] += 100.0
                save_users(users)
            pending[pid]["status"]="approved"
            save_pending(pending)
            await q.message.reply_text(f"✅ Approved {pid} +₹100")
            try:
                await context.bot.send_message(user_id, f"✅ 𝐏𝐚𝐲𝐦𝐞𝐧𝐭 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝! ₹100 Added\n🤖 Glory Bot ke liye @{SUPPORT} pe contact karo 💬")
            except: pass

    elif q.data.startswith("cancel_"):
        pid = q.data.replace("cancel_","")
        pending = load_pending()
        if pid in pending:
            user_id = pending[pid]["user_id"]
            pending[pid]["status"]="cancelled"
            save_pending(pending)
            await q.message.reply_text(f"❌ Cancelled {pid}")
            try:
                await context.bot.send_message(user_id, f"❌ Cancelled 😥 @{SUPPORT}")
            except: pass

    elif q.data=="back_home":
        await start(q, context)
    elif q.data=="add_balance":
        text = f"""💳 𝐙𝐄𝐕𝐑𝐈𝐂 𝐏𝐀𝐘𝐌𝐄𝐍𝐓\n💜 UPI | 💛 USDT\nSelect karo 👇"""
        kb = [[InlineKeyboardButton("💜 UPI 💳", callback_data="pay_upi"),
               InlineKeyboardButton("💛 USDT 🌐", callback_data="pay_usdt")]]
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
    elif q.data=="refs":
        await q.message.reply_text(f"👥 Refs: {user['referrals']} | ₹{user['referrals']*0.1:.2f}\n🔗 {ref_link}")
    elif q.data=="stats":
        await q.message.reply_text(f"📊 {name} | Balance: ₹{user['balance']:.2f}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users = load_users()
    awaiting = users.get(str(uid), {}).get("awaiting_screenshot")
    if awaiting:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        pid = f"{uid}_{int(time.time())}"
        pending = load_pending()
        pending[pid] = {"user_id": uid, "username": update.effective_user.username, "name": update.effective_user.first_name, "method": awaiting, "file_id": file_id, "status": "pending", "time": int(time.time())}
        save_pending(pending)
        users[str(uid)]["awaiting_screenshot"] = None
        save_users(users)
        await update.message.reply_text(f"✅ Screenshot Received! {awaiting}\n⏳ Admin approve karega 🚀\n🤖 Glory Bot Setup ke liye wait karo 💫")
        for admin_id in get_admins():
            try:
                kb = [[InlineKeyboardButton(f"✅ Approve +₹100", callback_data=f"approve_{pid}"),
                       InlineKeyboardButton(f"❌ Cancel", callback_data=f"cancel_{pid}")]]
                await context.bot.send_photo(admin_id, photo=file_id, caption=f"🚨 New Payment - {awaiting}\n👤 {update.effective_user.first_name} @{update.effective_user.username}\n🆔 {uid}\nPID: {pid}\n🤖 For Guild Glory Bot", reply_markup=InlineKeyboardMarkup(kb))
            except: pass
    else:
        await update.message.reply_text("📸 Pehle UPI/USDT select karo! /start")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users = load_users()
    if users.get(str(uid), {}).get("awaiting_screenshot"):
        await update.message.reply_text("📸 Photo bhejo, text nahi! 👆")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆘 @{SUPPORT} | Guild Glory Bot")

async def main():
    while True:
        try:
            if not TOKEN:
                await asyncio.sleep(10)
                continue
            app = Application.builder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help_cmd))
            app.add_handler(CommandHandler("support", help_cmd))
            app.add_handler(CallbackQueryHandler(btn_handler))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
            app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print("✅ GUILD GLORY BOT LIVE")
            await asyncio.Event().wait()
        except Exception as e:
            print(e)
            await asyncio.sleep(5)

if __name__=="__main__":
    asyncio.run(main())
