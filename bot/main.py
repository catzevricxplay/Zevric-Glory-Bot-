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
    return "🔥 ZEVRIC - NO SUPPORT SS - BOT CHAT SS ONLY ✅"
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
        users[str(uid)] = {"balance":0.0,"referrals":0,"ref_code":str(uid)[-6:],"awaiting_uid":False,"awaiting_screenshot":None}
        save_users(users)
    return users[str(uid)]

def load_pending():
    try:
        with open("pending.json","r") as f: return json.load(f)
    except: return {}
def save_pending(d):
    with open("pending.json","w") as f: json.dump(d,f)

def get_admins():
    admins = []
    if ADMIN_IDS:
        for x in ADMIN_IDS.split(","):
            x=x.strip()
            if x.isdigit():
                admins.append(int(x))
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
  🎮 𝐙𝐄𝐕𝐑𝐈𝐂 𝐆𝐋𝐎𝐑𝐘 𝐒𝐓𝐎𝐑𝐄 🎮
✨ ━━━━━━━━━━━━━━━━ ✨

👋 𝐇𝐞𝐲, {name}! 😎💫
🌟 𝒲𝑒𝓁𝒸𝑜𝓂𝑒 𝓉𝑜 𝒵𝑒𝓋𝓇𝒾𝒸 𝐹𝒶𝓂𝒾𝓁𝓎 💖🔥

┏━ 𝙔𝙊𝙐𝙍 𝙒𝘼𝙇𝙇𝙀𝙏 ━┓
💰 ₹{user['balance']:.2f} 𝐵𝒶𝓁𝒶𝓃𝒸𝑒 💵
💸 𝑬𝒂𝒓𝒏 ₹0.10 𝑝𝑒𝓇 𝑅𝑒𝒻𝑒𝓇 🤑
┗━━━━━━━━━━━━┛

🎯 𝐋𝐈𝐌𝐈𝐓𝐄𝐃 𝐎𝐅𝐅𝐄𝐑 🔥
⚡ 100% Trusted | Instant Delivery 🚀
💎 Free Fire Likes | Credits 💖

🔗 𝒀𝒐𝒖𝒓 𝑴𝒂𝒈𝒊𝒄 𝑳𝒊𝒏𝒌 👇
{ref_link}

💡 𝙎𝙝𝙖𝙧𝙚 𝙆𝙖𝙧𝙤 𝘼𝙪𝙧 𝙆𝙖𝙢𝙖𝙤! 🚀💵
🎯 Support: @{SUPPORT} 💬

✨ ━━━━━━━━━━━━━━━━ ✨
👇 𝐒𝐡𝐨𝐩𝐩𝐢𝐧𝐠 𝐒𝐭𝐚𝐫𝐭 𝐊𝐚𝐫𝐨 👇
"""
    kb = [
        [InlineKeyboardButton("💳 𝐀𝐝𝐝 𝐁𝐚𝐥𝐚𝐧𝐜𝐞 💰✨", callback_data="add_balance"),
         InlineKeyboardButton("🛒 𝐁𝐮𝐲 𝐂𝐫𝐞𝐝𝐢𝐭𝐬 💎🔥", callback_data="buy")],
        [InlineKeyboardButton("👥 𝐌𝐲 𝐑𝐞𝐟𝐞𝐫𝐫𝐚𝐥𝐬 🙋💸", callback_data="refs"),
         InlineKeyboardButton("📊 𝐌𝐲 𝐒𝐭𝐚𝐭𝐬 ✨📈", callback_data="stats")],
        [InlineKeyboardButton("🆘 𝐒𝐮𝐩𝐩𝐨𝐫𝐭 💬💖", url=f"https://t.me/{SUPPORT}"),
         InlineKeyboardButton("❤️‍🔥 𝐅𝐅 𝐋𝐢𝐤𝐞𝐬 🔥💖", callback_data="likes")],
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
        text = f"""╔════════════════════╗
  💳 𝐙𝐄𝐕𝐑𝐈𝐂 𝐏𝐀𝐘𝐌𝐄𝐍𝐓 💳
╚════════════════════╝

💎 𝐏𝐚𝐲𝐦𝐞𝐧𝐭 𝐌𝐞𝐭𝐡𝐨𝐝 𝐂𝐡𝐨𝐨𝐬𝐞 𝐊𝐚𝐫𝐨 👇

┏━━━━━━━━━━━━━━━━━┓
💜 𝐔𝐏𝐈 - GPay/PhonePe 💸
💛 𝐔𝐒𝐃𝐓 - TRON TRC20 🌐
┗━━━━━━━━━━━━━━━━━┛

⚡ 𝐼𝓃𝓈𝓉𝒶𝓃𝓉 | 100% Safe 🔐
👇 𝐒𝐞𝐥𝐞𝐜𝐭 𝐊𝐚𝐫𝐨 👇
"""
        kb = [
            [InlineKeyboardButton("💜 𝐔𝐏𝐈 𝐏𝐚𝐲𝐦𝐞𝐧𝐭 💳", callback_data="pay_upi"),
             InlineKeyboardButton("💛 𝐔𝐒𝐃𝐓 𝐏𝐚𝐲𝐦𝐞𝐧𝐭 🌐", callback_data="pay_usdt")],
            [InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤 🏠✨", callback_data="back_home")]
        ]
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

    elif q.data=="pay_upi":
        try:
            upi_path = find_qr("upi_qr")
            if upi_path:
                await context.bot.send_photo(q.message.chat_id, photo=open(upi_path,"rb"), caption=f"💜 𝐙𝐄𝐕𝐑𝐈𝐂 𝐔𝐏𝐈 𝐐𝐑 💜\n🆔 {UPI_ID}")
            caption = f"""╔════════════════════╗
  💜 𝐔𝐏𝐈 𝐏𝐀𝐘𝐌𝐄𝐍𝐓 💜
╚════════════════════╝

┏━ 𝐔𝐏𝐈 𝐃𝐞𝐭𝐚𝐢𝐥𝐬 ━┓
🆔 {UPI_ID} 💳
💰 GPay/PhonePe/Paytm 💸
┗━━━━━━━━━━━━┛

📸 𝐔𝐩𝐚𝐫 𝐐𝐑 𝐒𝐜𝐚𝐧 𝐊𝐚𝐫𝐨 👆

╔════════════════════╗
  📸 𝐒𝐂𝐑𝐄𝐄𝐍𝐒𝐇𝐎𝐓 𝐘𝐀𝐇𝐈 𝐁𝐇𝐄𝐉𝐎
╚════════════════════╝
✅ Payment ke baad
📸 𝐈𝐬𝐢 𝐂𝐡𝐚𝐭 𝐌𝐞 Screenshot 𝐁𝐡𝐞𝐣𝐨 👇
🚫 Support pe mat bhejo
⚡ Bot khud detect karega

⚡ Instant Approval ✅
🚀 Fast 💯🔥
"""
            kb = [[InlineKeyboardButton("💛 𝐔𝐒𝐃𝐓 💳", callback_data="pay_usdt"),
                   InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤 🏠", callback_data="add_balance")]]
            await q.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb))
            users = load_users()
            users[str(uid)]["awaiting_screenshot"] = "UPI"
            save_users(users)
        except Exception as e:
            print(e)

    elif q.data=="pay_usdt":
        try:
            usdt_path = find_qr("usdt_qr")
            if usdt_path:
                await context.bot.send_photo(q.message.chat_id, photo=open(usdt_path,"rb"), caption=f"💛 𝐙𝐄𝐕𝐑𝐈𝐂 𝐔𝐒𝐃𝐓 𝐐𝐑 💛\n🔐 {USDT_ADDR}")
            caption = f"""╔════════════════════╗
  💛 𝐔𝐒𝐃𝐓 𝐏𝐀𝐘𝐌𝐄𝐍𝐓 💛
╚════════════════════╝

┏━ 𝐔𝐒𝐃𝐓 𝐃𝐞𝐭𝐚𝐢𝐥𝐬 ━┓
🔐 {USDT_ADDR} 🔐
🌐 TRON (TRC20) Only ⚡
┗━━━━━━━━━━━━┛

📸 𝐔𝐩𝐚𝐫 𝐐𝐑 𝐒𝐜𝐚𝐧 𝐊𝐚𝐫𝐨 👆

╔════════════════════╗
  📸 𝐒𝐂𝐑𝐄𝐄𝐍𝐒𝐇𝐎𝐓 + TxID 𝐘𝐀𝐇𝐈
╚════════════════════╝
✅ Payment ke baad
📸 𝐈𝐬𝐢 𝐂𝐡𝐚𝐭 𝐌𝐞 Bhejo 👇
🚫 Support pe mat bhejo
⚡ Bot khud detect karega

⚡ Instant Approval ✅
🚀 Fast 💯🔥
"""
            kb = [[InlineKeyboardButton("💜 𝐔𝐏𝐈 💳", callback_data="pay_upi"),
                   InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤 🏠", callback_data="add_balance")]]
            await q.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb))
            users = load_users()
            users[str(uid)]["awaiting_screenshot"] = "USDT"
            save_users(users)
        except Exception as e:
            print(e)

    elif q.data.startswith("approve_"):
        pid = q.data.replace("approve_","")
        pending = load_pending()
        if pid in pending:
            data = pending[pid]
            user_id = data["user_id"]
            method = data["method"]
            users = load_users()
            if str(user_id) in users:
                users[str(user_id)]["balance"] += 100.0
                save_users(users)
            pending[pid]["status"] = "approved"
            save_pending(pending)
            await q.message.reply_text(f"✅ Approved {pid} | User {user_id} | {method} | +₹100")
            try:
                await context.bot.send_message(user_id, f"✅✨ 𝐏𝐚𝐲𝐦𝐞𝐧𝐭 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝! ✨✅\n💰 ₹100 Added 💵\n💖 Thanks! 🔥")
            except: pass
        else:
            await q.message.reply_text("❌ Not found")

    elif q.data.startswith("cancel_"):
        pid = q.data.replace("cancel_","")
        pending = load_pending()
        if pid in pending:
            user_id = pending[pid]["user_id"]
            pending[pid]["status"] = "cancelled"
            save_pending(pending)
            await q.message.reply_text(f"❌ Cancelled {pid}")
            try:
                await context.bot.send_message(user_id, f"❌ 𝐏𝐚𝐲𝐦𝐞𝐧𝐭 𝐂𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝 😥\n📞 Contact @{SUPPORT}")
            except: pass

    elif q.data=="back_home" or q.data=="back_menu":
        await start(q, context)

    elif q.data=="buy":
        await q.message.reply_text("🛒 Buy ke liye Support pe aao")
    elif q.data=="refs":
        await q.message.reply_text(f"👥 Refs: {user['referrals']} | ₹{user['referrals']*0.1:.2f}\n🔗 {ref_link}")
    elif q.data=="stats":
        await q.message.reply_text(f"📊 {name} | ₹{user['balance']:.2f} | {user['referrals']} refs")
    elif q.data=="likes":
        users = load_users()
        users[str(uid)]["awaiting_uid"] = True
        save_users(users)
        await q.message.reply_text("❤️‍🔥 UID Bhejo")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users = load_users()
    if users.get(str(uid), {}).get("awaiting_uid"):
        ff_uid = ''.join(filter(str.isdigit, update.message.text))
        await update.message.reply_text(f"✅ Likes Sent to {ff_uid}!")
        users[str(uid)]["awaiting_uid"] = False
        save_users(users)
    else:
        # If awaiting screenshot but sent text, remind
        if users.get(str(uid), {}).get("awaiting_screenshot"):
            await update.message.reply_text("📸 Please screenshot bhejo photo ke roop me, text nahi! 👆")
        else:
            await update.message.reply_text(f"👋 Hey {update.effective_user.first_name}! /start")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users = load_users()
    awaiting = users.get(str(uid), {}).get("awaiting_screenshot")
    if awaiting:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        pid = f"{uid}_{int(time.time())}"
        pending = load_pending()
        pending[pid] = {
            "user_id": uid,
            "username": update.effective_user.username,
            "name": update.effective_user.first_name,
            "method": awaiting,
            "file_id": file_id,
            "status": "pending",
            "time": int(time.time())
        }
        save_pending(pending)
        users[str(uid)]["awaiting_screenshot"] = None
        save_users(users)
        await update.message.reply_text(f"""✅✨ 𝐒𝐜𝐫𝐞𝐞𝐧𝐬𝐡𝐨𝐭 𝐑𝐞𝐜𝐞𝐢𝐯𝐞𝐝! ✨✅
━━━━━━━━━━━━━━━━━
💜 Method: {awaiting}
⏳ Admin check karega
⚡ Jaldi approve hoga

💖 ZEVRIC Thanks!
""")
        admins = get_admins()
        if not admins:
            print("No ADMIN_IDS set, cannot alert admin")
        for admin_id in admins:
            try:
                kb = [
                    [InlineKeyboardButton(f"✅ Approve +₹100", callback_data=f"approve_{pid}"),
                     InlineKeyboardButton(f"❌ Cancel", callback_data=f"cancel_{pid}")],
                ]
                await context.bot.send_photo(
                    admin_id,
                    photo=file_id,
                    caption=f"🚨 𝐍𝐞𝐰 𝐏𝐚𝐲𝐦𝐞𝐧𝐭 🚨\n👤 {update.effective_user.first_name} (@{update.effective_user.username})\n🆔 {uid}\n💰 {awaiting}\nPID: {pid}",
                    reply_markup=InlineKeyboardMarkup(kb)
                )
            except Exception as e:
                print(f"Admin alert error {admin_id}: {e}")
    else:
        await update.message.reply_text("📸 Pehle UPI/USDT select karo, fir screenshot bhejo! /start")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆘 Support: @{SUPPORT}")

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
            await asyncio.Event().wait()
        except Exception as e:
            print(f"Crash: {e}")
            await asyncio.sleep(5)

if __name__=="__main__":
    asyncio.run(main())
