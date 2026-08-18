import os, asyncio, json, logging, threading, re, uuid
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS", "")
SUPPORT = "just_zevric"
UPI_ID = "zervicxplay@okhdfcbank"
USDT_ADDR = "TLwAWcJ7Tm34jqyYqV6qhizQHy8pe7US1v"

logging.basicConfig(level=logging.INFO)

# 24/7 Keep Alive
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "👑 ZEVRIC 24/7 LIVE WITH PAYMENT APPROVAL ✅"
def run_flask():
    port = int(os.getenv("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_flask, daemon=True).start()

def load_json(f, default):
    try:
        with open(f,"r") as fp: return json.load(fp)
    except: return default
def save_json(f, d):
    with open(f,"w") as fp: json.dump(fp,d)

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

def is_admin(uid): return str(uid) in ADMIN_IDS.split(",")

def main_menu_text(name, balance, ref_link):
    return f"""
╔══════════════════════════════╗
║  👑 ZEVRIC GLORY STORE 👑   ║
║   ⚡ ELITE EDITION ⚡        ║
╚══════════════════════════════╝

👋 Hello, Boss {name}! 💫
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 ┣ Wallet: ₹{balance:.2f}
🔗 ┣ Referral Link:
`{ref_link}`

💡 ┗ Earn ₹1.00 per Referral! 🎁
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ Support: @{SUPPORT} | 🟢 24/7 Online ✅
"""

def main_keyboard():
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
    # save name
    u = get_user(uid)
    u['name']=name
    users[str(uid)]=u
    save_users(users)
    
    if context.args:
        for k,v in users.items():
            if v.get("ref_code")==context.args[0] and k!=str(uid):
                users[k]["balance"]+=1.0
                users[k]["referrals"]+=1
                save_users(users)
                try:
                    await context.bot.send_message(int(k), f"🎉 New Referral! 👥\n💰 You got ₹1.00 from {name}")
                except: pass
                break
    user = get_user(uid)
    me = await context.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"
    await update.message.reply_text(main_menu_text(name, user['balance'], ref_link), reply_markup=main_keyboard(), parse_mode="Markdown")

async def btn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = q.data
    user = get_user(uid)
    me = await context.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"

    # --- ADMIN APPROVAL ---
    if data.startswith("approve_") or data.startswith("cancel_"):
        if not is_admin(uid):
            await q.message.reply_text("❌ Only Admin can do this!")
            return
        pid = data.split("_",1)[1]
        pending = load_pending()
        if pid not in pending:
            await q.message.reply_text("❌ Payment already processed or not found.")
            return
        p = pending[pid]
        users = load_users()
        target_id = p['user_id']
        amount = p['amount']
        
        if data.startswith("approve_"):
            # add balance
            if str(target_id) not in users:
                users[str(target_id)] = {"balance":0.0,"referrals":0,"ref_code":str(target_id)[-6:]}
            users[str(target_id)]['balance']+=amount
            save_users(users)
            pending[pid]['status']="approved"
            save_pending(pending)
            await q.message.edit_text(f"✅ APPROVED ✅\n👤 User: {p['user_name']} ({target_id})\n💰 Amount: ₹{amount}\n🔖 UTR: {p['utr']}\nApproved by Admin")
            try:
                await context.bot.send_message(target_id, f"✅ Payment Approved! 💳\n💰 ₹{amount} added to your wallet!\n💵 New Balance: ₹{users[str(target_id)]['balance']:.2f}\n\n/start dabao 👑", reply_markup=main_keyboard())
            except: pass
        else:
            pending[pid]['status']="cancelled"
            save_pending(pending)
            await q.message.edit_text(f"❌ CANCELLED ❌\n👤 User: {p['user_name']} ({target_id})\n💰 Amount: ₹{amount}\n🔖 UTR: {p['utr']}\nCancelled by Admin")
            try:
                await context.bot.send_message(target_id, f"❌ Payment Cancelled by Admin\n🔖 UTR: {p['utr']}\n📞 Contact @{SUPPORT} for help.")
            except: pass
        return

    if data=="add_balance":
        txt = f"""
╔════════════════════════════╗
║ 💳 ZEVRIC PAYMENT CENTER 💳 ║
╚════════════════════════════╝

💰 Your Balance: ₹{user['balance']:.2f}
━━━━━━━━━━━━━━━━━━━━━━━
✨ *UPI PAYMENT* ✨
🏦 ID: `{UPI_ID}`

✨ *USDT TRON* ✨
📬 `{USDT_ADDR}`

👇 QR bhej raha hu, scan karo!
"""
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ I Paid / Submit UTR", callback_data="submit_utr")],
            [InlineKeyboardButton("❌ Cancel", callback_data="main_menu")],
        ])
        await q.message.reply_text(txt, reply_markup=kb, parse_mode="Markdown")
        base = os.path.dirname(__file__)
        try:
            await context.bot.send_photo(q.message.chat_id, photo=open(os.path.join(base,"upi_qr.jpg"),"rb"), caption=f"💳 UPI QR 👑\n🆔 {UPI_ID}")
        except: pass
        try:
            await context.bot.send_photo(q.message.chat_id, photo=open(os.path.join(base,"usdt_qr.jpg"),"rb"), caption=f"💎 USDT TRON QR\n📬 {USDT_ADDR}")
        except: pass

    elif data=="submit_utr":
        context.user_data['awaiting_utr']=True
        txt = f"""
📝 *SUBMIT PAYMENT PROOF*

Format me bhejo:
`UTR Amount`

Example:
`123456789012 30` (UPI)
`abcd1234 10` (USDT - last 8 chars)

💡 UTR kaha milega?
UPI: GPay/PhonePe me 12 digit UTR
USDT: Transaction ID ka last 8 digit

❌ Cancel karne ke liye /start likho
"""
        await q.message.reply_text(txt, parse_mode="Markdown")

    elif data=="buy_credits":
        txt = f"🎫 *BUY CREDITS* - Balance ₹{user['balance']:.2f}\n❤️‍🔥 Likes | 🏆 Glory - @{SUPPORT} pe order karo"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])
        await q.message.reply_text(txt, reply_markup=kb, parse_mode="Markdown")

    elif data=="my_refs":
        txt = f"👥 Referrals: {user['referrals']} | Earned ₹{user['referrals']*1.0:.2f}\n🔗 {ref_link}"
        await q.message.reply_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]))

    elif data=="my_stats":
        txt = f"📊 Stats\n💳 Balance ₹{user['balance']:.2f}\n👥 Refs {user['referrals']}"
        await q.message.reply_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]))

    elif data=="ff_likes":
        await q.message.reply_text("❤️‍🔥 UID bhejo, Support handle karega", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]))
    elif data=="guild_glory":
        await q.message.reply_text("🏆 Guild ID bhejo, Support handle karega", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]))
    elif data=="main_menu":
        text = main_menu_text(q.from_user.first_name, user['balance'], ref_link)
        await q.message.reply_text(text, reply_markup=main_keyboard(), parse_mode="Markdown")

async def handle_utr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_utr'):
        return
    text = update.message.text.strip()
    uid = update.effective_user.id
    name = update.effective_user.first_name
    
    # parse UTR and amount
    parts = text.split()
    if len(parts)<2:
        await update.message.reply_text("❌ Galat format! Example: `123456789012 30`", parse_mode="Markdown")
        return
    utr = parts[0]
    try:
        amount = float(parts[1])
    except:
        await update.message.reply_text("❌ Amount sahi likho! Example: 30")
        return
    
    if len(utr)<6:
        await update.message.reply_text("❌ UTR kam se kam 6 digit ka hona chahiye!")
        return

    pid = str(uuid.uuid4())[:8]
    pending = load_pending()
    pending[pid] = {"user_id":uid, "user_name":name, "utr":utr, "amount":amount, "status":"pending"}
    save_pending(pending)
    context.user_data['awaiting_utr']=False

    await update.message.reply_text(f"✅ Request Sent! ⏳\n🔖 UTR: {utr}\n💰 Amount: ₹{amount}\n\nAdmin approve karega, 2-5 min wait karo.\n📞 Support: @{SUPPORT}", reply_markup=main_keyboard())

    # send to admin
    for admin_id in ADMIN_IDS.split(","):
        if not admin_id.strip(): continue
        try:
            admin_text = f"""
🔔 NEW PAYMENT REQUEST 🔔
━━━━━━━━━━━━━━━
👤 User: {name} ({uid})
💰 Amount: ₹{amount}
🔖 UTR: `{utr}`
🆔 PID: {pid}
⏰ Pending ⏳

Approve karo ya Cancel?
"""
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{pid}"),
                 InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{pid}")]
            ])
            await context.bot.send_message(int(admin_id), admin_text, reply_markup=kb, parse_mode="Markdown")
        except Exception as e:
            print(f"Admin send fail {admin_id}: {e}")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    pending = load_pending()
    count = len([p for p in pending.values() if p['status']=='pending'])
    await update.message.reply_text(f"👑 ADMIN PANEL 👑\n⏳ Pending Payments: {count}\n📊 Total Users: {len(load_users())}\n\nPending dekhne ke liye /pending")

async def pending_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    pending = load_pending()
    for pid,p in pending.items():
        if p['status']!='pending': continue
        txt = f"⏳ {p['user_name']} ({p['user_id']}) - ₹{p['amount']} - UTR {p['utr']} - PID {pid}"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve", callback_data=f"approve_{pid}"), InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{pid}")]])
        await update.message.reply_text(txt, reply_markup=kb)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Support @{SUPPORT} | UPI {UPI_ID} | USDT {USDT_ADDR}")

async def main():
    while True:
        try:
            app = Application.builder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help_cmd))
            app.add_handler(CommandHandler("support", help_cmd))
            app.add_handler(CommandHandler("admin", admin_panel))
            app.add_handler(CommandHandler("pending", pending_cmd))
            app.add_handler(CallbackQueryHandler(btn_handler))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_utr))
            print("👑 ZEVRIC FINAL BOT WITH APPROVAL Starting...")
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print("✅ LIVE 24/7 WITH ADMIN APPROVAL")
            await asyncio.Event().wait()
        except Exception as e:
            print(f"Crash {e}, restart in 5 sec")
            await asyncio.sleep(5)

if __name__=="__main__":
    asyncio.run(main())
