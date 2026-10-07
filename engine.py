from datetime import datetime
import config

class TradePosition:
    def __init__(self, symbol: str, buy_price: float, qty: int = 20, entry_time: str = None, stop_loss: float = None):
        self.symbol = symbol.strip().upper()
        self.buy_price = float(buy_price)
        self.qty = int(qty)
        self.entry_time = entry_time if entry_time else datetime.now().strftime("%H:%M")
        self.invested_amount = self.buy_price * self.qty
        
        # Stop loss (default -15% or custom)
        if stop_loss is not None:
            self.stop_loss = float(stop_loss)
        else:
            self.stop_loss = round(self.buy_price * (1 - (config.DEFAULT_STOP_LOSS_PCT / 100)), 2)
            
        # Live tracking metrics
        self.current_price = self.buy_price
        self.peak_price = self.buy_price
        self.peak_profit_pct = 0.0
        self.peak_pnl = 0.0
        
        # Track milestones already triggered (e.g., 500, 1000, 2000, 3000)
        self.milestones_hit = set()
        
        # Alert state flags
        self.cost_shield_active = False
        self.warned_drawdown = False
        self.warned_near_sl = False
        self.warned_sl_hit = False
        
        self.created_at = datetime.now()
        self.is_active = True

    def calculate_metrics(self, price: float):
        self.current_price = float(price)
        pnl = (self.current_price - self.buy_price) * self.qty
        pnl_pct = ((self.current_price - self.buy_price) / self.buy_price) * 100

        # Track peaks
        if self.current_price > self.peak_price:
            self.peak_price = self.current_price
            self.peak_profit_pct = pnl_pct
            self.peak_pnl = pnl

        return pnl, pnl_pct

    def update_price(self, new_price: float):
        """
        Receives new tick price and checks for all risk/profit rules.
        Returns a list of alert messages to send if any triggered.
        """
        if not self.is_active:
            return []

        pnl, pnl_pct = self.calculate_metrics(new_price)
        alerts = []

        # ------------------------------------------------------------------
        # 1. PROFIT MILESTONES (₹500, ₹1000, ₹2000, ₹3000 SELL ALERTS)
        # ------------------------------------------------------------------
        for milestone in sorted(config.PROFIT_MILESTONES):
            if pnl >= milestone and milestone not in self.milestones_hit:
                self.milestones_hit.add(milestone)
                
                # Custom advice based on milestone
                if milestone == 500:
                    advice = "👉 *Safe Trader na ippove SELL panni ₹500 safe pannidunga!* Hold panreengana alert-ah irunga."
                    badge = "💰 PROFIT MILESTONE"
                elif milestone == 1000:
                    advice = "👉 *Nalla Profit! Ippove SELL panni ₹1,000 book pannidunga!* Profit miss aaga vidatheenga."
                    badge = "🎯 TARGET 1 HIT (+₹1,000)"
                elif milestone == 2000:
                    advice = "👉 *MASS PROFIT! +₹2,000 Vandhiruchu!* Don't be greedy, SELL panna correct time!"
                    badge = "🏆 MASS PROFIT HIT (+₹2,000)"
                else:
                    advice = "👉 *JACKPOT PROFIT! +₹3,000 Crossed!* Ippove Alice Blue-la SELL pannidunga!"
                    badge = "💎 JACKPOT PROFIT (+₹3,000+)"

                alert_msg = (
                    f"🔔 *{badge}! SELL ALERT!* 🔔\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📌 *Contract:* `{self.symbol}`\n"
                    f"⏰ *Entry Time:* {self.entry_time} @ ₹{self.buy_price:.2f}\n"
                    f"⚡ *CMP (Current):* ₹{self.current_price:.2f}\n"
                    f"💵 *Current Profit:* *+₹{pnl:,.2f}* (+{pnl_pct:.1f}%)\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"{advice}"
                )
                alerts.append(alert_msg)

        # ------------------------------------------------------------------
        # 2. 70% PEAK PROFIT DRAIN WARNING (USER'S SHIELD)
        # ------------------------------------------------------------------
        # If trade reached at least ₹400 profit and now dropped by 70% of peak profit:
        if self.peak_pnl >= 400.0:
            peak_gain = self.peak_pnl
            current_gain = pnl
            profit_loss_from_peak_pct = ((peak_gain - current_gain) / peak_gain) * 100.0

            if profit_loss_from_peak_pct >= config.PEAK_DRAWDOWN_PERCENT and not self.warned_drawdown:
                self.warned_drawdown = True
                alert_msg = (
                    f"⚠️ *PROFIT DRAIN EARLY WARNING!* 🔔\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📌 *Contract:* `{self.symbol}`\n"
                    f"📈 *Peak Profit Was:* +₹{self.peak_pnl:,.2f} (+{self.peak_profit_pct:.1f}%)\n"
                    f"📉 *Current Profit:* +₹{pnl:,.2f} (+{pnl_pct:.1f}%)\n"
                    f"🔻 *Drawdown:* Peak-la irundhu *{profit_loss_from_peak_pct:.0f}% profit drop* aayiduchu!\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🛑 *Warning:* Innum keezha pona loss aagidum!\n"
                    f"👉 *Action:* Ippove Alice Blue-la SELL panni irukra profit-a safe pannidunga!"
                )
                alerts.append(alert_msg)

        # ------------------------------------------------------------------
        # 3. COST-TO-COST SHIELD (ZERO-LOSS GUARANTEE)
        # ------------------------------------------------------------------
        if pnl_pct >= config.BREAKEVEN_TRIGGER_PCT and not self.cost_shield_active:
            self.cost_shield_active = True
            self.stop_loss = self.buy_price
            alert_msg = (
                f"🛡️ *ZERO-LOSS SHIELD ACTIVATED!* 🛡️\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 *Contract:* `{self.symbol}`\n"
                f"💵 Profit crossed +{pnl_pct:.1f}% (+₹{pnl:,.2f})\n"
                f"✅ *Stop Loss moved to Buy Price:* ₹{self.buy_price:.2f}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🎉 Super! Indha trade-la ungalukku *1 rooba kooda loss aagadhu*."
            )
            alerts.append(alert_msg)

        # ------------------------------------------------------------------
        # 4. PRE-STOP LOSS DANGER ALERT
        # ------------------------------------------------------------------
        dist_to_sl_pct = ((self.current_price - self.stop_loss) / self.buy_price) * 100
        if 0 < dist_to_sl_pct <= 3.0 and not self.warned_near_sl:
            self.warned_near_sl = True
            alert_msg = (
                f"⚠️ *EARLY RISK WARNING (Near Stop Loss)!* ⚠️\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 *Contract:* `{self.symbol}`\n"
                f"💵 *CMP:* ₹{self.current_price:.2f} | *SL:* ₹{self.stop_loss:.2f}\n"
                f"📉 *Current P&L:* ₹{pnl:,.2f} ({pnl_pct:.1f}%)\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👀 Price Stop Loss kitta vandhurukku. Alert-ah irunga!"
            )
            alerts.append(alert_msg)

        # ------------------------------------------------------------------
        # 5. STOP LOSS HIT (EMERGENCY EXIT)
        # ------------------------------------------------------------------
        if self.current_price <= self.stop_loss and not self.warned_sl_hit:
            self.warned_sl_hit = True
            alert_msg = (
                f"🚨 *STOP LOSS TRIGGERED! EMERGENCY EXIT!* 🚨\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 *Contract:* `{self.symbol}`\n"
                f"💵 *CMP:* ₹{self.current_price:.2f} (SL: ₹{self.stop_loss:.2f})\n"
                f"🛑 *Total Loss:* ₹{pnl:,.2f} ({pnl_pct:.1f}%)\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👉 Periya loss aagama iruka *IPPOVE ALICE BLUE-LA SELL PANNIDUNGA!*"
            )
            alerts.append(alert_msg)

        return alerts

    def get_status_card(self) -> str:
        pnl = (self.current_price - self.buy_price) * self.qty
        pnl_pct = ((self.current_price - self.buy_price) / self.buy_price) * 100
        pnl_emoji = "🟢" if pnl >= 0 else "🔴"
        shield_icon = "🛡️ ON (Zero-Loss)" if self.cost_shield_active else "⏳ Waiting (+10% needed)"

        card = (
            f"📊 *LIVE TRADE STATUS* {pnl_emoji}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *Contract:* `{self.symbol}`\n"
            f"⏰ *Entry Time:* {self.entry_time} | *Buy Price:* ₹{self.buy_price:.2f}\n"
            f"📦 *Qty:* {self.qty} | *Invested:* ₹{self.invested_amount:,.2f}\n"
            f"⚡ *CMP (Current):* ₹{self.current_price:.2f}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{pnl_emoji} *P&L:* *₹{pnl:,.2f}* ({pnl_pct:+.2f}%)\n"
            f"📈 *Peak High:* ₹{self.peak_price:.2f} (+₹{self.peak_pnl:,.2f})\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🛑 *Stop Loss:* ₹{self.stop_loss:.2f}\n"
            f"🛡️ *Cost Shield:* {shield_icon}\n"
            f"🎯 *Next Sell Milestone:* ₹{self._next_milestone(pnl)}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 *Milestones:* ₹500, ₹1000, ₹2000, ₹3000 Sell Alerts ON!"
        )
        return card

    def _next_milestone(self, pnl: float) -> str:
        for m in sorted(config.PROFIT_MILESTONES):
            if pnl < m:
                needed = m - pnl
                return f"+₹{m} (innum ₹{needed:,.0f} needed)"
        return "All Milestones Achieved! 🏆"
