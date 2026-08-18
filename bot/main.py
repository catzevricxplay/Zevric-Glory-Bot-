import os, asyncio, json, logging, threading, uuid
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS", "")
SUPPORT = "just_zevric"
UPI_ID = "zervicxplay@okhdfcbank"
USDT_ADDR = "TLwAWcJ7Tm34jqyYqV6qhizQHy8pe7US1v"

logging.basicConfig(level=logging.INFO)

# --- 24/7 Keep Alive (safe) ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "👑 ZEVRIC 24/7 LIVE ✅"

def run_flask():
    try:
        port = int(os.getenv("PORT", 10000))
        flask_app.run(host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Flask error (ignore if BG worker): {e}")

threading.Thread(target=run_flask, daemon=True).start()

# --- SAFE JSON ---
def load_json(file, default):
    try:
        with open(file,"r") as f: return json.load(f)
    except: return default

def save_json(file, data):
    try:
        with open(file,"w") as f: json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Save error {file}: {e}")

def load_users(): return load_json("users.json", {})
def save_users(d): save_json("users.json", d)
def load_pending(): return load_json("pending.json", {})
def save_pending(d): save_json("pending.json", d)

def get_user(uid):
    users = load_users()
    if str(uid) not in users:
        users[str(uid)] = {"balance":0.0,"referrals":0,"ref_code":str(uid)[-6:], "name":""}
        save_users(users)
    return users[str(uid)]

def is_admin(uid): return str(uid) in ADMIN_IDS.split(",") if ADMIN_IDS else False

def main_text(name, balance, ref_link):
    return f"""
╔══════════════════════════════╗
║  👑 ZEVRIC GLORY STORE 👑   ║
║   ⚡ ELITE EDITION ⚡        ║
╚══════════════════════════════╝

👋 Hello, Boss *{name}*! 💫
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 Wallet: ₹{balance:.2f}
🔗 Referral:
`{ref_link}`

💡 1 Referral = ₹1.00 🎁
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ Support: @{SUPPORT} | 🟢 24/7 Online ✅
"""

def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Add Balance", callback_data="add_balance"),
         InlineKeyboardButton("🎫 Buy Credits", callback_data="buy_credits")],
        [InlineKeyboardButton("👥 My Referrals", callback_data="my_refs"),
         InlineKeyboardButton("📊 My Stats", callback_data="my_stats")],
        [InlineKeyboardButton("❤️‍🔥 Free Fire Likes", callback_data="ff_likes"),
         InlineKeyboardButton("🏆 Guild Glory", callback_data="guild_glory")],
        [InlineKeyboardButton("📞 Support / Help", url=f"https://t.me/{SUPPORT}")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.first_name
    users = load_users()
    u = get_user(uid)
    u['name']=name
    users[str(uid)]=u
    save_users(users)
    if context.args:
        for k,v in list(users.items()):
            if v.get("ref_code")==context.args[0] and k!=str(uid):
                users[k]["balance"]+=1.0
                users[k]["referrals"]+=1
                save_users(users)
                break
    user = get_user(uid)
    me = await context.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"
    await update.message.reply_text(main_text(name, user['balance'], ref_link), reply_markup=main_kb(), parse_mode="Markdown")

async def btn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = q.data
    user = get_user(uid)
    me = await context.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"

    # ADMIN APPROVE/CANCEL
    if data.startswith("approve_") or data.startswith("cancel_"):
        if not is_admin(uid):
            await q.message.reply_text("❌ Only Admin!")
            return
        pid = data.split("_",1)[1]
        pending = load_pending()
        if pid not in pending:
            await q.message.edit_text("❌ Already processed!")
            return
        p = pending[pid]
        users = load_users()
        tid = p['user_id']
        amt = p['amount']
        if data.startswith("approve_"):
            if str(tid) not in users: users[str(tid)]={"balance":0.0,"referrals":0,"ref_code":str(tid)[-6:],"name":p['user_name']}
            users[str(tid)]['balance']+=amt
            save_users(users)
            pending[pid]['status']="approved"
            save_pending(pending)
            await q.message.edit_text(f"✅ APPROVED ✅\n👤 {p['user_name']} ({tid})\n💰 ₹{amt}\n🔖 {p['utr']}")
            try: await context.bot.send_message(tid, f"✅ Payment Approved! 💳\n💰 ₹{amt} added!\n💵 New Balance: ₹{users[str(tid)]['balance']:.2f}\n\n/start 👑", reply_markup=main_kb())
            except: pass
        else:
            pending[pid]['status']="cancelled"
            save_pending(pending)
            await q.message.edit_text(f"❌ CANCELLED ❌\n👤 {p['user_name']} ({tid})\n💰 ₹{amt}\n🔖 {p['utr']}")
            try: await context.bot.send_message(tid, f"❌ Payment Cancelled ❌\n🔖 UTR: {p['utr']}\n📞 Contact @{SUPPORT}")
            except: pass
        return

    if data=="add_balance":
        txt = f"""
💳 *ZEVRIC PAYMENT CENTER* 💳
━━━━━━━━━━━━━━━
💰 Balance: ₹{user['balance']:.2f}

✨ UPI ID:
`{UPI_ID}`

✨ USDT TRON:
`{USDT_ADDR}`

👇 QR bhej raha hu!
"""
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ I Paid / Submit UTR", callback_data="submit_utr")],
            [InlineKeyboardButton("❌ Cancel", callback_data="main_menu")],
        ])
        await q.message.reply_text(txt, reply_markup=kb, parse_mode="Markdown")
        base = os.path.dirname(__file__)
        try:
            upi_path = os.path.join(base,"upi_qr.jpg")
            if os.path.exists(upi_path):
                await context.bot.send_photo(q.message.chat_id, photo=open(upi_path,"rb"), caption=f"💳 UPI QR 👑 {UPI_ID}")
            else:
                await q.message.reply_text(f"📸 UPI QR yaha hai, ID: {UPI_ID}")
        except Exception as e: print(e)
        try:
            usdt_path = os.path.join(base,"usdt_qr.jpg")
            if os.path.exists(usdt_path):
                await context.bot.send_photo(q.message.chat_id, photo=open(usdt_path,"rb"), caption=f"💎 USDT QR {USDT_ADDR}")
        except Exception as e: print(e)

    elif data=="submit_utr":
        context.user_data['awaiting_utr']=True
        await q.message.reply_text("📝 *UTR + Amount bhejo*\nExample: `123456789012 30`\n\n❌ Cancel ke liye /start", parse_mode="Markdown")

    elif data=="main_menu":
        await q.message.reply_text(main_text(q.from_user.first_name, user['balance'], ref_link), reply_markup=main_kb(), parse_mode="Markdown")
    elif data=="my_refs":
        await q.message.reply_text(f"👥 Referrals: {user['referrals']} | Earned ₹{user['referrals']}\n🔗 {ref_link}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]]))
    elif data=="my_stats":
        await q.message.reply_text(f"📊 Balance ₹{user['balance']:.2f} | Refs {user['referrals']}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]]))
    elif data=="buy_credits":
        await q.message.reply_text(f"🎫 Buy Credits - Balance ₹{user['balance']:.2f} - Contact @{SUPPORT}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]]))
    else:
        await q.message.reply_text(f"Contact @{SUPPORT}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu", callback_data="main_menu")]]))

async def handle_utr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_utr'): return
    txt = update.message.text.strip()
    parts = txt.split()
    if len(parts)<2:
        await update.message.reply_text("❌ Format: `UTR Amount` jaise `123456789012 30`", parse_mode="Markdown"); return
    utr=parts[0]
    try: amt=float(parts[1])
    except: await update.message.reply_text("❌ Amount sahi likho"); return
    if len(utr)<6: await update.message.reply_text("❌ UTR 6 digit se bada hona chahiye"); return

    pid=str(uuid.uuid4())[:8]
    pending=load_pending()
    pending[pid]={"user_id":update.effective_user.id,"user_name":update.effective_user.first_name,"utr":utr,"amount":amt,"status":"pending"}
    save_pending(pending)
    context.user_data['awaiting_utr']=False
    await update.message.reply_text(f"✅ Request Sent ⏳\n🔖 {utr}\n💰 ₹{amt}\nAdmin approve karega...", reply_markup=main_kb())
    for aid in ADMIN_IDS.split(","):
        if not aid.strip(): continue
        try:
            atxt=f"🔔 NEW PAYMENT 🔔\n👤 {update.effective_user.first_name} ({update.effective_user.id})\n💰 ₹{amt}\n🔖 `{utr}`\n🆔 {pid}"
            kb=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve", callback_data=f"approve_{pid}"), InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{pid}")]])
            await context.bot.send_message(int(aid), atxt, reply_markup=kb, parse_mode="Markdown")
        except Exception as e: print(e)

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    pending=load_pending()
    cnt=len([p for p in pending.values() if p['status']=='pending'])
    await update.message.reply_text(f"👑 ADMIN\n⏳ Pending: {cnt}\n👥 Users: {len(load_users())}\n/pending se list dekho")

async def pending_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    pending=load_pending()
    for pid,p in pending.items():
        if p['status']!='pending': continue
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve", callback_data=f"approve_{pid}"), InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{pid}")]])
        await update.message.reply_text(f"⏳ {p['user_name']} {p['user_id']} ₹{p['amount']} UTR {p['utr']} PID {pid}", reply_markup=kb)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Support @{SUPPORT} | UPI {UPI_ID}")

async def main():
    while True:
        try:
            if not TOKEN:
                print("❌ TELEGRAM_TOKEN missing in Env!")
                await asyncio.sleep(10); continue
            app = Application.builder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help_cmd))
            app.add_handler(CommandHandler("support", help_cmd))
            app.add_handler(CommandHandler("admin", admin_cmd))
            app.add_handler(CommandHandler("pending", pending_cmd))
            app.add_handler(CallbackQueryHandler(btn_handler))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_utr))
            print("👑 ZEVRIC FIXED BOT Starting...")
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print("✅ BOT LIVE - All Options Working")
            await asyncio.Event().wait()
        except Exception as e:
            print(f"Crash: {e}")
            await asyncio.sleep(5)

if __name__=="__main__":
    asyncio.run(main())
