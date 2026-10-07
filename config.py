import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8851611658:AAHH5buvOsNUUpweW260bhtrBuzso27ALso")

# Risk & Profit Rules
# If profit was up and drops by 70% from peak gain -> TRIGGER ALERT
PEAK_DRAWDOWN_PERCENT = 70.0  

# Minimum profit % needed before peak-drawdown tracking kicks in (e.g. +5% or +₹300)
MIN_PEAK_PROFIT_PCT = 5.0  

# Once profit touches +10%, move stop loss to entry price (Zero loss guarantee)
BREAKEVEN_TRIGGER_PCT = 10.0  

# Default Initial Stop Loss % (e.g. -15% from buy price)
DEFAULT_STOP_LOSS_PCT = 15.0  

# Profit Milestones in ₹ (Alert to Sell & Book Profit)
PROFIT_MILESTONES = [500, 1000, 2000, 3000]

# Profit Targets in %
DEFAULT_TARGET_1_PCT = 25.0
DEFAULT_TARGET_2_PCT = 50.0

# Default Lots
DEFAULT_SENSEX_LOT = 20
DEFAULT_NIFTY_LOT = 25
DEFAULT_BANKNIFTY_LOT = 15
