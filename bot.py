import time
import threading
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot import types
from datetime import datetime
import config
from engine import TradePosition

# Support UTF-8 in Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Lightweight HTTP Health Check for Render Cloud 24/7 Hosting
class RenderHealthServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Trade Guardian Bot is running 24/7 on Cloud!")

    def log_message(self, format, *args):
        pass  # Suppress HTTP request logs

def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(("0.0.0.0", port), RenderHealthServer)
        print(f"[*] Cloud Web Health Server running on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"[*] Web Server notice: {e}")

threading.Thread(target=start_health_server, daemon=True).start()

bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN, parse_mode="Markdown")

# Global Active State
active_position: TradePosition = None
current_tracked_symbol: str = "SENSEX 72700 PE"
registered_chat_ids = set()

# Save / Load Chat IDs
CHAT_FILE = "registered_chats.txt"

def load_chats():
    global registered_chat_ids
    try:
        with open(CHAT_FILE, "r") as f:
            for line in f:
                cid = line.strip()
                if cid:
                    registered_chat_ids.add(int(cid))
    except FileNotFoundError:
        pass

def save_chat(chat_id):
    registered_chat_ids.add(chat_id)
    with open(CHAT_FILE, "w") as f:
        for cid in registered_chat_ids:
            f.write(f"{cid}\n")

load_chats()

def broadcast_alert(message: str):
    """Sends an alert to all registered user chats."""
    for cid in registered_chat_ids:
        try:
            bot.send_message(cid, message)
        except Exception as e:
            print(f"[Error sending alert to {cid}]: {e}")

# -------------------------------------------------------------
# COMMAND HANDLERS (PRODUCTION READY)
# -------------------------------------------------------------

@bot.message_handler(commands=['start'])
def handle_start(message):
    save_chat(message.chat.id)
    welcome_text = (
        f"👋 *Trade Guardian - Options Assistant Online!* 🛡️\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Cloud server-la 24/7 active-ah irukku. Laptop thevaiye illa!\n\n"
        f"🌅 *Daily Routine:*\n"
        f"1. *Morning Track:* `/track SENSEX 72700 PE`\n"
        f"2. *Alice Blue-la Buy pannitu:* `/buy 10:36 121`\n"
        f"3. *Price Update:* Just type current price (e.g. `135`)\n"
        f"4. *Auto Sell Alerts:* +₹500, +₹1,000, +₹2,000, +₹3,000 profit vandha SELL notification varum!\n"
        f"5. *70% Drop Shield:* Peak profit-la irundhu 70% drop aana loss aagarathuku munnadiye warning varum!\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 *Quick Menu:*"
    )
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("/status"), types.KeyboardButton("/exit"))
    markup.row(types.KeyboardButton("/help"))
    
    bot.reply_to(message, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['help'])
def handle_help(message):
    save_chat(message.chat.id)
    help_text = (
        f"📖 *Trade Guardian - Commands Guide* 🛡️\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔹 *1. Morning-la Contract Track Panna:*\n"
        f"`/track SENSEX 72700 PE`\n"
        f"_(or `/track NIFTY 25000 CE`)_\n\n"
        f"🔹 *2. Buy Pannadha Register Panna:*\n"
        f"`/buy 10:36 121` _(Time & Price)_\n"
        f"or simply `/buy 121`\n\n"
        f"🔹 *3. Market Price Update Panna:*\n"
        f"Just type the price: `135` or `/price 135`\n\n"
        f"🔹 *4. Current P&L Card Paaka:*\n"
        f"`/status`\n\n"
        f"🔹 *5. Trade Close Panna:*\n"
        f"`/exit`"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['track'])
def handle_track(message):
    global current_tracked_symbol
    save_chat(message.chat.id)
    
    args = message.text.split()[1:]
    if not args:
        bot.reply_to(
            message,
            "👉 *Usage:* `/track <Contract Name>`\n"
            "_Example:_ `/track SENSEX 72700 PE`\n"
            "_Example:_ `/track NIFTY 25000 CE`"
        )
        return
        
    current_tracked_symbol = " ".join(args).strip().upper()
    
    reply = (
        f"🎯 *TRACKING ACTIVATED!* 🟢\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Contract:* `{current_tracked_symbol}`\n"
        f"👀 Bot continuous-ah chart & momentum-ah watch panren!\n\n"
        f"Alice Blue-la buy pannadhukku apram bot kitta:\n"
        f"`/buy 10:36 121` nu anupunga!"
    )
    bot.reply_to(message, reply)

@bot.message_handler(commands=['buy'])
def handle_buy(message):
    global active_position, current_tracked_symbol
    save_chat(message.chat.id)
    
    args = message.text.split()[1:]
    if not args:
        bot.reply_to(
            message,
            "👉 *Usage:* `/buy <Time> <Price>` or `/buy <Price>`\n"
            "_Example:_ `/buy 10:36 121`\n"
            "_Example:_ `/buy 121`"
        )
        return

    try:
        entry_time = None
        price = None
        qty = config.DEFAULT_SENSEX_LOT if "SENSEX" in current_tracked_symbol.upper() else config.DEFAULT_NIFTY_LOT
        symbol = current_tracked_symbol

        if len(args) == 1:
            price = float(args[0])
            entry_time = datetime.now().strftime("%H:%M")
        elif len(args) == 2:
            if ":" in args[0]:
                entry_time = args[0]
                price = float(args[1])
            else:
                price = float(args[0])
                qty = int(args[1])
                entry_time = datetime.now().strftime("%H:%M")
        elif len(args) >= 3:
            entry_time = args[0]
            price = float(args[1])
            qty = int(args[2])

        active_position = TradePosition(
            symbol=symbol,
            buy_price=price,
            qty=qty,
            entry_time=entry_time
        )
        
        reply = (
            f"🛡️ *TRADE LOGGED & GUARDIAN ON!* 🟢\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *Contract:* `{active_position.symbol}`\n"
            f"⏰ *Entry Time:* {active_position.entry_time}\n"
            f"💵 *Buy Price:* ₹{active_position.buy_price:.2f}\n"
            f"📦 *Qty:* {active_position.qty} (₹{active_position.invested_amount:,.2f})\n"
            f"🛑 *Stop Loss:* ₹{active_position.stop_loss:.2f}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 *Auto Sell Alert Targets:*\n"
            f"• +₹500 Profit (Safe exit)\n"
            f"• +₹1,000 Profit (Target 1)\n"
            f"• +₹2,000 Profit (Mass target)\n"
            f"• +₹3,000 Profit (Jackpot)\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Price update panna just type number (e.g. `135`) or `/price 135`!"
        )
        bot.reply_to(message, reply)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}\n👉 *Usage:* `/buy 10:36 121`")

@bot.message_handler(commands=['status'])
def handle_status(message):
    save_chat(message.chat.id)
    if not active_position or not active_position.is_active:
        bot.reply_to(
            message,
            f"ℹ️ *Ippo active trade illa.*\n"
            f"Current Tracked: `{current_tracked_symbol}`\n"
            f"Trade log panna: `/buy 10:36 121`"
        )
        return
    bot.reply_to(message, active_position.get_status_card())

@bot.message_handler(commands=['price'])
def handle_price(message):
    global active_position
    save_chat(message.chat.id)
    if not active_position or not active_position.is_active:
        bot.reply_to(message, "ℹ️ Active trade illa. First `/buy 10:36 121` use pannunga.")
        return
        
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "👉 *Usage:* `/price 135` (or just type `135`)")
        return
        
    try:
        new_price = float(args[1])
        alerts = active_position.update_price(new_price)
        bot.reply_to(message, f"⚡ Price updated to ₹{new_price:.2f}\n\n" + active_position.get_status_card())
        for a in alerts:
            broadcast_alert(a)
    except ValueError:
        bot.reply_to(message, "❌ Invalid price value.")

@bot.message_handler(commands=['exit', 'sell'])
def handle_exit(message):
    global active_position
    save_chat(message.chat.id)
    if not active_position or not active_position.is_active:
        bot.reply_to(message, "ℹ️ Active trade edhuvum illa.")
        return
        
    pnl, pnl_pct = active_position.calculate_metrics(active_position.current_price)
    active_position.is_active = False
    
    emoji = "🎉 PROFIT BOOKED!" if pnl >= 0 else "🛑 TRADE CLOSED"
    summary = (
        f"{emoji}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Contract:* `{active_position.symbol}`\n"
        f"⏰ *Entry Time:* {active_position.entry_time}\n"
        f"💵 *Buy Price:* ₹{active_position.buy_price:.2f}\n"
        f"⚡ *Exit Price:* ₹{active_position.current_price:.2f}\n"
        f"💰 *Final P&L:* *₹{pnl:,.2f}* ({pnl_pct:+.2f}%)\n"
        f"📈 *Peak Profit Was:* +₹{active_position.peak_pnl:,.2f}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Trade successfully closed! Adutha trade-ku `/track` use pannunga."
    )
    bot.reply_to(message, summary)
    active_position = None

# -------------------------------------------------------------
# PLAIN TEXT HANDLER (NATURAL INPUT)
# -------------------------------------------------------------

@bot.message_handler(func=lambda msg: True)
def handle_text(message):
    global active_position
    save_chat(message.chat.id)
    text = message.text.strip()

    # If user types just a number (e.g. "135" or "142.5") -> Update CMP!
    try:
        val = float(text)
        if active_position and active_position.is_active:
            alerts = active_position.update_price(val)
            bot.reply_to(message, f"⚡ Price updated to ₹{val:.2f}\n\n" + active_position.get_status_card())
            for a in alerts:
                broadcast_alert(a)
            return
        else:
            bot.reply_to(message, f"ℹ️ Active trade edhuvum illa. First `/buy 10:36 {val}` panni start pannunga.")
            return
    except ValueError:
        pass

    bot.reply_to(
        message,
        "💡 *Quick Usage:*\n"
        "• Morning Track: `/track SENSEX 72700 PE`\n"
        "• Buy Log: `/buy 10:36 121`\n"
        "• Price Update: Just type number (e.g. `135`)\n"
        "• P&L Card: `/status`\n"
        "• Exit Trade: `/exit`\n"
        "• Instructions: `/help`"
    )

if __name__ == "__main__":
    print("=" * 50)
    print("[*] Trade Guardian Bot is running (Production)...")
    print(f"[*] Milestones: {config.PROFIT_MILESTONES}")
    print("=" * 50)
    
    bot.infinity_polling()
