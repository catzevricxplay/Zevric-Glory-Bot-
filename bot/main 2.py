
import os, asyncio, json, logging, threading, time, random
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
TOKEN=os.getenv("TELEGRAM_TOKEN")
SUPPORT="just_zevric"
UPI_ID="zervicxplay@okhdfcbank"
USDT_ADDR="TLwAWcJ7Tm34jqyYqV6qhizQHy8pe7US1v"
ADMIN_IDS=os.getenv("ADMIN_IDS","")
CREDIT_PRICE=130
USDT_RATE=95.78
logging.basicConfig(level=logging.INFO)
flask_app=Flask(__name__)
@flask_app.route('/')
def home(): return "ZEVRIC EXTRA PRICE 130 READY"
def run_flask():
 port=int(os.getenv('PORT',10000))
 flask_app.run(host='0.0.0.0',port=port)
threading.Thread(target=run_flask,daemon=True).start()
def load_users():
 try:
  with open("users.json","r") as f: return json.load(f)
 except: return {}
def save_users(d):
 with open("users.json","w") as f: json.dump(d,f)
def get_user(uid):
 users=load_users()
 if str(uid) not in users:
  users[str(uid)]={"balance":0.0,"credits":0,"guild_id":None,"referrals":0,"ref_code":str(uid)[-6:],"awaiting_screenshot":None,"awaiting_utr":False,"awaiting_guild_id":False,"selected_package":None,"orders":[],"history":[]}
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
 for p in [f"bot/{name}.png",f"{name}.png",f"bot/{name}.jpg",f"{name}.jpg"]:
  if os.path.exists(p): return p
 return None
def calc_usdt(inr): return round(inr/USDT_RATE,2)
async def start(update,context):
 uid=update.effective_user.id
 name=update.effective_user.first_name
 users=load_users()
 if context.args:
  for k,v in users.items():
   if v.get("ref_code")==context.args[0] and k!=str(uid):
    users[k]["balance"]+=0.1
    users[k]["referrals"]+=1
    if "history" not in users[k]: users[k]["history"]=[]
    users[k]["history"].append(f"Referral +0.1 from {name}")
    save_users(users)
    break
 user=get_user(uid)
 me=await context.bot.get_me()
 ref_link=f"https://t.me/{me.username}?start={user['ref_code']}"
 text=f"""━━━━━━━━━━━━━━━━━━━━━━
🎮 Guild Glory Credit Shop 🎮
━━━━━━━━━━━━━━━━━━━━━━

👋 Welcome, {name}! 😎

💰 Wallet Balance: ₹{user['balance']:.2f} 💵
🎫 Credits: {user.get('credits',0)} 🪙
🏰 Guild ID: {user.get('guild_id','Not Set')} 🏰

🔥 Trusted by 3.1M+ Players ✅
⚡ 24/7 Auto Bots 🤖
💎 1 Credit = ₹{CREDIT_PRICE} = 10K-50K Glory 🔥
💵 Extra Profit ₹{CREDIT_PRICE-95} per credit 💰

🔗 Referral Link: 🔗
{ref_link}

💡 Earn ₹0.1 per refer! 🤑
"""
 kb=[[InlineKeyboardButton("➕ Add Balance 💰",callback_data="add_balance"),InlineKeyboardButton("🎫 Buy Credits 🏆",callback_data="buy_credits")],[InlineKeyboardButton("🚀 Launch Glory Bot 🤖",callback_data="launch_bot"),InlineKeyboardButton("🏰 My Guilds 📋",callback_data="my_guilds")],[InlineKeyboardButton("👥 My Referrals 🙋",callback_data="refs"),InlineKeyboardButton("📊 My Stats 📈",callback_data="stats")],[InlineKeyboardButton("🕐 History 📜",callback_data="history"),InlineKeyboardButton("📞 Contact Admin 💬",url=f"https://t.me/{SUPPORT}")]]
 await update.message.reply_text(text,reply_markup=InlineKeyboardMarkup(kb))
async def btn_handler(update,context):
 q=update.callback_query
 await q.answer()
 uid=q.from_user.id
 name=q.from_user.first_name
 users=load_users()
 user=get_user(uid)
 if q.data=="add_balance":
  text=f"💳 PAYMENT - ₹{CREDIT_PRICE}/Credit 💳\n💜 UPI 💳\n💛 USDT 🌐\n✅ Auto-approval ⚡"
  kb=[[InlineKeyboardButton("💜 UPI 💳",callback_data="pay_upi"),InlineKeyboardButton("💛 USDT 🌐",callback_data="pay_usdt")],[InlineKeyboardButton("🎫 Buy Credits 🏆",callback_data="buy_credits"),InlineKeyboardButton("🔙 Back 🏠",callback_data="back_home")]]
  await q.message.reply_text(text,reply_markup=InlineKeyboardMarkup(kb))
 elif q.data=="buy_credits":
  bal=user['balance']
  text=f"🎫 Buy Credits - ₹{CREDIT_PRICE} 🔥\nBalance: ₹{bal:.2f}\n1 Credit = ₹{CREDIT_PRICE} = 10K-50K Glory\nExtra Profit ₹{CREDIT_PRICE-95} 💰\n"
  kb=[]
  for i in range(1,7):
   inr=i*CREDIT_PRICE
   usdt=calc_usdt(inr)
   profit=i*(CREDIT_PRICE-95)
   kb.append([InlineKeyboardButton(f"💎 {i}C — ₹{inr} (~{usdt} USDT) Profit ₹{profit} 🔥",callback_data=f"pkg_{i}")])
  kb.append([InlineKeyboardButton("💳 Add Balance 💰",callback_data="add_balance"),InlineKeyboardButton("🔙 Back 🏠",callback_data="back_home")])
  await q.message.reply_text(text,reply_markup=InlineKeyboardMarkup(kb))
 elif q.data.startswith("pkg_"):
  pkg=int(q.data.split("_")[1])
  inr=pkg*CREDIT_PRICE
  users=load_users()
  user=get_user(uid)
  if user['balance']>=inr:
   users[str(uid)]['balance']-=inr
   users[str(uid)]['credits']=users[str(uid)].get('credits',0)+pkg
   if "history" not in users[str(uid)]: users[str(uid)]["history"]=[]
   users[str(uid)]["history"].append(f"Bought {pkg} Credits -₹{inr} Profit ₹{pkg*(CREDIT_PRICE-95)}")
   save_users(users)
   await q.message.reply_text(f"✅ Purchased {pkg} Credits! 🎫 Deducted ₹{inr} Total {users[str(uid)]['credits']} Profit ₹{pkg*(CREDIT_PRICE-95)} 💰",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Launch Glory Bot 🤖",callback_data="launch_bot")]]))
  else:
   need=inr-user['balance']
   usdt=calc_usdt(inr)
   text=f"❌ Insufficient ₹{need:.2f} more 😥\nPackage {pkg}C ₹{inr} (~{usdt} USDT)"
   kb=[[InlineKeyboardButton(f"💜 Pay ₹{inr} UPI 💳",callback_data="pay_upi"),InlineKeyboardButton(f"💛 Pay {usdt} USDT 🌐",callback_data="pay_usdt")],[InlineKeyboardButton("🔙 Back 🏠",callback_data="buy_credits")]]
   await q.message.reply_text(text,reply_markup=InlineKeyboardMarkup(kb))
   users[str(uid)]['selected_package']=pkg
   save_users(users)
 elif q.data=="launch_bot":
  if user.get('credits',0)<1:
   await q.message.reply_text("❌ No Credits! Buy first",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎫 Buy Credits 🏆",callback_data="buy_credits")]]))
   return
  if not user.get('guild_id'):
   await q.message.reply_text("🏰 Guild ID Required!",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏰 Set Guild ID 🆔",callback_data="set_guild_id")]]))
   return
  text=f"🚀 Launch Glory Bot 🤖\nGuild: {user.get('guild_id')}\nCredits: {user.get('credits')}\n"
  kb=[]
  for i in range(1,min(7,user.get('credits',0)+1)):
   kb.append([InlineKeyboardButton(f"🚀 Use {i}C = {i*10}-{i*50}K Glory 🔥",callback_data=f"launch_{i}")])
  kb.append([InlineKeyboardButton("🔙 Back 🏠",callback_data="back_home")])
  await q.message.reply_text(text,reply_markup=InlineKeyboardMarkup(kb))
 elif q.data.startswith("launch_"):
  use=int(q.data.split("_")[1])
  users=load_users()
  user=get_user(uid)
  if user.get('credits',0)<use: return
  guild=user.get('guild_id')
  users[str(uid)]['credits']-=use
  order_id=f"ORD{uid}{int(time.time())}"
  gmin=use*10000
  gmax=use*50000
  order={"order_id":order_id,"guild_id":guild,"credits_used":use,"glory_min":gmin,"glory_max":gmax,"status":"launching","time":int(time.time())}
  if "orders" not in users[str(uid)]: users[str(uid)]["orders"]=[]
  users[str(uid)]["orders"].append(order)
  if "history" not in users[str(uid)]: users[str(uid)]["history"]=[]
  users[str(uid)]["history"].append(f"Launched {use}C for Guild {guild}")
  save_users(users)
  all_orders=load_orders()
  all_orders[order_id]={"user_id":uid,"username":q.from_user.username,"name":name,**order}
  save_orders(all_orders)
  await q.message.reply_text(f"✅ Launched! Order {order_id} Guild {guild} {use}C = {gmin//1000}-{gmax//1000}K Glory Bots joining... ⏳")
  await asyncio.sleep(1)
  glory=random.randint(gmin,gmax)
  users=load_users()
  all_orders=load_orders()
  if order_id in all_orders:
   all_orders[order_id]["status"]="completed"
   all_orders[order_id]["glory_delivered"]=glory
   save_orders(all_orders)
  for o in users.get(str(uid),{}).get("orders",[]):
   if o["order_id"]==order_id:
    o["status"]="completed"
    o["glory_delivered"]=glory
  save_users(users)
  try: await context.bot.send_message(uid,f"🎉 Glory Delivered! {glory} points! Guild {guild} Order {order_id} ✅ Credits left {users[str(uid)]['credits']}")
  except: pass
  for admin in get_admins():
   try: await context.bot.send_message(admin,f"🚀 New Order {order_id} Guild {guild} {use}C = {glory} Glory User {name} {uid}")
   except: pass
 elif q.data=="set_guild_id":
  users[str(uid)]['awaiting_guild_id']=True
  save_users(users)
  await q.message.reply_text("🏰 Guild ID bhejo: Example 12345678")
 elif q.data=="my_guilds":
  gid=user.get('guild_id')
  orders=user.get('orders',[])
  txt=f"🏰 Guild: {gid}\n" if gid else "No Guild\n"
  txt+="Orders:\n"
  for o in orders[-5:]:
   txt+=f"{o['order_id']} {o['credits_used']}C {o.get('glory_delivered',f'{o['glory_min']}-{o['glory_max']}')} {o['status']}\n"
  await q.message.reply_text(txt)
 elif q.data=="pay_upi":
  upi=find_qr("upi_qr")
  sel=users.get(str(uid),{}).get('selected_package')
  amt=sel*CREDIT_PRICE if sel else CREDIT_PRICE
  cap=f"UPI ID {UPI_ID} Amount ₹{amt} - {sel if sel else 1}C 🔥 Screenshot + UTR bhejo"
  kb=[[InlineKeyboardButton("❌ Cancel ❌",callback_data="cancel_pay")]]
  if upi: await context.bot.send_photo(q.message.chat_id,photo=open(upi,"rb"),caption=cap,reply_markup=InlineKeyboardMarkup(kb))
  else: await q.message.reply_text(cap,reply_markup=InlineKeyboardMarkup(kb))
  users[str(uid)]["awaiting_screenshot"]="UPI"
  users[str(uid)]["awaiting_utr"]=True
  save_users(users)
 elif q.data=="pay_usdt":
  usdt=find_qr("usdt_qr")
  sel=users.get(str(uid),{}).get('selected_package')
  amt=sel*CREDIT_PRICE if sel else CREDIT_PRICE
  usdt_amt=calc_usdt(amt)
  cap=f"USDT {USDT_ADDR} TRC20 Amount {usdt_amt} USDT (~₹{amt}) Screenshot bhejo"
  kb=[[InlineKeyboardButton("❌ Cancel ❌",callback_data="cancel_pay")]]
  if usdt: await context.bot.send_photo(q.message.chat_id,photo=open(usdt,"rb"),caption=cap,reply_markup=InlineKeyboardMarkup(kb))
  else: await q.message.reply_text(cap,reply_markup=InlineKeyboardMarkup(kb))
  users[str(uid)]["awaiting_screenshot"]="USDT"
  users[str(uid)]["awaiting_utr"]=True
  save_users(users)
 elif q.data=="cancel_pay":
  users=load_users()
  if str(uid) in users:
   users[str(uid)]["awaiting_screenshot"]=None
   users[str(uid)]["awaiting_utr"]=False
   save_users(users)
  await q.message.reply_text("❌ Cancelled /start")
 elif q.data=="refs":
  me=await context.bot.get_me()
  ref_link=f"https://t.me/{me.username}?start={user['ref_code']}"
  await q.message.reply_text(f"Referrals {user['referrals']} Earned ₹{user['referrals']*0.1:.2f} Link {ref_link}")
 elif q.data=="stats":
  await q.message.reply_text(f"Name {name} Balance ₹{user['balance']:.2f} Credits {user.get('credits',0)} Guild {user.get('guild_id')} Referrals {user['referrals']} Orders {len(user.get('orders',[]))}")
 elif q.data=="history":
  hist=user.get('history',[])
  txt="History:\n" + "\n".join(hist[-10:]) if hist else "No history"
  await q.message.reply_text(txt)
 elif q.data.startswith("approve_"):
  pid=q.data.replace("approve_","")
  pending=load_pending()
  if pid in pending:
   user_id=pending[pid]["user_id"]
   amount=pending[pid].get("amount",CREDIT_PRICE)
   users=load_users()
   if str(user_id) in users:
    users[str(user_id)]["balance"]+=float(amount)
    if "history" not in users[str(user_id)]: users[str(user_id)]["history"]=[]
    users[str(user_id)]["history"].append(f"Balance +₹{amount}")
    save_users(users)
   pending[pid]["status"]="approved"
   save_pending(pending)
   await q.message.reply_text(f"Approved {pid} +₹{amount}")
   try: await context.bot.send_message(user_id,f"Approved ₹{amount} Balance ₹{users[str(user_id)]['balance']:.2f}")
   except: pass
 elif q.data.startswith("cancel_"):
  pid=q.data.replace("cancel_","")
  pending=load_pending()
  if pid in pending:
   pending[pid]["status"]="cancelled"
   save_pending(pending)
   await q.message.reply_text(f"Cancelled {pid}")
 elif q.data=="back_home":
  await start(q,context)
async def handle_photo(update,context):
 uid=update.effective_user.id
 users=load_users()
 awaiting=users.get(str(uid),{}).get("awaiting_screenshot")
 if awaiting:
  photo=update.message.photo[-1]
  file_id=photo.file_id
  pid=f"{uid}_{int(time.time())}"
  pending=load_pending()
  sel=users.get(str(uid),{}).get('selected_package')
  amt=(sel*CREDIT_PRICE) if sel else CREDIT_PRICE
  pending[pid]={"user_id":uid,"username":update.effective_user.username,"name":update.effective_user.first_name,"method":awaiting,"file_id":file_id,"amount":amt,"status":"pending","time":int(time.time())}
  save_pending(pending)
  users[str(uid)]["awaiting_screenshot"]=None
  save_users(users)
  await update.message.reply_text(f"Screenshot received ₹{amt} Ab UTR bhejo")
  for admin in get_admins():
   try:
    kb=[[InlineKeyboardButton(f"Approve ₹{amt}",callback_data=f"approve_{pid}"),InlineKeyboardButton("Cancel",callback_data=f"cancel_{pid}")]]
    await context.bot.send_photo(admin,photo=file_id,caption=f"New Payment {awaiting} User {update.effective_user.first_name} {uid} ₹{amt} PID {pid}",reply_markup=InlineKeyboardMarkup(kb))
   except: pass
 else:
  await update.message.reply_text("Pehle UPI/USDT select karo /start")
async def handle_text(update,context):
 uid=update.effective_user.id
 text=update.message.text.strip()
 users=load_users()
 if users.get(str(uid),{}).get('awaiting_guild_id'):
  gid=''.join(filter(str.isdigit,text))
  if len(gid)>=6 and len(gid)<=12:
   users[str(uid)]['guild_id']=gid
   users[str(uid)]['awaiting_guild_id']=False
   save_users(users)
   await update.message.reply_text(f"Guild ID Set {gid} Ab Launch kar sakte ho",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Launch Bot 🤖",callback_data="launch_bot")]]))
   return
  else:
   await update.message.reply_text("Valid Guild ID bhejo 6-12 digits")
   return
 if users.get(str(uid),{}).get('awaiting_utr'):
  utr=''.join(filter(str.isalnum,text))
  if len(utr)>=8:
   pending=load_pending()
   latest=None
   for pid,data in pending.items():
    if str(data.get('user_id'))==str(uid) and data.get('status')=='pending': latest=pid
   if latest: pending[latest]['utr']=utr; save_pending(pending)
   await update.message.reply_text(f"Payment Submitted ₹{users.get(str(uid),{}).get('selected_package',1)*CREDIT_PRICE if users.get(str(uid),{}).get('selected_package') else CREDIT_PRICE} UTR {utr} Awaiting verification")
   users[str(uid)]['awaiting_utr']=False
   users[str(uid)]['last_utr']=utr
   save_users(users)
   for admin in get_admins():
    try: await context.bot.send_message(admin,f"UTR {utr} User {update.effective_user.first_name} {uid} PID {latest}")
    except: pass
   return
  else:
   await update.message.reply_text("Valid UTR bhejo 12 digit")
   return
 if users.get(str(uid),{}).get("awaiting_screenshot"):
  await update.message.reply_text("Photo bhejo UTR baad me")
 else:
  await update.message.reply_text("/start dabao")
async def help_cmd(update,context):
 await update.message.reply_text(f"Contact @{SUPPORT}")
async def main():
 while True:
  try:
   if not TOKEN: await asyncio.sleep(10); continue
   app=Application.builder().token(TOKEN).build()
   app.add_handler(CommandHandler("start",start))
   app.add_handler(CommandHandler("help",help_cmd))
   app.add_handler(CommandHandler("support",help_cmd))
   app.add_handler(CallbackQueryHandler(btn_handler))
   app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_text))
   app.add_handler(MessageHandler(filters.PHOTO,handle_photo))
   await app.initialize()
   await app.start()
   await app.updater.start_polling()
   print("BOT LIVE EXTRA PRICE 130 GLORY BOT")
   await asyncio.Event().wait()
  except Exception as e:
   print(e)
   await asyncio.sleep(5)
if __name__=="__main__":
 asyncio.run(main())
