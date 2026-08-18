import os, asyncio, json, logging, threading, time
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPPORT = "just_zevric"
UPI_ID = "zervicxplay@okhdfcbank"
USDT_ADDR = "TLwAWcJ7Tm34jqyYqV6qhizQHy8pe7US1v"
ADMIN_IDS = os.getenv("ADMIN_IDS", "")
CREDIT_PRICE_INR = 95
USDT_RATE = 95.78

logging.basicConfig(level=logging.INFO)
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "🔥 ZEVRIC - FANCY MAST TEXT STYLE - FINAL ✅"
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
        users[str(uid)] = {"balance":0.0,"credits":0,"referrals":0,"ref_code":str(uid)[-6:],"awaiting_screenshot":None,"awaiting_utr":False,"selected_package":None,"history":[]}
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

def calc_usdt(inr):
    return round(inr / USDT_RATE, 2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.first_name
    users = load_users()
    if context.args:
        for k,v in users.items():
            if v.get("ref_code")==context.args[0] and k!=str(uid):
                users[k]["balance"]+=0.1
                users[k]["referrals"]+=1
                if "history" not in users[k]:
                    users[k]["history"]=[]
                users[k]["history"].append(f"Referral bonus +₹0.1 from {name}")
                save_users(users)
                break
    user = get_user(uid)
    me = await context.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"
    # FANCY MAST TEXT STYLE - Jo dekh ke kharidne ka man kare
    text = f"""✨ ━━━━━━━━━━━━━━━━ ✨
  🎮 𝐙𝐄𝐕𝐑𝐈𝐂 𝐆𝐔𝐈𝐋𝐃 𝐆𝐋𝐎𝐑𝐘 𝐁𝐎𝐓 🎮
✨ ━━━━━━━━━━━━━━━━ ✨

👋 𝐇𝐞𝐲, {name}! 😎💫
🌟 𝒲𝑒𝓁𝒸𝑜𝓂𝑒 𝓉𝑜 𝒵𝑒𝓋𝓇𝒾𝒸 𝒮𝓉𝑜𝓇𝑒 💖

┏━ 𝐆𝐔𝐈𝐋𝐃 𝐆𝐋𝐎𝐑𝐘 𝐁𝐎𝐓 ━┓
🏆 Guild Glory Boost 🔥
⚡ 100% Working | 24/7 🚀
💎 Fast & Secure 💫
🎯 Trusted by 1000+ Guilds 🙋
┗━━━━━━━━━━━━┛

┏━ 𝙔𝙊𝙐𝙍 𝙒𝘼𝙇𝙇𝙀𝙏 ━┓
💰 ₹{user['balance']:.2f} 💵
🎫 {user.get('credits',0)} Credits 🪙
💸 𝑬𝒂𝒓𝒏 ₹0.10 𝑝𝑒𝓇 𝑅𝑒𝒻𝑒𝓇 🤑
┗━━━━━━━━━━━━┛

🔗 𝒀𝒐𝒖𝒓 𝑹𝒆𝒇𝒆𝒓𝒓𝒂𝒍 𝑳𝒊𝒏𝒌 👇
{ref_link}

💡 𝐁𝐨𝐭 𝐊𝐡𝐚𝐫𝐢𝐝𝐨 𝐀𝐮𝐫 𝐆𝐮𝐢𝐥𝐝 𝐆𝐥𝐨𝐫𝐲 𝐁𝐚𝐝𝐡𝐚𝐨! 🚀🏆
🎯 @{SUPPORT} 💬
✨ ━━━━━━━━━━━━━━━━ ✨
"""
    kb = [
        [InlineKeyboardButton("💳 𝐀𝐝𝐝 𝐁𝐚𝐥𝐚𝐧𝐜𝐞 💰", callback_data="add_balance"),
         InlineKeyboardButton("🎫 𝐁𝐮𝐲 𝐂𝐫𝐞𝐝𝐢𝐭𝐬 🏆", callback_data="buy_credits")],
        [InlineKeyboardButton("👥 𝐌𝐲 𝐑𝐞𝐟𝐞𝐫𝐫𝐚𝐥𝐬 🙋", callback_data="refs"),
         InlineKeyboardButton("📊 𝐌𝐲 𝐒𝐭𝐚𝐭𝐬 ✨", callback_data="stats")],
        [InlineKeyboardButton("🕐 𝐇𝐢𝐬𝐭𝐨𝐫𝐲 📜", callback_data="history"),
         InlineKeyboardButton("📋 𝐂𝐫𝐞𝐝𝐢𝐭 𝐏𝐥𝐚𝐧𝐬 💎", callback_data="credit_plans")],
        [InlineKeyboardButton("🆘 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐀𝐝𝐦𝐢𝐧 💬", url=f"https://t.me/{SUPPORT}")]
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
💜 UPI - GPay/PhonePe/Paytm
💛 USDT - TRON TRC20 Only
━━━━━━━━━━━━━━
"""
        kb = [[InlineKeyboardButton("💜 𝐔𝐏𝐈 💳", callback_data="pay_upi"),
               InlineKeyboardButton("💛 𝐔𝐒𝐃𝐓 🌐", callback_data="pay_usdt")],
              [InlineKeyboardButton("🎫 𝐁𝐮𝐲 𝐂𝐫𝐞𝐝𝐢𝐭𝐬 🏆", callback_data="buy_credits"),
               InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤 🏠", callback_data="back_home")]]
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

    elif q.data=="buy_credits" or q.data=="credit_plans":
        bal = user['balance']
        text = f"""✨ ━━━━━━━━━━━━━━━━ ✨
  🎫 𝐁𝐔𝐘 𝐂𝐑𝐄𝐃𝐈𝐓𝐒 🎫
✨ ━━━━━━━━━━━━━━━━ ✨

💰 𝒀𝒐𝒖𝒓 𝑩𝒂𝒍𝒂𝒏𝒄𝒆: ₹{bal:.2f} 💵
💎 𝐃𝐞𝐟𝐚𝐮𝐥𝐭: 1 Credit = ₹{CREDIT_PRICE_INR} 🪙
💱 1 USDT ≈ ₹{USDT_RATE} 💹

━━━━━━━━━━━━━━━━━
📦 𝐒𝐞𝐥𝐞𝐜𝐭 𝐏𝐚𝐜𝐤𝐚𝐠𝐞 👇
━━━━━━━━━━━━━━━━━
"""
        kb = []
        for i in range(1,7):
            inr_price = i * CREDIT_PRICE_INR
            usdt_price = calc_usdt(inr_price)
            kb.append([InlineKeyboardButton(f"💎 {i} Credits — ₹{inr_price} (~{usdt_price} USDT) 🔥", callback_data=f"pkg_{i}")])
        kb.append([InlineKeyboardButton("💳 𝐀𝐝𝐝 𝐁𝐚𝐥𝐚𝐧𝐜𝐞 💰", callback_data="add_balance"),
                   InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤 🏠", callback_data="back_home")])
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

    elif q.data.startswith("pkg_"):
        try:
            pkg = int(q.data.split("_")[1])
            inr_price = pkg * CREDIT_PRICE_INR
            usdt_price = calc_usdt(inr_price)
            users = load_users()
            user = get_user(uid)
            if user['balance'] >= inr_price:
                users[str(uid)]['balance'] -= inr_price
                users[str(uid)]['credits'] = users[str(uid)].get('credits',0) + pkg
                if "history" not in users[str(uid)]:
                    users[str(uid)]["history"]=[]
                users[str(uid)]["history"].append(f"Bought {pkg} Credits -₹{inr_price} ({usdt_price} USDT)")
                save_users(users)
                await q.message.reply_text(f"""✨ ━━━━━━━━━━━━━━━━ ✨
✅ 𝐏𝐮𝐫𝐜𝐡𝐚𝐬𝐞𝐝 {pkg} Credits! 🎫
✨ ━━━━━━━━━━━━━━━━ ✨
💰 Deducted: ₹{inr_price} (~{usdt_price} USDT)
🪙 Total Credits: {users[str(uid)]['credits']}
🏆 Glory Boost Ready! 🚀

🎯 @{SUPPORT} 💬
""")
            else:
                need = inr_price - user['balance']
                text = f"""❌ 𝐈𝐧𝐬𝐮𝐟𝐟𝐢𝐜𝐢𝐞𝐧𝐭 𝐁𝐚𝐥𝐚𝐧𝐜𝐞 😥
━━━━━━━━━━━━━━
📦 Package: {pkg} Credits 🪙
💰 Price: ₹{inr_price} (~{usdt_price} USDT)
💵 Your Balance: ₹{user['balance']:.2f}
💸 Need: ₹{need:.2f} more

👇 𝐀𝐝𝐝 𝐁𝐚𝐥𝐚𝐧𝐜𝐞 𝐊𝐚𝐫𝐨 👇
"""
                kb = [[InlineKeyboardButton(f"💜 Pay ₹{inr_price} UPI 💳", callback_data="pay_upi"),
                       InlineKeyboardButton(f"💛 Pay {usdt_price} USDT 🌐", callback_data="pay_usdt")],
                      [InlineKeyboardButton("🔙 𝐁𝐚𝐜𝐤 🏠", callback_data="buy_credits")]]
                await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
                users[str(uid)]['selected_package'] = pkg
                save_users(users)
        except Exception as e:
            print(e)

    elif q.data=="pay_upi":
        upi_path = find_qr("upi_qr")
        users = load_users()
        sel = users.get(str(uid),{}).get('selected_package')
        if sel:
            amt = sel * CREDIT_PRICE_INR
            usdt = calc_usdt(amt)
            amount_line = f"💰 Amount: ₹{amt}.00 (~{usdt} USDT) - {sel} Credits"
        else:
            amount_line = f"💰 Amount: Your Plan Amount"
        caption = f"""📲 Payment Instructions

{amount_line}
📱 UPI ID: {UPI_ID}

1️⃣ Scan the QR code or pay to the UPI ID above
2️⃣ After payment, send a screenshot along with your UTR / Transaction ID

📸 Please send your payment screenshot now:
"""
        kb = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_pay")]]
        if upi_path:
            await context.bot.send_photo(q.message.chat_id, photo=open(upi_path,"rb"), caption=caption, reply_markup=InlineKeyboardMarkup(kb))
        else:
            await q.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb))
        users[str(uid)]["awaiting_screenshot"] = "UPI"
        users[str(uid)]["awaiting_utr"] = True
        save_users(users)

    elif q.data=="pay_usdt":
        usdt_path = find_qr("usdt_qr")
        users = load_users()
        sel = users.get(str(uid),{}).get('selected_package')
        if sel:
            amt = sel * CREDIT_PRICE_INR
            usdt = calc_usdt(amt)
            amount_line = f"💰 Amount: {usdt} USDT (~₹{amt}) - {sel} Credits"
        else:
            amount_line = f"💰 Amount: Your Plan Amount"
        caption = f"""📲 Payment Instructions

{amount_line}
🔐 USDT Address: {USDT_ADDR}
🌐 Network: TRON (TRC20) Only

1️⃣ Scan the QR code or send to the address above
2️⃣ After payment, send a screenshot along with your TxID

📸 Please send your payment screenshot now:
"""
        kb = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_pay")]]
        if usdt_path:
            await context.bot.send_photo(q.message.chat_id, photo=open(usdt_path,"rb"), caption=caption, reply_markup=InlineKeyboardMarkup(kb))
        else:
            await q.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb))
        users[str(uid)]["awaiting_screenshot"] = "USDT"
        users[str(uid)]["awaiting_utr"] = True
        save_users(users)

    elif q.data=="cancel_pay":
        users = load_users()
        if str(uid) in users:
            users[str(uid)]["awaiting_screenshot"] = None
            users[str(uid)]["awaiting_utr"] = False
            save_users(users)
        await q.message.reply_text("❌ Payment Cancelled\n/start se restart karo 🏠")

    elif q.data=="refs":
        text = f"""✨ ━━━━━━━━━━━━━━━━ ✨
  👥 𝐌𝐘 𝐑𝐄𝐅𝐄𝐑𝐑𝐀𝐋𝐒 🙋
✨ ━━━━━━━━━━━━━━━━ ✨

👥 Total: {user['referrals']} 🙋
💰 Earned: ₹{user['referrals']*0.1:.2f} 💸

🔗 𝒀𝒐𝒖𝒓 𝑳𝒊𝒏𝒌 👇
{ref_link}

💡 𝑺𝒉𝒂𝒓𝒆 𝑲𝒂𝒓𝒐 𝑨𝒖𝒓 𝑲𝒂𝒎𝒂𝒐! 🚀
"""
        await q.message.reply_text(text)

    elif q.data=="stats":
        text = f"""✨ ━━━━━━━━━━━━━━━━ ✨
  📊 𝐌𝐘 𝐒𝐓𝐀𝐓𝐒 ✨
✨ ━━━━━━━━━━━━━━━━ ✨

👤 Name: {name} 😎
💰 Balance: ₹{user['balance']:.2f} 💵
🎫 Credits: {user.get('credits',0)} 🪙
👥 Referrals: {user['referrals']} 🙋
💸 Referral Earn: ₹{user['referrals']*0.1:.2f} 💰
"""
        await q.message.reply_text(text)

    elif q.data=="history":
        hist = user.get('history',[])
        if not hist:
            text = "🕐 𝐇𝐢𝐬𝐭𝐨𝐫𝐲\n━━━━━━━━━━━━━━\nNo history yet! 😅"
        else:
            htxt = "\n".join([f"{i+1}. {h}" for i,h in enumerate(hist[-10:])])
            text = f"🕐 𝐇𝐢𝐬𝐭𝐨𝐫𝐲 (Last 10)\n━━━━━━━━━━━━━━\n{htxt}"
        await q.message.reply_text(text)

    elif q.data.startswith("approve_"):
        pid = q.data.replace("approve_","")
        pending = load_pending()
        if pid in pending:
            user_id = pending[pid]["user_id"]
            amount = pending[pid].get("amount",95)
            users = load_users()
            if str(user_id) in users:
                users[str(user_id)]["balance"] += float(amount)
                if "history" not in users[str(user_id)]:
                    users[str(user_id)]["history"]=[]
                users[str(user_id)]["history"].append(f"Balance Added +₹{amount} via {pending[pid]['method']}")
                save_users(users)
            pending[pid]["status"]="approved"
            save_pending(pending)
            await q.message.reply_text(f"✅ Approved {pid} +₹{amount}")
            try:
                await context.bot.send_message(user_id, f"✅ Payment Submitted!\n\nAmount: ₹{amount}\nUTR: {pending[pid].get('utr','')}\n\n✅ Approved! Balance Added\n💰 Balance: ₹{users[str(user_id)]['balance']:.2f}")
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
                await context.bot.send_message(user_id, f"❌ Payment Cancelled 😥 @{SUPPORT}")
            except: pass
    elif q.data=="back_home":
        await start(q, context)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users = load_users()
    awaiting = users.get(str(uid), {}).get("awaiting_screenshot")
    if awaiting:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        pid = f"{uid}_{int(time.time())}"
        pending = load_pending()
        sel = users.get(str(uid),{}).get('selected_package')
        amt = (sel * CREDIT_PRICE_INR) if sel else CREDIT_PRICE_INR
        pending[pid] = {"user_id": uid, "username": update.effective_user.username, "name": update.effective_user.first_name, "method": awaiting, "file_id": file_id, "amount": amt, "status": "pending", "time": int(time.time())}
        save_pending(pending)
        users[str(uid)]["awaiting_screenshot"] = None
        save_users(users)
        await update.message.reply_text(f"✅ Screenshot Received!\n💰 Method: {awaiting}\n💵 Amount: ₹{amt} (~{calc_usdt(amt)} USDT)\n\n📲 Ab UTR / Transaction ID bhejo 👇")
        for admin_id in get_admins():
            try:
                kb = [[InlineKeyboardButton(f"✅ Approve +₹{amt}", callback_data=f"approve_{pid}"),
                       InlineKeyboardButton(f"❌ Cancel", callback_data=f"cancel_{pid}")]]
                await context.bot.send_photo(admin_id, photo=file_id, caption=f"🚨 New Payment - {awaiting}\n👤 {update.effective_user.first_name} @{update.effective_user.username}\n🆔 {uid}\n💰 ₹{amt} (~{calc_usdt(amt)} USDT)\nPID: {pid}", reply_markup=InlineKeyboardMarkup(kb))
            except: pass
    else:
        await update.message.reply_text("📸 Pehle UPI/USDT select karo! /start")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    users = load_users()
    if users.get(str(uid),{}).get('awaiting_utr'):
        utr = ''.join(filter(str.isalnum, text))
        if len(utr) >= 8:
            pending = load_pending()
            latest_pid = None
            for pid, data in pending.items():
                if str(data.get('user_id'))==str(uid) and data.get('status')=='pending':
                    latest_pid = pid
            if latest_pid:
                pending[latest_pid]['utr']=utr
                save_pending(pending)
            await update.message.reply_text(f"✅ Payment Submitted!\n\nAmount: ₹{users.get(str(uid),{}).get('selected_package',1)*CREDIT_PRICE_INR if users.get(str(uid),{}).get('selected_package') else CREDIT_PRICE_INR}\nUTR: {utr}\n\n⏳ Awaiting admin verification. You'll be notified once approved.")
            users[str(uid)]['awaiting_utr'] = False
            users[str(uid)]['last_utr'] = utr
            save_users(users)
            for admin_id in get_admins():
                try:
                    await context.bot.send_message(admin_id, f"📲 UTR Received\n👤 {update.effective_user.first_name} @{update.effective_user.username}\n🆔 {uid}\nUTR: {utr}\nPID: {latest_pid}")
                except: pass
            return
        else:
            await update.message.reply_text("❌ Valid UTR bhejo 👇")
            return
    if users.get(str(uid), {}).get("awaiting_screenshot"):
        await update.message.reply_text("📸 Photo bhejo! UTR baad me")
    else:
        await update.message.reply_text("👋 /start dabao")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆘 Contact: @{SUPPORT}")

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
            print("✅ BOT LIVE - FANCY MAST TEXT STYLE - ALL COMMANDS NO FF LIKES")
            await asyncio.Event().wait()
        except Exception as e:
            print(e)
            await asyncio.sleep(5)

if __name__=="__main__":
    asyncio.run(main())
