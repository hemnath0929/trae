# 🛡️ Trade Guardian - Options Assistant & Profit Guardian

24/7 Cloud Telegram Assistant for **Sensex & Nifty Options (F&O)** traders.

---

## 🌅 Daily Morning-to-Evening Workflow

### 1. Morning Setup (9:00 AM - 10:00 AM)
Tell the bot which contract you are watching:
```text
/track SENSEX 72700 PE
```
* The bot activates tracking for this contract.

### 2. Enter Trade in Alice Blue & Log Entry
Once you execute the trade in Alice Blue, reply to the bot with your execution time & price:
```text
/buy 10:36 121
```
*(Example: Bought at 10:36 AM at ₹121 price point)*

### 3. Update Live Market Price
Simply type the price number in Telegram chat:
```text
135
```
*(Or `/price 135`)*

### 4. Automatic Sell Notifications & Profit Milestones
During the trade, the bot continuously calculates your P&L:
* **+₹500 Profit:** 💰 `SELL ALERT: Safe profit achieved, book now or hold!`
* **+₹1,000 Profit:** 🎯 `TARGET 1 HIT: Great profit! Sell to lock in ₹1,000!`
* **+₹2,000 Profit:** 🏆 `MASS PROFIT HIT: Excellent gain, sell now!`
* **+₹3,000+ Profit:** 💎 `JACKPOT HIT: Peak profit, exit immediately!`

### 5. 70% Profit Drain Early Warning
* If profit climbed to e.g. **+₹1,000** and starts falling towards **+₹300** (losing 70% of peak gain), the bot sounds an immediate **⚠️ PROFIT DRAIN WARNING** before your trade turns into a loss!

### 6. Cost-to-Cost Zero-Loss Shield
* Once profit touches **+10%**, Stop Loss is automatically moved to your entry price (₹121). Your capital is protected.

---

## ⚡ Quick Telegram Commands (`@Trading_phs_bot`)

| Command | Usage | Description |
|---|---|---|
| `/track <Contract>` | `/track SENSEX 72700 PE` | Start watching contract |
| `/buy <Time> <Price>` | `/buy 10:36 121` | Log entry time and price point |
| `<Number>` or `/price <Val>` | `135` or `/price 135` | Quick update market price |
| `/status` | `/status` | View live P&L card & next milestone |
| `/exit` | `/exit` | Close trade & view final summary |
| `/help` | `/help` | Complete help guide |
