
import os, asyncio, json, logging, threading, time, random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPPORT = "just_zevric"
UPI_ID = "zervicxplay@okhdfcbank"
USDT_ADDR = "TLwAWcJ7Tm34jqyYqV6qhizQHy8pe7US1v"
ADMIN_IDS = os.getenv("ADMIN_IDS", "")
CREDIT_PRICE = 130
USDT_RATE = 95.78

logging.basicConfig(level=logging.INFO)
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "ZEVRIC PROFESSIONAL ₹130 AUTO-DELETE LIVE ✅"
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
        users[str(uid)] = {"balance":0.0,"credits":0,"guild_id":None,"referrals":0,"ref_code":str(uid)[-6:],"awaiting_screenshot":None,"awaiting_utr":False,"awaiting_guild_id":False,"selected_package":None,"orders":[],"history":[],"last_bot_msgs":[]}
        save_users(users)
    # ensure last_bot_msgs exists
    if "last_bot_msgs" not in users[str(uid)]:
        users[str(uid)]["last_bot_msgs"] = []
        save_users(users)
    return users[str(uid)]

def load_pending():
    try:
        with open("pending.json","r") as f: return json.load(f)
    except: return {}
def save_pending(d):
    with open("pending.json","w") as f: json.dump(d,f)
def load_orders():
    try:
        with open("orders.json","r") as f: return json.load(f)
    except: return {}
def save_orders(d):
    with open("orders.json","w") as f: json.dump(d,f)
def get_admins():
    admins=[]
    if ADMIN_IDS:
        for x in ADMIN_IDS.split(","):
            if x.strip().isdigit(): admins.append(int(x.strip()))
    return admins
def find_qr(name):
    for p in [f"bot/{name}.png", f"{name}.png", f"bot/{name}.jpg", f"{name}.jpg"]:
        if os.path.exists(p): return p
    return None
def calc_usdt(inr): return round(inr/USDT_RATE,2)

async def delete_old_messages(context, chat_id, uid):
    """Auto delete previous bot messages when new command comes"""
    try:
        users = load_users()
        user_data = users.get(str(uid), {})
        last_ids = user_data.get('last_bot_msgs', [])
        for mid in last_ids:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=mid)
            except:
                pass
        if str(uid) in users:
            users[str(uid)]['last_bot_msgs'] = []
            save_users(users)
    except:
        pass

async def send_and_track(update_or_q, context, uid, text, reply_markup=None, parse_mode="Markdown", is_photo=False, photo_path=None):
    """Send message and track its ID for auto-delete"""
    try:
        chat_id = uid
        if hasattr(update_or_q, 'message') and update_or_q.message:
            chat_id = update_or_q.message.chat_id
        elif hasattr(update_or_q, 'effective_chat'):
            chat_id = update_or_q.effective_chat.id
        
        # Delete old messages first
        await delete_old_messages(context, chat_id, uid)
        
        # Send new message
        if is_photo and photo_path:
            msg = await context.bot.send_photo(chat_id=chat_id, photo=open(photo_path,"rb"), caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            if hasattr(update_or_q, 'message') and hasattr(update_or_q, 'callback_query'):
                # callback query - send as new message
                msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
            elif hasattr(update_or_q, 'message'):
                msg = await update_or_q.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            else:
                msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
        
        # Track this message ID
        users = load_users()
        if str(uid) not in users:
            users[str(uid)] = {"last_bot_msgs":[]}
        if "last_bot_msgs" not in users[str(uid)]:
            users[str(uid)]["last_bot_msgs"] = []
        users[str(uid)]["last_bot_msgs"].append(msg.message_id)
        # Keep only last 5 messages to avoid too many
        if len(users[str(uid)]["last_bot_msgs"]) > 5:
            users[str(uid)]["last_bot_msgs"] = users[str(uid)]["last_bot_msgs"][-5:]
        save_users(users)
        return msg
    except Exception as e:
        print(f"Send track error: {e}")
        try:
            # Fallback without tracking
            return await context.bot.send_message(chat_id=uid, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
        except:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.first_name
    users = load_users()
    if context.args:
        for k,v in users.items():
            if v.get("ref_code")==context.args[0] and k!=str(uid):
                users[k]["balance"]+=0.1
                users[k]["referrals"]+=1
                if "history" not in users[k]: users[k]["history"]=[]
                users[k]["history"].append(f"Referral +₹0.1 from {name}")
                save_users(users)
                break
    
    # Auto delete old
    await delete_old_messages(context, update.effective_chat.id, uid)
    
    user = get_user(uid)
    me = await context.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"
    
    text = f"""🎮 **ZEVRIC GLORY STORE** 🎮
━━━━━━━━━━━━━━━━━━━━━
👋 Welcome, **{name}**! 😎

💰 Balance: **₹{user['balance']:.2f}** 💵
🎫 Credits: **{user.get('credits',0)}** 🪙
🏰 Guild: **{user.get('guild_id','Not Set ❌')}**

🔥 3.1M+ Players Trusted ✅
⚡ 24/7 Auto Bots 🤖
💎 1 Credit = ₹{CREDIT_PRICE} = 10K-50K Glory 🔥
💵 Profit: ₹{CREDIT_PRICE-95}/credit 💰

🔗 **Referral Link:**
`{ref_link}`
💡 Earn ₹0.1 per referral 🤑
"""
    kb = [
        [InlineKeyboardButton("💰 Add Balance", callback_data="add_balance"),
         InlineKeyboardButton("🎫 Buy Credits", callback_data="buy_credits")],
        [InlineKeyboardButton("🚀 Launch Bot", callback_data="launch_bot"),
         InlineKeyboardButton("🏰 My Guilds", callback_data="my_guilds")],
        [InlineKeyboardButton("👥 Referrals", callback_data="refs"),
         InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("📜 History", callback_data="history"),
         InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT}")]
    ]
    
    msg = await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    users = load_users()
    if str(uid) not in users: users[str(uid)] = {"last_bot_msgs":[]}
    if "last_bot_msgs" not in users[str(uid)]: users[str(uid)]["last_bot_msgs"] = []
    users[str(uid)]["last_bot_msgs"].append(msg.message_id)
    save_users(users)

async def btn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    name = q.from_user.first_name
    chat_id = q.message.chat_id
    users = load_users()
    user = get_user(uid)
    me = await context.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"

    # DELETE OLD MESSAGES ON EVERY NEW BUTTON PRESS
    try:
        # Try to delete the clicked message itself
        await q.message.delete()
    except:
        pass
    await delete_old_messages(context, chat_id, uid)

    if q.data=="add_balance":
        text = f"""💳 **PAYMENT CENTER** 💳
━━━━━━━━━━━━━━━━━━━━━
💰 Balance: ₹{user['balance']:.2f}
💎 1 Credit = ₹{CREDIT_PRICE} 💵

**💜 UPI Payment:**
ID: `{UPI_ID}`
GPay/PhonePe/Paytm ✅

**💛 USDT Payment:**
`{USDT_ADDR}`
Network: TRON (TRC20) Only ⚠️

📸 Screenshot + UTR bhejo
⏰ 2-5 min me add hoga ⚡
"""
        kb = [[InlineKeyboardButton("💜 UPI", callback_data="pay_upi"),
               InlineKeyboardButton("💛 USDT", callback_data="pay_usdt")],
              [InlineKeyboardButton("🎫 Buy Credits", callback_data="buy_credits"),
               InlineKeyboardButton("🏠 Home", callback_data="back_home")]]
        msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

    elif q.data=="buy_credits":
        bal = user['balance']
        text = f"""🎫 **BUY CREDITS - ₹{CREDIT_PRICE}** 🎫
━━━━━━━━━━━━━━━━━━━━━
💰 Balance: ₹{bal:.2f}
💎 1 Credit = ₹{CREDIT_PRICE} = 10K-50K Glory
💵 Profit: ₹{CREDIT_PRICE-95}/credit 💰
🤖 4 Bots per credit
💡 Credit idhar hi rahega 🔒

**Select Package:** 👇
"""
        kb = []
        for i in range(1,7):
            inr_price = i * CREDIT_PRICE
            usdt_price = calc_usdt(inr_price)
            profit = i * (CREDIT_PRICE-95)
            kb.append([InlineKeyboardButton(f"💎 {i} Credit = ₹{inr_price} ({usdt_price} USDT) | {i*10}-{i*50}K Glory | Profit ₹{profit} 🔥", callback_data=f"pkg_{i}")])
        kb.append([InlineKeyboardButton("💰 Add Balance", callback_data="add_balance"),
                   InlineKeyboardButton("🏠 Home", callback_data="back_home")])
        msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

    elif q.data.startswith("pkg_"):
        pkg = int(q.data.split("_")[1])
        inr_price = pkg * CREDIT_PRICE
        usdt_price = calc_usdt(inr_price)
        users = load_users()
        user = get_user(uid)
        if user['balance'] >= inr_price:
            users[str(uid)]['balance'] -= inr_price
            users[str(uid)]['credits'] = users[str(uid)].get('credits',0) + pkg
            if "history" not in users[str(uid)]: users[str(uid)]["history"]=[]
            users[str(uid)]["history"].append(f"Bought {pkg} Credits -₹{inr_price} Profit ₹{pkg*(CREDIT_PRICE-95)}")
            save_users(users)
            txt = f"""✅ **PURCHASE SUCCESSFUL!** 🎉
━━━━━━━━━━━━━━━━━━━━━
🎫 Credits: {pkg}
💰 Deducted: ₹{inr_price} ({usdt_price} USDT)
🪙 Total: {users[str(uid)]['credits']} Credits
🔥 Glory: {pkg*10}-{pkg*50}K
💵 Profit: ₹{pkg*(CREDIT_PRICE-95)}

💡 Credit idhar hi hai 🔒
🚀 Launch Bot dabao!
"""
            msg = await context.bot.send_message(chat_id=chat_id, text=txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Launch Glory Bot", callback_data="launch_bot")]]), parse_mode="Markdown")
            users = load_users()
            users[str(uid)]['last_bot_msgs'] = [msg.message_id]
            save_users(users)
        else:
            need = inr_price - user['balance']
            text = f"""❌ **INSUFFICIENT BALANCE** 😥
━━━━━━━━━━━━━━━━━━━━━
📦 Package: {pkg} Credits = {pkg*10}-{pkg*50}K Glory
💰 Price: ₹{inr_price} ({usdt_price} USDT)
💵 Your Balance: ₹{user['balance']:.2f}
💸 Need: ₹{need:.2f} more

👇 Add Balance Karo 👇
"""
            kb = [[InlineKeyboardButton(f"💜 Pay ₹{inr_price} UPI", callback_data="pay_upi"),
                   InlineKeyboardButton(f"💛 Pay {usdt_price} USDT", callback_data="pay_usdt")],
                  [InlineKeyboardButton("🏠 Home", callback_data="back_home")]]
            msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
            users = load_users()
            users[str(uid)]['selected_package']=pkg
            users[str(uid)]['last_bot_msgs'] = [msg.message_id]
            save_users(users)

    elif q.data=="launch_bot":
        if user.get('credits',0)<1:
            txt = f"""❌ **NO CREDITS!** 😥
━━━━━━━━━━━━━━━━━━━━━
💳 Pehle Credits kharido
💰 ₹{CREDIT_PRICE}/credit = 10K-50K Glory
"""
            msg = await context.bot.send_message(chat_id=chat_id, text=txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎫 Buy Credits", callback_data="buy_credits")]]), parse_mode="Markdown")
            users = load_users()
            users[str(uid)]['last_bot_msgs'] = [msg.message_id]
            save_users(users)
            return
        if not user.get('guild_id'):
            txt = f"""🏰 **GUILD ID REQUIRED!** 🆔
━━━━━━━━━━━━━━━━━━━━━
📋 Pehle Guild ID set karo
🆔 Example: 12345678
"""
            msg = await context.bot.send_message(chat_id=chat_id, text=txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏰 Set Guild ID", callback_data="set_guild_id")]]), parse_mode="Markdown")
            users = load_users()
            users[str(uid)]['last_bot_msgs'] = [msg.message_id]
            save_users(users)
            return
        text = f"""🚀 **LAUNCH GLORY BOT** 🤖
━━━━━━━━━━━━━━━━━━━━━
🏰 Guild: {user.get('guild_id')}
🎫 Credits: {user.get('credits')}
💎 1 Credit = 10K-50K Glory

**Select credits to use:** 👇
"""
        kb = []
        for i in range(1, min(7, user.get('credits',0)+1)):
            kb.append([InlineKeyboardButton(f"🚀 Use {i} Credit = {i*10}-{i*50}K Glory", callback_data=f"launch_{i}")])
        kb.append([InlineKeyboardButton("🏠 Home", callback_data="back_home")])
        msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

    elif q.data.startswith("launch_"):
        use_credits = int(q.data.split("_")[1])
        users = load_users()
        user = get_user(uid)
        if user.get('credits',0) < use_credits:
            msg = await context.bot.send_message(chat_id=chat_id, text="❌ Not enough credits!")
            users[str(uid)]['last_bot_msgs'] = [msg.message_id]
            save_users(users)
            return
        guild_id = user.get('guild_id')
        users[str(uid)]['credits'] -= use_credits
        order_id = f"ORD{uid}{int(time.time())}"
        glory_min = use_credits * 10000
        glory_max = use_credits * 50000
        order = {"order_id": order_id,"guild_id": guild_id,"credits_used": use_credits,"glory_min": glory_min,"glory_max": glory_max,"status": "launching","time": int(time.time()),"bots": 4 * use_credits}
        if "orders" not in users[str(uid)]: users[str(uid)]["orders"] = []
        users[str(uid)]["orders"].append(order)
        if "history" not in users[str(uid)]: users[str(uid)]["history"] = []
        users[str(uid)]["history"].append(f"Launched {use_credits} Credits for Guild {guild_id}")
        save_users(users)
        all_orders = load_orders()
        all_orders[order_id] = {"user_id": uid, "username": q.from_user.username, "name": name, **order}
        save_orders(all_orders)
        txt = f"""✅ **ORDER LAUNCHED!** 🚀
━━━━━━━━━━━━━━━━━━━━━
🆔 Order: {order_id}
🏰 Guild: {guild_id}
💎 Used: {use_credits} Credits
🔥 Glory: {glory_min//1000}-{glory_max//1000}K Expected
🤖 Bots: {4 * use_credits} Bots
⏰ Time: Max 8 Hours
📊 Status: Bots joining...

⚡ Bots start in minutes!
"""
        msg = await context.bot.send_message(chat_id=chat_id, text=txt, parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)
        await asyncio.sleep(2)
        glory_delivered = random.randint(glory_min, glory_max)
        users = load_users()
        all_orders = load_orders()
        if order_id in all_orders:
            all_orders[order_id]["status"] = "completed"
            all_orders[order_id]["glory_delivered"] = glory_delivered
            save_orders(all_orders)
        for o in users.get(str(uid),{}).get("orders",[]):
            if o["order_id"]==order_id:
                o["status"]="completed"
                o["glory_delivered"]=glory_delivered
        # Clear old and send new
        await delete_old_messages(context, chat_id, uid)
        txt2 = f"""🎉 **GLORY DELIVERED!** 🔥
━━━━━━━━━━━━━━━━━━━━━
🆔 Order: {order_id}
🏰 Guild: {guild_id}
🔥 Glory: **{glory_delivered}** points!
🤖 Bots left guild ✅
💰 Credits left: {users[str(uid)]['credits']}
💵 Profit: ₹{use_credits*(CREDIT_PRICE-95)}
"""
        msg2 = await context.bot.send_message(chat_id=chat_id, text=txt2, parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg2.message_id]
        save_users(users)

    elif q.data=="set_guild_id":
        users = load_users()
        users[str(uid)]['awaiting_guild_id']=True
        save_users(users)
        txt = f"""🏰 **SET GUILD ID** 🆔
━━━━━━━━━━━━━━━━━━━━━
📋 Apna Guild ID bhejo
🆔 Example: 12345678
"""
        msg = await context.bot.send_message(chat_id=chat_id, text=txt, parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

    elif q.data=="my_guilds":
        guild_id = user.get('guild_id')
        orders = user.get('orders', [])
        if not guild_id and not orders:
            txt = f"""🏰 **NO GUILDS YET!** 😅
━━━━━━━━━━━━━━━━━━━━━
Set Guild ID first! 🏰
"""
        else:
            txt = f"""🏰 **MY GUILDS & ORDERS** 📋
━━━━━━━━━━━━━━━━━━━━━
🏰 Current: {guild_id if guild_id else 'Not Set ❌'}

📋 Recent Orders:
"""
            if orders:
                for o in orders[-5:]:
                    status_emoji = "✅" if o.get('status')=='completed' else "⏳"
                    glory_txt = o.get('glory_delivered', f"{o['glory_min']//1000}-{o['glory_max']//1000}K")
                    txt += f"{status_emoji} {o['order_id']} - {o['credits_used']}C - {glory_txt} Glory\n"
            else:
                txt += "No orders yet!\n"
        msg = await context.bot.send_message(chat_id=chat_id, text=txt, parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

    elif q.data=="pay_upi":
        upi_path = find_qr("upi_qr")
        users = load_users()
        sel = users.get(str(uid),{}).get('selected_package')
        amt = sel*CREDIT_PRICE if sel else CREDIT_PRICE
        usdt = calc_usdt(amt)
        caption = f"""💳 **UPI PAYMENT** 💳
━━━━━━━━━━━━━━━━━━━━━
💰 Amount: ₹{amt} (~{usdt} USDT)
📱 UPI ID: `{UPI_ID}`

1️⃣ Scan QR or pay to ID
2️⃣ Send Screenshot + UTR
"""
        kb = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_pay")]]
        if upi_path:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=q.message.message_id)
            except: pass
            msg = await context.bot.send_photo(chat_id=chat_id, photo=open(upi_path,"rb"), caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        else:
            msg = await context.bot.send_message(chat_id=chat_id, text=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        users = load_users()
        users[str(uid)]["awaiting_screenshot"]="UPI"
        users[str(uid)]["awaiting_utr"]=True
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

    elif q.data=="pay_usdt":
        usdt_path = find_qr("usdt_qr")
        users = load_users()
        sel = users.get(str(uid),{}).get('selected_package')
        amt = sel*CREDIT_PRICE if sel else CREDIT_PRICE
        usdt_amt = calc_usdt(amt)
        caption = f"""💛 **USDT PAYMENT** 🌐
━━━━━━━━━━━━━━━━━━━━━
💰 Amount: {usdt_amt} USDT (~₹{amt})
🔐 Address: `{USDT_ADDR}`
🌐 Network: TRON (TRC20) Only

📸 Send screenshot now
"""
        kb = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_pay")]]
        if usdt_path:
            msg = await context.bot.send_photo(chat_id=chat_id, photo=open(usdt_path,"rb"), caption=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        else:
            msg = await context.bot.send_message(chat_id=chat_id, text=caption, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        users = load_users()
        users[str(uid)]["awaiting_screenshot"]="USDT"
        users[str(uid)]["awaiting_utr"]=True
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

    elif q.data=="cancel_pay":
        users = load_users()
        if str(uid) in users:
            users[str(uid)]["awaiting_screenshot"]=None
            users[str(uid)]["awaiting_utr"]=False
            users[str(uid)]['last_bot_msgs']=[]
            save_users(users)
        try: await q.message.delete()
        except: pass
        # Go home
        user = get_user(uid)
        me = await context.bot.get_me()
        ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"
        text = f"""🎮 **ZEVRIC GLORY STORE** 🎮
━━━━━━━━━━━━━━━━━━━━━
👋 Welcome, {name}!

💰 Balance: ₹{user['balance']:.2f}
🎫 Credits: {user.get('credits',0)}
🏰 Guild: {user.get('guild_id','Not Set ❌')}

🔗 Referral: `{ref_link}`
"""
        kb = [[InlineKeyboardButton("💰 Add Balance", callback_data="add_balance"),InlineKeyboardButton("🎫 Buy Credits", callback_data="buy_credits")],[InlineKeyboardButton("🚀 Launch Bot", callback_data="launch_bot"),InlineKeyboardButton("🏰 My Guilds", callback_data="my_guilds")],[InlineKeyboardButton("👥 Referrals", callback_data="refs"),InlineKeyboardButton("📊 Stats", callback_data="stats")],[InlineKeyboardButton("📜 History", callback_data="history"),InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT}")]]
        msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

    elif q.data=="refs":
        text = f"""👥 **MY REFERRALS** 💸
━━━━━━━━━━━━━━━━━━━━━
👥 Total: {user['referrals']}
💰 Earned: ₹{user['referrals']*0.1:.2f}
🔗 Link:
`{ref_link}`

💡 1 Refer = ₹0.1
"""
        msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📤 Share Link", url=f"https://t.me/share/url?url={ref_link}")],[InlineKeyboardButton("🏠 Home", callback_data="back_home")]]), parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

    elif q.data=="stats":
        text = f"""📊 **MY STATS** 💎
━━━━━━━━━━━━━━━━━━━━━
👤 Name: {name}
💰 Balance: ₹{user['balance']:.2f}
🎫 Credits: {user.get('credits',0)}
🏰 Guild: {user.get('guild_id','Not Set')}
👥 Referrals: {user['referrals']}
💸 Earn: ₹{user['referrals']*0.1:.2f}
📋 Orders: {len(user.get('orders',[]))}
🟢 Active ✅
"""
        msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Home", callback_data="back_home")]]), parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

    elif q.data=="history":
        hist = user.get('history',[])
        if not hist:
            txt = "📜 **HISTORY** ⏰\nNo history yet! 😅"
        else:
            htxt = "\n".join([f"{i+1}. {h}" for i,h in enumerate(hist[-10:])])
            txt = f"📜 **HISTORY (Last 10)** ⏰\n━━━━━━━━━━━━━━━━━━━━━\n{htxt}"
        msg = await context.bot.send_message(chat_id=chat_id, text=txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Home", callback_data="back_home")]]), parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

    elif q.data.startswith("approve_"):
        pid = q.data.replace("approve_","")
        pending = load_pending()
        if pid in pending:
            user_id = pending[pid]["user_id"]
            amount = pending[pid].get("amount",CREDIT_PRICE)
            users = load_users()
            if str(user_id) in users:
                users[str(user_id)]["balance"]+=float(amount)
                if "history" not in users[str(user_id)]: users[str(user_id)]["history"]=[]
                users[str(user_id)]["history"].append(f"Balance +₹{amount} via {pending[pid]['method']}")
                save_users(users)
            pending[pid]["status"]="approved"
            save_pending(pending)
            await q.message.reply_text(f"✅ Approved {pid} +₹{amount}")
            try:
                # Clear old for user and send new
                await delete_old_messages(context, user_id, user_id)
                msg = await context.bot.send_message(chat_id=user_id, text=f"✅ **PAYMENT APPROVED!** 💰\n💵 Amount: ₹{amount}\n💳 Balance: ₹{users[str(user_id)]['balance']:.2f}", parse_mode="Markdown")
                users = load_users()
                users[str(user_id)]['last_bot_msgs'] = [msg.message_id]
                save_users(users)
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
                await context.bot.send_message(chat_id=user_id, text=f"❌ Payment Cancelled 😥 Contact @{SUPPORT}")
            except: pass

    elif q.data=="back_home":
        await delete_old_messages(context, chat_id, uid)
        user = get_user(uid)
        me = await context.bot.get_me()
        ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"
        text = f"""🎮 **ZEVRIC GLORY STORE** 🎮
━━━━━━━━━━━━━━━━━━━━━
👋 Welcome, {name}! 😎

💰 Balance: ₹{user['balance']:.2f}
🎫 Credits: {user.get('credits',0)}
🏰 Guild: {user.get('guild_id','Not Set ❌')}

🔗 Link: `{ref_link}`
💡 Earn ₹0.1 per refer 🤑
"""
        kb = [[InlineKeyboardButton("💰 Add Balance", callback_data="add_balance"),InlineKeyboardButton("🎫 Buy Credits", callback_data="buy_credits")],[InlineKeyboardButton("🚀 Launch Bot", callback_data="launch_bot"),InlineKeyboardButton("🏰 My Guilds", callback_data="my_guilds")],[InlineKeyboardButton("👥 Referrals", callback_data="refs"),InlineKeyboardButton("📊 Stats", callback_data="stats")],[InlineKeyboardButton("📜 History", callback_data="history"),InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT}")]]
        msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users = load_users()
    awaiting = users.get(str(uid),{}).get("awaiting_screenshot")
    if awaiting:
        # Delete user photo to keep chat clean
        try:
            await update.message.delete()
        except: pass
        
        photo = update.message.photo[-1]
        file_id = photo.file_id
        pid = f"{uid}_{int(time.time())}"
        pending = load_pending()
        sel = users.get(str(uid),{}).get('selected_package')
        amt = (sel*CREDIT_PRICE) if sel else CREDIT_PRICE
        pending[pid] = {"user_id": uid, "username": update.effective_user.username, "name": update.effective_user.first_name, "method": awaiting, "file_id": file_id, "amount": amt, "status": "pending", "time": int(time.time())}
        save_pending(pending)
        users[str(uid)]["awaiting_screenshot"] = None
        save_users(users)
        
        # Auto delete old bot messages
        await delete_old_messages(context, update.effective_chat.id, uid)
        
        msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ **Screenshot Received!** 🧾\n💰 Amount: ₹{amt}\n📸 Ab **UTR** bhejo: 👇", parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)
        
        for admin_id in get_admins():
            try:
                kb = [[InlineKeyboardButton(f"✅ Approve +₹{amt}", callback_data=f"approve_{pid}"),InlineKeyboardButton(f"❌ Cancel", callback_data=f"cancel_{pid}")]]
                await context.bot.send_photo(chat_id=admin_id, photo=file_id, caption=f"🚨 New Payment - {awaiting} 👤 {update.effective_user.first_name} @{update.effective_user.username} 🆔 {uid} 💰 ₹{amt} PID: {pid}", reply_markup=InlineKeyboardMarkup(kb))
            except: pass
    else:
        await delete_old_messages(context, update.effective_chat.id, uid)
        msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="📸 Pehle UPI/USDT select karo! /start 👇")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    users = load_users()
    
    # Delete user message to keep chat clean
    try:
        await update.message.delete()
    except:
        pass
    
    if users.get(str(uid),{}).get('awaiting_guild_id'):
        guild_id = ''.join(filter(str.isdigit, text))
        if len(guild_id) >= 6 and len(guild_id) <= 12:
            users[str(uid)]['guild_id'] = guild_id
            users[str(uid)]['awaiting_guild_id'] = False
            save_users(users)
            await delete_old_messages(context, update.effective_chat.id, uid)
            msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ **Guild ID Set!** 🏰\n🏰 ID: {guild_id}\n🚀 Ab Launch kar sakte ho!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Launch Glory Bot", callback_data="launch_bot")]]), parse_mode="Markdown")
            users = load_users()
            users[str(uid)]['last_bot_msgs'] = [msg.message_id]
            save_users(users)
            return
        else:
            await delete_old_messages(context, update.effective_chat.id, uid)
            msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Valid Guild ID bhejo (6-12 digits) 🏰")
            users = load_users()
            users[str(uid)]['last_bot_msgs'] = [msg.message_id]
            save_users(users)
            return
            
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
            await delete_old_messages(context, update.effective_chat.id, uid)
            msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ **Payment Submitted!** 🎉\n💰 Amount: ₹{users.get(str(uid),{}).get('selected_package',1)*CREDIT_PRICE if users.get(str(uid),{}).get('selected_package') else CREDIT_PRICE}\n🔢 UTR: {utr}\n⏳ Awaiting verification...", parse_mode="Markdown")
            users[str(uid)]['awaiting_utr'] = False
            users[str(uid)]['last_utr'] = utr
            users[str(uid)]['last_bot_msgs'] = [msg.message_id]
            save_users(users)
            for admin_id in get_admins():
                try:
                    await context.bot.send_message(chat_id=admin_id, text=f"📲 UTR Received 🧾 👤 {update.effective_user.first_name} @{update.effective_user.username} 🆔 {uid} 🔢 UTR: {utr} PID: {latest_pid}")
                except: pass
            return
        else:
            await delete_old_messages(context, update.effective_chat.id, uid)
            msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Valid UTR bhejo (12 digit) 🔢")
            users = load_users()
            users[str(uid)]['last_bot_msgs'] = [msg.message_id]
            save_users(users)
            return
            
    if users.get(str(uid),{}).get("awaiting_screenshot"):
        await delete_old_messages(context, update.effective_chat.id, uid)
        msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="📸 Photo bhejo! UTR baad me 🧾👇")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)
    else:
        await delete_old_messages(context, update.effective_chat.id, uid)
        user = get_user(uid)
        me = await context.bot.get_me()
        ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"
        text2 = f"""🎮 **ZEVRIC GLORY STORE** 🎮
━━━━━━━━━━━━━━━━━━━━━
👋 Welcome, {update.effective_user.first_name}!

💰 Balance: ₹{user['balance']:.2f}
🎫 Credits: {user.get('credits',0)}

🔗 Link: `{ref_link}`
"""
        kb = [[InlineKeyboardButton("💰 Add Balance", callback_data="add_balance"),InlineKeyboardButton("🎫 Buy Credits", callback_data="buy_credits")],[InlineKeyboardButton("🚀 Launch Bot", callback_data="launch_bot"),InlineKeyboardButton("🏰 My Guilds", callback_data="my_guilds")]]
        msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=text2, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        users = load_users()
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except: pass
    await delete_old_messages(context, update.effective_chat.id, update.effective_user.id)
    msg = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🆘 **Contact:** @{SUPPORT} 💬\n💳 UPI: {UPI_ID}", parse_mode="Markdown")
    users = load_users()
    uid = update.effective_user.id
    if str(uid) in users:
        users[str(uid)]['last_bot_msgs'] = [msg.message_id]
        save_users(users)

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
            print("BOT LIVE PROFESSIONAL AUTO-DELETE ₹130")
            await asyncio.Event().wait()
        except Exception as e:
            print(f"Main error: {e}")
            await asyncio.sleep(5)

if __name__=="__main__":
    asyncio.run(main())
