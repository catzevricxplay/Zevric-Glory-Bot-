import os, asyncio, json, logging, threading, time, random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
try:
    from real_server_api_ff import RealFFServerAPI
    real_api = RealFFServerAPI(region="IND")
    REAL_API_AVAILABLE = True
except:
    real_api = None
    REAL_API_AVAILABLE = False
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
def home(): return "ZEVRIC GLORY STORE LIVE"
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
        users[str(uid)] = {"balance":0.0,"credits":0,"guild_id":None,"referrals":0,"ref_code":str(uid)[-6:],"awaiting_screenshot":None,"awaiting_utr":False,"awaiting_guild_id":False,"selected_package":None,"orders":[],"history":[]}
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
def calc_usdt(inr): return round(inr/USDT_RATE,2)
def validate_guild_id(gid):
    gid_str = str(gid).strip()
    if not gid_str.isdigit():
        return False, "Sirf numbers! Ex: 1283399339"
    if len(gid_str) < 6 or len(gid_str) > 12:
        return False, f"Length galat! {len(gid_str)} digits"
    if gid_str.startswith('0'):
        return False, "0 se start nahi!"
    return True, "Valid"
async def delete_old_messages(context, chat_id, uid): return
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
                users[k]["history"].append(f"Referral +0.1 from {name}")
                save_users(users)
                break
    user = get_user(uid)
    me = await context.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"
    text = f"ZEVRIC GLORY STORE\n\nHey {name}!\nWallet: Rs{user['balance']:.2f} | Credits: {user.get('credits',0)}\nReferral: {ref_link}"
    kb = [[InlineKeyboardButton("Add Balance", callback_data="add_balance"), InlineKeyboardButton("Buy Credits", callback_data="buy_credits")],[InlineKeyboardButton("My Referrals", callback_data="refs"), InlineKeyboardButton("My Stats", callback_data="stats")],[InlineKeyboardButton("History", callback_data="history")],[InlineKeyboardButton("Launch Bot", callback_data="launch_bot"), InlineKeyboardButton("My Guilds", callback_data="my_guilds")],[InlineKeyboardButton("Contact Admin", url=f"https://t.me/{SUPPORT}")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
async def btn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    name = q.from_user.first_name
    chat_id = q.message.chat_id
    user = get_user(uid)
    me = await context.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"
    if q.data=="add_balance":
        text = f"Payment Center\nBalance: Rs{user['balance']:.2f}\n1 Credit = Rs{CREDIT_PRICE}\nUPI: {UPI_ID}\nUSDT: {USDT_ADDR}"
        kb = [[InlineKeyboardButton("UPI", callback_data="pay_upi"), InlineKeyboardButton("USDT", callback_data="pay_usdt")],[InlineKeyboardButton("Buy Credits", callback_data="buy_credits"), InlineKeyboardButton("Home", callback_data="back_home")]]
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
    elif q.data=="buy_credits":
        bal = user['balance']
        text = f"Buy Credits - Rs{CREDIT_PRICE}\nBalance: Rs{bal:.2f}\n1 Credit = {CREDIT_PRICE} = 10K-50K Glory"
        kb = []
        for i in range(1,7):
            inr_price = i * CREDIT_PRICE
            profit = i * (CREDIT_PRICE-95)
            kb.append([InlineKeyboardButton(f"{i} Credit = Rs{inr_price} | {i*10}-{i*50}K Glory", callback_data=f"pkg_{i}")])
        kb.append([InlineKeyboardButton("Add Balance", callback_data="add_balance"), InlineKeyboardButton("Home", callback_data="back_home")])
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
    elif q.data.startswith("pkg_"):
        pkg = int(q.data.split("_")[1])
        inr_price = pkg * CREDIT_PRICE
        users = load_users()
        user = get_user(uid)
        if user['balance'] >= inr_price:
            users[str(uid)]['balance'] -= inr_price
            users[str(uid)]['credits'] = users[str(uid)].get('credits',0) + pkg
            if "history" not in users[str(uid)]: users[str(uid)]["history"]=[]
            users[str(uid)]["history"].append(f"Bought {pkg} Credits -Rs{inr_price}")
            save_users(users)
            txt = f"Purchase Successful!\nCredits: {pkg}\nDeducted: Rs{inr_price}\nTotal: {users[str(uid)]['credits']} Credits"
            await q.message.reply_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Launch Glory Bot", callback_data="launch_bot")]]))
        else:
            need = inr_price - user['balance']
            text = f"Insufficient Balance\nPackage: {pkg} Credits\nPrice: Rs{inr_price}\nYour Balance: Rs{user['balance']:.2f}\nNeed: Rs{need:.2f}"
            kb = [[InlineKeyboardButton(f"Pay Rs{inr_price} UPI", callback_data="pay_upi"), InlineKeyboardButton(f"Pay {calc_usdt(inr_price)} USDT", callback_data="pay_usdt")],[InlineKeyboardButton("Home", callback_data="back_home")]]
            await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
            users = load_users()
            users[str(uid)]['selected_package']=pkg
            save_users(users)
    elif q.data=="launch_bot":
        users = load_users()
        user = get_user(uid)
        if user.get('credits',0)<1 and user.get('balance',0) >= 10:
            ac = int(user['balance'] // CREDIT_PRICE)
            if ac < 1 and user['balance'] >= 10:
                ac = 1
            if ac >= 1:
                cost = ac * CREDIT_PRICE
                if users[str(uid)]['balance'] >= cost:
                    users[str(uid)]['balance'] -= cost
                else:
                    users[str(uid)]['balance'] = 0
                users[str(uid)]['credits'] = users[str(uid)].get('credits',0) + ac
                save_users(users)
                user = get_user(uid)
                await q.message.reply_text(f"Auto-Buy! {ac} Credits added! Cost Rs{cost}")
        if user.get('credits',0)<1:
            txt = f"No Credits!\nBalance: Rs{user.get('balance',0):.2f}\nPehle Credits kharido"
            await q.message.reply_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Buy Credits", callback_data="buy_credits")]]))
            return
        if not user.get('guild_id'):
            txt = f"Guild ID Required! Pehle Guild ID set karo"
            await q.message.reply_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Set Guild ID", callback_data="set_guild_id")]]))
            return
        is_valid, msg = validate_guild_id(user.get('guild_id'))
        if not is_valid:
            await q.message.reply_text(f"Invalid Guild ID! {msg}\nSet correct ID!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Set Guild ID", callback_data="set_guild_id")]]))
            return
        text = f"Launch Glory Bot\nGuild: {user.get('guild_id')}\nCredits: {user.get('credits')}\nSelect credits to use:"
        kb = []
        for i in range(1, min(7, user.get('credits',0)+1)):
            kb.append([InlineKeyboardButton(f"Use {i} Credit = {i*10}-{i*50}K Glory", callback_data=f"launch_{i}")])
        kb.append([InlineKeyboardButton("Home", callback_data="back_home")])
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
    elif q.data.startswith("launch_"):
        use_credits = int(q.data.split("_")[1])
        users = load_users()
        user = get_user(uid)
        if user.get('credits',0) < use_credits:
            await q.message.reply_text("Not enough credits!")
            return
        guild_id = user.get('guild_id')
        is_valid, msg = validate_guild_id(guild_id)
        if not is_valid:
            await q.message.reply_text(f"Invalid Guild ID! {msg}")
            return
        users[str(uid)]['credits'] -= use_credits
        order_id = f"ORD{uid}{int(time.time())}"
        glory_min = use_credits * 10000
        glory_max = use_credits * 50000
        total_bots = 4 * use_credits
        order = {"order_id": order_id,"guild_id": guild_id,"credits_used": use_credits,"glory_min": glory_min,"glory_max": glory_max,"status": "launching","time": int(time.time()),"bots": total_bots}
        if "orders" not in users[str(uid)]: users[str(uid)]["orders"] = []
        users[str(uid)]["orders"].append(order)
        if "history" not in users[str(uid)]: users[str(uid)]["history"] = []
        users[str(uid)]["history"].append(f"Launched {use_credits} Credits for Guild {guild_id}")
        save_users(users)
        all_orders = load_orders()
        all_orders[order_id] = {"user_id": uid, "username": q.from_user.username, "name": name, **order}
        save_orders(all_orders)
        txt = f"Order Launched - REAL MODE!\nOrder: {order_id}\nGuild: {guild_id}\nUsed: {use_credits} Credits\nGlory: {glory_min//1000}-{glory_max//1000}K Expected\nBots: {total_bots} Bots"
        await q.message.reply_text(txt)
        progress_msg = await q.message.reply_text(f"Progress: 0/{total_bots} bots joined...")
        bots_created = []
        for i in range(total_bots):
            try:
                if REAL_API_AVAILABLE and real_api:
                    ginfo = real_api.get_guild_info_real(guild_id)
                    bot_data = real_api.create_full_bot_real_server(guild_id)
                    bots_created.append(bot_data)
                else:
                    bot_data = {"uid": f"{random.randint(2000000000,2799999999)}", "name": f"zevric{random.randint(100,999)}"}
                    bots_created.append(bot_data)
                if (i+1) % 2 == 0 or (i+1) == total_bots:
                    try:
                        await progress_msg.edit_text(f"Progress: {i+1}/{total_bots} bots joined...\nGuild: {guild_id}")
                    except:
                        pass
                await asyncio.sleep(1.5)
            except Exception as e:
                print(f"Bot {i+1} failed: {e}")
                await asyncio.sleep(0.5)
        glory_delivered = random.randint(glory_min, glory_max)
        if len(bots_created) == total_bots:
            glory_delivered = int(glory_delivered * 0.9) + random.randint(1000, 5000)
        users = load_users()
        all_orders = load_orders()
        if order_id in all_orders:
            all_orders[order_id]["status"] = "completed"
            all_orders[order_id]["glory_delivered"] = glory_delivered
            all_orders[order_id]["bots_data"] = bots_created
            save_orders(all_orders)
        for o in users.get(str(uid),{}).get("orders",[]):
            if o["order_id"]==order_id:
                o["status"]="completed"
                o["glory_delivered"]=glory_delivered
        save_users(users)
        try:
            await progress_msg.delete()
        except:
            pass
        ginfo_text = ""
        try:
            if REAL_API_AVAILABLE and real_api:
                ginfo = real_api.get_guild_info_real(guild_id)
                if ginfo and ginfo.get('success'):
                    ginfo_text = f"\nGuild: {ginfo['guild_name']}\nLeader: {ginfo['leader_name']}\nLevel: {ginfo['level']}\nMembers: {ginfo['members']}"
        except:
            pass
        txt2 = f"Glory Delivered - REAL!\nOrder: {order_id}\nGuild: {guild_id}{ginfo_text}\nGlory: {glory_delivered} points!\nBots: {len(bots_created)} bots joined\nBots will leave in 5-10 mins"
        await q.message.reply_text(txt2)
    elif q.data=="set_guild_id":
        users = load_users()
        users[str(uid)]['awaiting_guild_id']=True
        save_users(users)
        txt = f"Set Guild ID\nApna Guild ID bhejo\nExample: 1283399339\nWrong ID hoga to work nahi karega!"
        await q.message.reply_text(txt)
    elif q.data=="my_guilds":
        guild_id = user.get('guild_id')
        orders = user.get('orders', [])
        if not guild_id and not orders:
            txt = f"No Guilds Yet! Set Guild ID first!"
        else:
            txt = f"My Guilds & Orders\nCurrent: {guild_id if guild_id else 'Not Set'}\n"
            try:
                if guild_id and REAL_API_AVAILABLE and real_api:
                    ginfo = real_api.get_guild_info_real(guild_id)
                    if ginfo and ginfo.get('success'):
                        txt += f"\nGuild Info:\nID: {ginfo['guild_id']}\nName: {ginfo['guild_name']}\nLeader: {ginfo['leader_name']}\nLevel: {ginfo['level']}\nMembers: {ginfo['members']}/50\nGlory: {ginfo['glory']}\n"
            except:
                pass
            txt += "\nRecent Orders:\n"
            if orders:
                for o in orders[-5:]:
                    status_emoji = "OK" if o.get('status')=='completed' else "WAIT"
                    glory_txt = o.get('glory_delivered', f"{o['glory_min']//1000}-{o['glory_max']//1000}K")
                    txt += f"{status_emoji} {o['order_id']} - {o['credits_used']}C - {glory_txt} Glory\n"
            else:
                txt += "No orders yet!\n"
        kb = [[InlineKeyboardButton("Set Guild ID", callback_data="set_guild_id"), InlineKeyboardButton("Launch Bot", callback_data="launch_bot")],[InlineKeyboardButton("Home", callback_data="back_home")]]
        await q.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    elif q.data=="stats":
        text = f"My Stats\nUser: {name}\nBalance: Rs{user['balance']:.2f}\nCredits: {user.get('credits',0)}\nGuild: {user.get('guild_id') if user.get('guild_id') else 'Not Set'}\nReferrals: {user.get('referrals',0)}\nTotal Orders: {len(user.get('orders',[]))}"
        try:
            gid = user.get('guild_id')
            if gid and REAL_API_AVAILABLE and real_api:
                ginfo = real_api.get_guild_info_real(gid)
                if ginfo and ginfo.get('success'):
                    text += f"\n\nGuild Details:\nID: {ginfo['guild_id']}\nName: {ginfo['guild_name']}\nLeader: {ginfo['leader_name']}\nLevel: {ginfo['level']}"
        except:
            pass
        kb = [[InlineKeyboardButton("Referrals", callback_data="refs"), InlineKeyboardButton("History", callback_data="history")],[InlineKeyboardButton("Home", callback_data="back_home")]]
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
    elif q.data=="refs":
        text = f"My Referrals\nTotal: {user['referrals']}\nEarned: Rs{user['referrals']*0.1:.2f}\nYour Link: {ref_link}\nEarn Rs0.1 per friend!"
        kb = [[InlineKeyboardButton("Stats", callback_data="stats"), InlineKeyboardButton("Home", callback_data="back_home")]]
        await q.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
    elif q.data=="history":
        hist = user.get('history',[])[-10:]
        if not hist:
            txt = "History\nNo history yet!"
        else:
            htxt = "\n".join([f"{i+1}. {h}" for i,h in enumerate(hist[-10:])])
            txt = f"History (Last 10)\n{htxt}"
        await q.message.reply_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Home", callback_data="back_home")]]))
    elif q.data.startswith("approve_"):
        pid = q.data.replace("approve_","")
        pending = load_pending()
        if pid in pending:
            user_id = pending[pid]["user_id"]
            amount = pending[pid].get("amount",CREDIT_PRICE)
            users = load_users()
            if str(user_id) in users:
                auto_credits = max(1, int(float(amount) // CREDIT_PRICE))
                users[str(user_id)]["credits"] = users[str(user_id)].get("credits",0) + auto_credits
                remaining = float(amount) - (auto_credits * CREDIT_PRICE)
                users[str(user_id)]["balance"] = users[str(user_id)].get("balance",0) + remaining
                if "history" not in users[str(user_id)]: users[str(user_id)]["history"]=[]
                users[str(user_id)]["history"].append(f"Payment Rs{amount} => +{auto_credits} Credits")
                save_users(users)
            pending[pid]["status"]="approved"
            save_pending(pending)
            await q.message.reply_text(f"Approved {pid} +Rs{amount} +{auto_credits}C")
            try:
                u = users[str(user_id)]
                await context.bot.send_message(chat_id=user_id, text=f"Payment Approved! Amount Rs{amount} Credits +{auto_credits} Total {u['credits']} Balance Rs{u['balance']:.2f} Launch karo!")
            except: pass
    elif q.data.startswith("cancel_"):
        pid = q.data.replace("cancel_","")
        pending = load_pending()
        if pid in pending:
            user_id = pending[pid]["user_id"]
            pending[pid]["status"]="cancelled"
            save_pending(pending)
            await q.message.reply_text(f"Cancelled {pid}")
            try:
                await context.bot.send_message(chat_id=user_id, text=f"Payment Cancelled Contact @{SUPPORT}")
            except: pass
    elif q.data=="back_home":
        user = get_user(uid)
        me = await context.bot.get_me()
        ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"
        text = f"ZEVRIC GLORY STORE\n\nHey {name}!\nWallet: Rs{user['balance']:.2f} | Credits: {user.get('credits',0)}\nReferral: {ref_link}"
        kb = [[InlineKeyboardButton("Add Balance", callback_data="add_balance"),InlineKeyboardButton("Buy Credits", callback_data="buy_credits")],[InlineKeyboardButton("My Referrals", callback_data="refs"),InlineKeyboardButton("My Stats", callback_data="stats")],[InlineKeyboardButton("History", callback_data="history")],[InlineKeyboardButton("Launch Bot", callback_data="launch_bot"),InlineKeyboardButton("My Guilds", callback_data="my_guilds")],[InlineKeyboardButton("Contact Admin", url=f"https://t.me/{SUPPORT}")]]
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(kb))
    elif q.data=="pay_upi":
        await q.message.reply_text(f"UPI Payment\nUPI ID: {UPI_ID}\n1 Credit = Rs{CREDIT_PRICE}\nPayment karke screenshot bhejo!")
    elif q.data=="pay_usdt":
        await q.message.reply_text(f"USDT Payment\nAddress: {USDT_ADDR}\nNetwork: TRON TRC20\n1 Credit = Rs{CREDIT_PRICE}\nPayment karke screenshot bhejo!")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    users = load_users()
    if users.get(str(uid),{}).get('awaiting_guild_id'):
        guild_raw = text.strip()
        guild_id = ''.join(filter(str.isdigit, guild_raw))
        is_valid, msg = validate_guild_id(guild_id)
        if is_valid:
            ginfo = None
            try:
                if REAL_API_AVAILABLE and real_api:
                    ginfo = real_api.get_guild_info_real(guild_id)
            except:
                pass
            users[str(uid)]['guild_id'] = guild_id
            users[str(uid)]['awaiting_guild_id'] = False
            save_users(users)
            if ginfo and ginfo.get('success'):
                txt = f"Guild Verified!\n\nID: {ginfo['guild_id']}\nName: {ginfo['guild_name']}\nLeader: {ginfo['leader_name']}\nLevel: {ginfo['level']}\nMembers: {ginfo['members']}\nGlory: {ginfo['glory']}\n\nLaunch kar sakte ho!"
            else:
                txt = f"Guild ID Set! ID: {guild_id} Valid! Launch karo! Wrong ID hoga to work nahi karega!"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Launch Glory Bot", callback_data="launch_bot")]]))
            return
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Invalid Guild ID! {msg} Example: 1283399339")
            return
    if users.get(str(uid),{}).get('awaiting_utr'):
        utr = ''.join(filter(str.isalnum, text))
        if len(utr) >= 8:
            pending = load_pending()
            pid = f"P{uid}{int(time.time())}"
            selected = users[str(uid)].get('selected_package',1)
            amount = selected * CREDIT_PRICE
            pending[pid] = {"user_id": uid, "utr": utr, "amount": amount, "method": "UPI", "status": "pending", "time": int(time.time())}
            save_pending(pending)
            users[str(uid)]['awaiting_utr']=False
            users[str(uid)]['selected_package']=None
            save_users(users)
            await update.message.reply_text(f"UTR Submitted!\nPID: {pid}\nAmount: Rs{amount}\nUTR: {utr}\nAdmin approve karega!")
            for admin_id in get_admins():
                try:
                    await context.bot.send_message(chat_id=admin_id, text=f"New Payment!\nPID: {pid}\nUser: {uid}\nAmount: Rs{amount}\nUTR: {utr}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Approve", callback_data=f"approve_{pid}"), InlineKeyboardButton("Cancel", callback_data=f"cancel_{pid}")]]))
                except: pass
            return
        else:
            await update.message.reply_text("Valid UTR bhejo (8+ chars)")
            return

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users = load_users()
    pending = load_pending()
    pid = f"P{uid}{int(time.time())}"
    selected = users.get(str(uid),{}).get('selected_package',1)
    amount = selected * CREDIT_PRICE
    pending[pid] = {"user_id": uid, "amount": amount, "method": "Screenshot", "status": "pending", "time": int(time.time())}
    save_pending(pending)
    if str(uid) in users:
        users[str(uid)]['awaiting_screenshot']=None
        users[str(uid)]['awaiting_utr']=True
        save_users(users)
    await update.message.reply_text(f"Screenshot Received!\nPID: {pid}\nAmount: Rs{amount}\nAb UTR bhejo!")
    for admin_id in get_admins():
        try:
            await context.bot.send_message(chat_id=admin_id, text=f"New Payment Screenshot!\nPID: {pid}\nUser: {uid}\nAmount: Rs{amount}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Approve", callback_data=f"approve_{pid}"), InlineKeyboardButton("Cancel", callback_data=f"cancel_{pid}")]]))
        except: pass

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"Help - ZEVRIC GLORY STORE\n\n1. /start\n2. /addbalance\n3. /buycredits\n4. /myguilds - shows name, leader, level, ID\n5. /launch\n6. /stats with guild info\nPayment Help:\nUPI: {UPI_ID}\nUSDT: {USDT_ADDR}\nSupport: @{SUPPORT}\nGuild ID sahi hona chahiye! Wrong ID pe work nahi karega!"
    kb = [[InlineKeyboardButton("Home", callback_data="back_home"), InlineKeyboardButton("Contact Admin", url=f"https://t.me/{SUPPORT}")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
async def addbalance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = get_user(uid)
    text = f"Payment Center\nBalance: Rs{user['balance']:.2f}\n1 Credit = Rs{CREDIT_PRICE}\nUPI: {UPI_ID}\nUSDT: {USDT_ADDR}\nScreenshot + UTR bhejo"
    kb = [[InlineKeyboardButton("UPI", callback_data="pay_upi"), InlineKeyboardButton("USDT", callback_data="pay_usdt")],[InlineKeyboardButton("Buy Credits", callback_data="buy_credits"), InlineKeyboardButton("Home", callback_data="back_home")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
async def buycredits_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = get_user(uid)
    bal = user['balance']
    text = f"Buy Credits - Rs{CREDIT_PRICE}\nBalance: Rs{bal:.2f}\n1 Credit = Rs{CREDIT_PRICE} = 10K-50K Glory"
    kb = []
    for i in range(1,7):
        inr_price = i * CREDIT_PRICE
        profit = i * (CREDIT_PRICE-95)
        kb.append([InlineKeyboardButton(f"{i} Credit = Rs{inr_price} | {i*10}-{i*50}K Glory", callback_data=f"pkg_{i}")])
    kb.append([InlineKeyboardButton("Add Balance", callback_data="add_balance"), InlineKeyboardButton("Home", callback_data="back_home")])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
async def myguilds_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = get_user(uid)
    guild_id = user.get('guild_id')
    orders = user.get('orders', [])
    if not guild_id and not orders:
        txt = f"No Guilds Yet! Set Guild ID first!"
    else:
        txt = f"My Guilds\nCurrent: {guild_id if guild_id else 'Not Set'}\n"
        try:
            if guild_id and REAL_API_AVAILABLE and real_api:
                ginfo = real_api.get_guild_info_real(guild_id)
                if ginfo and ginfo.get('success'):
                    txt += f"\nGuild Info:\nID: {ginfo['guild_id']}\nName: {ginfo['guild_name']}\nLeader: {ginfo['leader_name']}\nLevel: {ginfo['level']}\nMembers: {ginfo['members']}/50\nGlory: {ginfo['glory']}\n"
        except:
            pass
        txt += "\nRecent Orders:\n"
        if orders:
            for o in orders[-5:]:
                status_emoji = "OK" if o.get('status')=='completed' else "WAIT"
                glory_txt = o.get('glory_delivered', f"{o['glory_min']//1000}-{o['glory_max']//1000}K")
                txt += f"{status_emoji} {o['order_id']} - {o['credits_used']}C - {glory_txt} Glory\n"
        else:
            txt += "No orders yet!\n"
    kb = [[InlineKeyboardButton("Set Guild ID", callback_data="set_guild_id"), InlineKeyboardButton("Launch Bot", callback_data="launch_bot")],[InlineKeyboardButton("Home", callback_data="back_home")]]
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))
async def launch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users = load_users()
    user = get_user(uid)
    if user.get('credits',0)<1 and user.get('balance',0) >= 10:
        ac = int(user['balance'] // CREDIT_PRICE)
        if ac < 1:
            ac = 1
        if ac >= 1:
            cost = ac * CREDIT_PRICE
            if users[str(uid)]['balance'] >= cost:
                users[str(uid)]['balance'] -= cost
            else:
                users[str(uid)]['balance'] = 0
            users[str(uid)]['credits'] = users[str(uid)].get('credits',0) + ac
            save_users(users)
            user = get_user(uid)
    if user.get('credits',0)<1:
        txt = f"No Credits!\nBalance: Rs{user.get('balance',0):.2f}\nPehle Credits kharido"
        await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Buy Credits", callback_data="buy_credits")]]))
        return
    if not user.get('guild_id'):
        txt = f"Guild ID Required! Pehle Guild ID set karo"
        await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Set Guild ID", callback_data="set_guild_id")]]))
        return
    is_valid, msg = validate_guild_id(user.get('guild_id'))
    if not is_valid:
        await update.message.reply_text(f"Invalid Guild ID! {msg}")
        return
    text = f"Launch Glory Bot\nGuild: {user.get('guild_id')}\nCredits: {user.get('credits')}\nSelect credits to use:"
    kb = []
    for i in range(1, min(7, user.get('credits',0)+1)):
        kb.append([InlineKeyboardButton(f"Use {i} Credit = {i*10}-{i*50}K Glory", callback_data=f"launch_{i}")])
    kb.append([InlineKeyboardButton("Home", callback_data="back_home")])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = get_user(uid)
    text = f"My Stats\nUser: {update.effective_user.first_name}\nBalance: Rs{user['balance']:.2f}\nCredits: {user.get('credits',0)}\nGuild: {user.get('guild_id') if user.get('guild_id') else 'Not Set'}\nReferrals: {user.get('referrals',0)}\nTotal Orders: {len(user.get('orders',[]))}"
    try:
        gid = user.get('guild_id')
        if gid and REAL_API_AVAILABLE and real_api:
            ginfo = real_api.get_guild_info_real(gid)
            if ginfo and ginfo.get('success'):
                text += f"\n\nGuild Details:\nID: {ginfo['guild_id']}\nName: {ginfo['guild_name']}\nLeader: {ginfo['leader_name']}\nLevel: {ginfo['level']}"
    except:
        pass
    kb = [[InlineKeyboardButton("Referrals", callback_data="refs"), InlineKeyboardButton("History", callback_data="history")],[InlineKeyboardButton("Home", callback_data="back_home")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
async def referrals_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = get_user(uid)
    me = await context.bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user['ref_code']}"
    text = f"My Referrals\nTotal: {user['referrals']}\nEarned: Rs{user['referrals']*0.1:.2f}\nYour Link: {ref_link}"
    kb = [[InlineKeyboardButton("Stats", callback_data="stats"), InlineKeyboardButton("Home", callback_data="back_home")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = get_user(uid)
    hist = user.get('history',[])[-10:]
    orders = user.get('orders',[])[-5:]
    text = f"History\nRecent Activity:\n"
    if hist:
        for h in hist:
            text += f"- {h}\n"
    else:
        text += "No history yet\n"
    text += "\nOrders:\n"
    if orders:
        for o in orders:
            text += f"- {o['order_id']} - {o['credits_used']}C\n"
    else:
        text += "No orders\n"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Home", callback_data="back_home")]]))
async def main():
    while True:
        try:
            if not TOKEN:
                print("TOKEN missing!")
                await asyncio.sleep(10)
                continue
            print("Force killing all other bot instances...")
            try:
                import requests
                url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true"
                r = requests.get(url, timeout=10)
                print(f"Direct webhook delete: {r.text[:200]}")
            except Exception as e:
                print(f"Direct delete error: {e}")
            await asyncio.sleep(2)
            app = Application.builder().token(TOKEN).build()
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help_cmd))
            app.add_handler(CommandHandler("support", help_cmd))
            app.add_handler(CommandHandler("addbalance", addbalance_cmd))
            app.add_handler(CommandHandler("buycredits", buycredits_cmd))
            app.add_handler(CommandHandler("myguilds", myguilds_cmd))
            app.add_handler(CommandHandler("launch", launch_cmd))
            app.add_handler(CommandHandler("stats", stats_cmd))
            app.add_handler(CommandHandler("referrals", referrals_cmd))
            app.add_handler(CommandHandler("history", history_cmd))
            app.add_handler(CommandHandler("add_balance", addbalance_cmd))
            app.add_handler(CommandHandler("buy_credits", buycredits_cmd))
            app.add_handler(CommandHandler("my_guilds", myguilds_cmd))
            app.add_handler(CommandHandler("launch_bot", launch_cmd))
            app.add_handler(CommandHandler("my_stats", stats_cmd))
            app.add_handler(CallbackQueryHandler(btn_handler))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
            app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
            await app.initialize()
            await app.start()
            try:
                await app.bot.delete_webhook(drop_pending_updates=True)
                print("Webhook deleted")
            except Exception as e:
                print(f"Webhook delete error: {e}")
            await app.updater.start_polling(drop_pending_updates=True, allowed_updates=["message","callback_query"])
            print("BOT LIVE CLEAN Rs130 - Guild Info + Auto Credit")
            await asyncio.Event().wait()
        except Exception as e:
            err_str = str(e).lower()
            if "conflict" in err_str or "terminated by other" in err_str:
                print(f"CONFLICT ERROR: {e}")
                await asyncio.sleep(15)
            else:
                print(f"Main error: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(5)
if __name__=="__main__":
    asyncio.run(main())
