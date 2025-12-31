# -*- coding: utf-8 -*-
"""
S&P 500 Professional Trading Bot - Full Day Coverage
=====================================================
Comprehensive Telegram bot with scheduled messages throughout the trading day.

Schedule (ET / Morocco WET):
- 8:00 AM  / 2:00 PM  - Market Opening Update
- 10:00 AM / 4:00 PM  - First Signal Update
- 12:00 PM / 6:00 PM  - Mid-Day Review
- 3:00 PM  / 9:00 PM  - Pre-Close Signal Update
- 5:00 PM  / 11:00 PM - End of Day Summary
- 7:00 PM  / 1:00 AM  - Late Night Update (optional)
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import warnings
import json
import pytz
warnings.filterwarnings('ignore')

# Configuration
TELEGRAM_BOT_TOKEN = "7125291296:AAFG1rkGILb22CVnYSr3UEmUxXg_8ikcHMQ"
TELEGRAM_CHAT_ID = "@lkiwanSP500"

# Time zones
ET_TIMEZONE = pytz.timezone('US/Eastern')
MOROCCO_TIMEZONE = pytz.timezone('Africa/Casablanca')

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREDICTIONS_FILE = os.path.join(BASE_DIR, 'predictions_with_accuracy.csv')
PREDICTIONS_HISTORY = os.path.join(BASE_DIR, 'predictions_history.csv')
SIGNALS_DIR = os.path.join(BASE_DIR, 'data', 'trading_signals')
SIGNALS_FILE = os.path.join(SIGNALS_DIR, 'signals_history.csv')
PRICE_DATA_FILE = os.path.join(BASE_DIR, 'data', 'raw', 'price_data.csv')
FEATURES_FILE = os.path.join(BASE_DIR, 'data', 'features', 'features_complete.csv')

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def send_telegram_message(text, parse_mode="HTML"):
    """Send a text message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=30, verify=False)
        if response.status_code == 200:
            print(f"[OK] Message sent successfully")
            return True
        else:
            print(f"[ERROR] Failed to send: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def get_current_time_et():
    """Get current time in Eastern Time"""
    return datetime.now(ET_TIMEZONE)


def get_current_time_morocco():
    """Get current time in Morocco"""
    return datetime.now(MOROCCO_TIMEZONE)


def format_date_display():
    """Format date for display"""
    now_et = get_current_time_et()
    return now_et.strftime("%B %d, %Y")


def get_price_data(days=30):
    """Load recent price data"""
    try:
        df = pd.read_csv(PRICE_DATA_FILE)
        # Standardize column names
        df.columns = [c.capitalize() if c.lower() in ['open', 'high', 'low', 'close', 'volume', 'date'] else c for c in df.columns]
        if 'Date' not in df.columns and 'date' in df.columns:
            df.rename(columns={'date': 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date'], format='mixed')
        df = df.sort_values('Date').tail(days)
        return df
    except Exception as e:
        print(f"Error loading price data: {e}")
        return pd.DataFrame()


def get_latest_prediction():
    """Get the latest prediction"""
    try:
        if os.path.exists(PREDICTIONS_FILE):
            df = pd.read_csv(PREDICTIONS_FILE)
        elif os.path.exists(PREDICTIONS_HISTORY):
            df = pd.read_csv(PREDICTIONS_HISTORY)
        else:
            return None

        if df.empty:
            return None

        latest = df.iloc[-1]
        return {
            'date': latest.get('prediction_date', latest.get('data_date', 'N/A')),
            'direction': latest.get('predicted_direction', latest.get('direction', 'N/A')),
            'confidence': float(latest.get('confidence', 0.5)),
            'actual_return': float(latest.get('actual_return', 0)) if 'actual_return' in latest else None,
            'is_correct': latest.get('is_correct', None),
            'current_price': float(latest.get('current_price', 0)) if 'current_price' in latest else None,
            'next_price': float(latest.get('next_price', 0)) if 'next_price' in latest else None
        }
    except Exception as e:
        print(f"Error loading prediction: {e}")
        return None


def get_latest_signal():
    """Get the latest trading signal with TP/SL"""
    try:
        if os.path.exists(SIGNALS_FILE):
            df = pd.read_csv(SIGNALS_FILE)
            if not df.empty:
                latest = df.iloc[-1]
                return {
                    'signal_id': int(latest.get('signal_id', 0)),
                    'direction': latest.get('direction', 'N/A'),
                    'entry_price': float(latest.get('entry_price', 0)),
                    'take_profit': float(latest.get('take_profit', 0)),
                    'stop_loss': float(latest.get('stop_loss', 0)),
                    'confidence': float(latest.get('confidence', 0.5)),
                    'risk_reward': float(latest.get('risk_reward', 0)),
                    'atr': float(latest.get('atr', 0)),
                    'status': latest.get('status', 'ACTIVE'),
                    'outcome': latest.get('outcome', 'PENDING'),
                    'signal_date': latest.get('signal_date', 'N/A')
                }
        return None
    except Exception as e:
        print(f"Error loading signal: {e}")
        return None


def get_active_signals():
    """Get all active signals"""
    try:
        if os.path.exists(SIGNALS_FILE):
            df = pd.read_csv(SIGNALS_FILE)
            active = df[df['status'] == 'ACTIVE']
            return active.to_dict('records')
        return []
    except:
        return []


def get_performance_stats():
    """Get performance statistics"""
    try:
        if os.path.exists(SIGNALS_FILE):
            df = pd.read_csv(SIGNALS_FILE)
            completed = df[df['outcome'].isin(['WIN', 'LOSS'])]

            if len(completed) == 0:
                return {
                    'total_signals': len(df),
                    'wins': 0,
                    'losses': 0,
                    'win_rate': 0,
                    'avg_pnl': 0,
                    'total_pnl': 0
                }

            wins = len(completed[completed['outcome'] == 'WIN'])
            losses = len(completed[completed['outcome'] == 'LOSS'])
            win_rate = (wins / len(completed)) * 100 if len(completed) > 0 else 0

            # Calculate P&L
            completed['pnl_percent'] = pd.to_numeric(completed['pnl_percent'], errors='coerce').fillna(0)
            avg_pnl = completed['pnl_percent'].mean()
            total_pnl = completed['pnl_percent'].sum()

            return {
                'total_signals': len(df),
                'completed': len(completed),
                'wins': wins,
                'losses': losses,
                'win_rate': round(win_rate, 1),
                'avg_pnl': round(avg_pnl, 2),
                'total_pnl': round(total_pnl, 2)
            }
        return None
    except Exception as e:
        print(f"Error getting stats: {e}")
        return None


def get_current_market_price():
    """Get current market price (latest available)"""
    df = get_price_data(5)
    if not df.empty:
        return float(df['Close'].iloc[-1])
    return None


def calculate_atr(df, period=14):
    """Calculate ATR"""
    if len(df) < period:
        return 0

    high = df['High']
    low = df['Low']
    close = df['Close']

    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean().iloc[-1]

    return float(atr) if not pd.isna(atr) else 0


def get_volatility_level(atr, price):
    """Determine volatility level"""
    if price == 0:
        return "Unknown"

    atr_pct = (atr / price) * 100

    if atr_pct < 0.8:
        return "Low"
    elif atr_pct < 1.5:
        return "Moderate"
    elif atr_pct < 2.5:
        return "High"
    else:
        return "Very High"


def get_confidence_tier(confidence):
    """Get confidence tier description"""
    if confidence >= 0.85:
        return ("VERY STRONG", "🔥🔥🔥")
    elif confidence >= 0.75:
        return ("STRONG", "🔥🔥")
    elif confidence >= 0.65:
        return ("MODERATE", "✅")
    elif confidence >= 0.55:
        return ("WEAK", "⚠️")
    else:
        return ("VERY WEAK", "❌")


# ============================================================================
# MESSAGE FUNCTIONS
# ============================================================================

def post_market_opening_update():
    """
    1. Market Opening Update (8:00 AM ET / 2:00 PM Morocco)
    """
    print("\n" + "="*60)
    print("Posting Market Opening Update...")
    print("="*60)

    date_str = format_date_display()
    prediction = get_latest_prediction()
    price_data = get_price_data(30)

    if prediction is None:
        print("No prediction data available")
        return False

    # Get current price and ATR
    current_price = get_current_market_price()
    atr = calculate_atr(price_data) if not price_data.empty else 0
    volatility = get_volatility_level(atr, current_price) if current_price else "Unknown"

    # Direction and confidence
    direction = prediction['direction']
    confidence = prediction['confidence']
    conf_tier, conf_emoji = get_confidence_tier(confidence)

    # Market sentiment based on recent performance
    if not price_data.empty:
        recent_return = ((price_data['Close'].iloc[-1] / price_data['Close'].iloc[-5]) - 1) * 100
        if recent_return > 1:
            sentiment = "Bullish momentum detected"
        elif recent_return < -1:
            sentiment = "Bearish pressure observed"
        else:
            sentiment = "Neutral/Consolidating"
    else:
        sentiment = "Market data unavailable"

    # Build message
    arrow = "📈" if direction == "UP" else "📉"
    direction_text = "BULLISH" if direction == "UP" else "BEARISH"

    msg = f"""
{arrow}{arrow}{arrow} <b>MARKET OPENING UPDATE</b> {arrow}{arrow}{arrow}
<b>{date_str}</b>

Good day traders! The market is opening, and our AI model has analyzed the data. Here are the key takeaways for today:

🔮 <b>Market Outlook for the Day:</b>
• {sentiment}
• <b>Overall Direction:</b> {direction_text} {arrow}
• <b>Confidence:</b> {conf_tier} {conf_emoji} ({confidence*100:.1f}%)
• <b>Volatility:</b> {volatility} (ATR: {atr:.2f})

💰 <b>Current Price:</b> <code>${current_price:,.2f}</code>

Stay tuned for our first signal update at 10:00 AM ET (4:00 PM Morocco)!

⏰ <b>Schedule Today:</b>
• 10:00 AM ET - First Signal
• 12:00 PM ET - Mid-Day Review
• 3:00 PM ET - Pre-Close Update
• 5:00 PM ET - End of Day Summary

Let's trade smartly today! 💪

#SP500 #TradingSignals #MarketUpdate #DayTrading
"""

    return send_telegram_message(msg)


def post_first_signal_update():
    """
    2. First Signal Update (10:00 AM ET / 4:00 PM Morocco)
    Only posts signal if confidence > 60%, otherwise posts "No Signal Today"
    """
    print("\n" + "="*60)
    print("Posting First Signal Update...")
    print("="*60)

    date_str = format_date_display()
    prediction = get_latest_prediction()
    signal = get_latest_signal()
    current_price = get_current_market_price()

    if prediction is None:
        print("No prediction data available")
        return False

    direction = prediction['direction']
    confidence = prediction['confidence']
    conf_tier, conf_emoji = get_confidence_tier(confidence)

    # Minimum confidence threshold
    MIN_CONFIDENCE = 0.60

    # Check if confidence is high enough
    if confidence < MIN_CONFIDENCE:
        print(f"Confidence {confidence*100:.1f}% < 60% - No signal today")

        # Post "No Signal Today" message
        msg = f"""
⏸️⏸️⏸️ <b>NO SIGNAL TODAY</b> ⏸️⏸️⏸️

📅 <b>S&P 500 - {date_str}</b>

━━━━━━━━━━━━━━━━━━━━━━

🔍 Our AI model has analyzed the market, but the confidence level is below our 60% threshold.

━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Current Analysis:</b>

   💰 Price: <code>${current_price:,.2f}</code>
   🎯 Model Prediction: {direction}
   📉 Confidence: <code>{confidence*100:.1f}%</code>
   ⚠️ Status: <b>Below 60% minimum</b>

━━━━━━━━━━━━━━━━━━━━━━

🛡️ <b>Why No Signal?</b>

When confidence is below 60%, the risk/reward is not favorable. We prioritize:

   ✅ Quality over quantity
   ✅ Protecting your capital
   ✅ Waiting for better setups

━━━━━━━━━━━━━━━━━━━━━━

💡 <b>What This Means:</b>

   🔸 Market conditions are unclear
   🔸 Mixed signals from indicators
   🔸 Better to stay on the sidelines

━━━━━━━━━━━━━━━━━━━━━━

📈 <b>Today's Recommendation:</b>

   🚫 No new positions today
   👀 Watch and observe
   ⏳ Wait for stronger setup

━━━━━━━━━━━━━━━━━━━━━━

💬 <i>"The best trade is sometimes no trade at all."</i>

Stay patient, stay disciplined! 💪🧘

#NoSignal #RiskManagement #SP500 #Patience #Trading
"""
        return send_telegram_message(msg)

    # Confidence >= 60% - Post the signal
    print(f"Confidence {confidence*100:.1f}% >= 60% - Posting signal")

    # Determine action
    is_long = direction == "UP"
    action_emoji = "🟢" if is_long else "🔴"
    action = "BUY (LONG)" if is_long else "SELL (SHORT)"
    trend_emoji = "📈🚀" if is_long else "📉💥"

    # Build message
    msg = f"""
{action_emoji}{action_emoji}{action_emoji} <b>TRADING SIGNAL</b> {action_emoji}{action_emoji}{action_emoji}

📅 <b>S&P 500 - {date_str}</b>

━━━━━━━━━━━━━━━━━━━━━━

🎯 <b>SIGNAL: {action}</b> {trend_emoji}

━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Signal Details:</b>

   🕒 Entry Price: <code>${signal['entry_price']:,.2f}</code>
   {trend_emoji} Direction: <b>{"BULLISH 📈" if is_long else "BEARISH 📉"}</b>
   💪 Confidence: {conf_tier} {conf_emoji} <code>{confidence*100:.1f}%</code>

━━━━━━━━━━━━━━━━━━━━━━
"""

    if signal:
        tp_distance = abs(signal['take_profit'] - signal['entry_price']) / signal['entry_price'] * 100
        sl_distance = abs(signal['entry_price'] - signal['stop_loss']) / signal['entry_price'] * 100

        msg += f"""
🎯 <b>Trading Levels:</b>

   ✅ Take Profit: <code>${signal['take_profit']:,.2f}</code> (+{tp_distance:.2f}%)
   ❌ Stop Loss: <code>${signal['stop_loss']:,.2f}</code> (-{sl_distance:.2f}%)

   📊 Risk/Reward: <code>{signal['risk_reward']:.2f}</code>
   💨 Volatility (ATR): <code>{signal['atr']:.2f}</code>

━━━━━━━━━━━━━━━━━━━━━━
"""

    msg += f"""
⚠️ <b>Risk Management:</b>

   💼 Position size: Max 2% of portfolio
   🛑 Always use stop loss
   🧘 Don't overtrade

━━━━━━━━━━━━━━━━━━━━━━

🔮 <b>Outlook:</b>

We are expecting a <b>{"bullish 📈" if is_long else "bearish 📉"}</b> move today!

⏰ Next update: 12:00 PM ET (6:00 PM Morocco)

━━━━━━━━━━━━━━━━━━━━━━

💪 <i>Trade smart, manage risk!</i>

#SignalUpdate #TradingSignal #SP500 #{action.split()[0]} #Trading
"""

    return send_telegram_message(msg)


def post_midday_review():
    """
    3. Mid-Day Review (12:00 PM ET / 6:00 PM Morocco)
    """
    print("\n" + "="*60)
    print("Posting Mid-Day Review...")
    print("="*60)

    date_str = format_date_display()
    signal = get_latest_signal()
    current_price = get_current_market_price()

    if signal is None or current_price is None:
        print("No signal or price data available")
        return False

    # Calculate current P&L
    entry = signal['entry_price']
    is_long = signal['direction'] == 'LONG'

    if is_long:
        current_pnl = ((current_price - entry) / entry) * 100
    else:
        current_pnl = ((entry - current_price) / entry) * 100

    pnl_emoji = "🟢" if current_pnl > 0 else "🔴" if current_pnl < 0 else "⚪"

    # Check TP/SL status
    tp = signal['take_profit']
    sl = signal['stop_loss']

    if is_long:
        tp_status = "HIT ✅" if current_price >= tp else f"Pending ({((tp - current_price) / current_price * 100):.2f}% away)"
        sl_status = "HIT ❌" if current_price <= sl else f"Safe ({((current_price - sl) / current_price * 100):.2f}% away)"
    else:
        tp_status = "HIT ✅" if current_price <= tp else f"Pending ({((current_price - tp) / current_price * 100):.2f}% away)"
        sl_status = "HIT ❌" if current_price >= sl else f"Safe ({((sl - current_price) / current_price * 100):.2f}% away)"

    msg = f"""
🔍 <b>MID-DAY REVIEW</b>
<b>{date_str}</b>

Here's a quick recap of how our signal is performing so far:

📈 <b>Signal Performance:</b>

<b>S&P 500 {signal['direction']}</b>
• Entry Price: <code>${entry:,.2f}</code>
• Current Price: <code>${current_price:,.2f}</code>
• {pnl_emoji} Current P&L: <code>{current_pnl:+.2f}%</code>

<b>Target Status:</b>
• TP (${tp:,.2f}): {tp_status}
• SL (${sl:,.2f}): {sl_status}

📝 <b>Market Commentary:</b>
{"The trade is in profit! Consider trailing your stop loss." if current_pnl > 0.5 else "The trade is slightly negative. Monitor closely but stick to your plan." if current_pnl < -0.3 else "The trade is near breakeven. Patience is key."}

⏰ <b>Remaining Schedule:</b>
• 3:00 PM ET - Pre-Close Update
• 5:00 PM ET - End of Day Summary

Stay disciplined and manage your risk! 💪

#MidDayReview #MarketRecap #TradingPerformance
"""

    return send_telegram_message(msg)


def post_preclose_update():
    """
    4. Pre-Close Signal Update (3:00 PM ET / 9:00 PM Morocco)
    """
    print("\n" + "="*60)
    print("Posting Pre-Close Update...")
    print("="*60)

    date_str = format_date_display()
    signal = get_latest_signal()
    prediction = get_latest_prediction()
    current_price = get_current_market_price()

    if signal is None or current_price is None:
        print("No data available")
        return False

    # Calculate current P&L
    entry = signal['entry_price']
    is_long = signal['direction'] == 'LONG'

    if is_long:
        current_pnl = ((current_price - entry) / entry) * 100
    else:
        current_pnl = ((entry - current_price) / entry) * 100

    # Status determination
    tp = signal['take_profit']
    sl = signal['stop_loss']

    if is_long:
        if current_price >= tp:
            status = "TP HIT ✅"
            status_msg = "Take Profit reached! Great trade!"
        elif current_price <= sl:
            status = "SL HIT ❌"
            status_msg = "Stop Loss triggered. Part of trading."
        else:
            status = "IN PROGRESS ⏳"
            status_msg = "Trade still active. Monitor into close."
    else:
        if current_price <= tp:
            status = "TP HIT ✅"
            status_msg = "Take Profit reached! Great trade!"
        elif current_price >= sl:
            status = "SL HIT ❌"
            status_msg = "Stop Loss triggered. Part of trading."
        else:
            status = "IN PROGRESS ⏳"
            status_msg = "Trade still active. Monitor into close."

    msg = f"""
⚠️ <b>PRE-CLOSE SIGNAL UPDATE</b>
<b>{date_str}</b>

It's almost time for market close! Here's the current status:

📊 <b>Active Signal Status:</b>

<b>S&P 500 {signal['direction']}</b>
• Entry: <code>${entry:,.2f}</code>
• Current: <code>${current_price:,.2f}</code>
• P&L: <code>{current_pnl:+.2f}%</code>
• Status: <b>{status}</b>

💬 {status_msg}

🔮 <b>Tomorrow's Outlook:</b>
{"Our model is analyzing data for tomorrow's prediction. Stay tuned for the End of Day summary!" if prediction else "Prediction will be available after market close."}

⏰ <b>Time Until Close:</b> ~1 hour

<b>Action Items:</b>
• Review your positions
• Set alerts for TP/SL levels
• Prepare for tomorrow's session

Final summary coming at 5:00 PM ET!

#PreCloseUpdate #MarketSignal #EndOfDayPrep
"""

    return send_telegram_message(msg)


def post_end_of_day_summary():
    """
    5. End of Day Summary (5:00 PM ET / 11:00 PM Morocco)
    """
    print("\n" + "="*60)
    print("Posting End of Day Summary...")
    print("="*60)

    date_str = format_date_display()
    signal = get_latest_signal()
    stats = get_performance_stats()
    prediction = get_latest_prediction()
    price_data = get_price_data(5)

    if signal is None:
        print("No signal data available")
        return False

    # Get final price
    final_price = get_current_market_price()
    entry = signal['entry_price']
    is_long = signal['direction'] == 'LONG'

    # Calculate final P&L
    if is_long:
        final_pnl = ((final_price - entry) / entry) * 100
    else:
        final_pnl = ((entry - final_price) / entry) * 100

    # Determine outcome
    tp = signal['take_profit']
    sl = signal['stop_loss']

    if is_long:
        if final_price >= tp:
            outcome = "TP HIT ✅ WIN"
            result_emoji = "🎉"
        elif final_price <= sl:
            outcome = "SL HIT ❌ LOSS"
            result_emoji = "😔"
        else:
            outcome = "EXPIRED ⏳"
            result_emoji = "📊"
    else:
        if final_price <= tp:
            outcome = "TP HIT ✅ WIN"
            result_emoji = "🎉"
        elif final_price >= sl:
            outcome = "SL HIT ❌ LOSS"
            result_emoji = "😔"
        else:
            outcome = "EXPIRED ⏳"
            result_emoji = "📊"

    msg = f"""
🏁 <b>END OF DAY SUMMARY</b>
<b>{date_str}</b>

Today's trading session has come to an end! Here's the full recap:

{result_emoji} <b>Today's Signal Result:</b>

<b>S&P 500 {signal['direction']}</b>
• Entry Price: <code>${entry:,.2f}</code>
• Final Price: <code>${final_price:,.2f}</code>
• P&L: <code>{final_pnl:+.2f}%</code>
• <b>Outcome: {outcome}</b>
"""

    if stats:
        msg += f"""
📊 <b>Overall Model Performance:</b>
• Total Signals: {stats['total_signals']}
• Completed: {stats['completed']}
• Wins: {stats['wins']} | Losses: {stats['losses']}
• Win Rate: <code>{stats['win_rate']:.1f}%</code>
• Avg P&L per trade: <code>{stats['avg_pnl']:+.2f}%</code>
• Total P&L: <code>{stats['total_pnl']:+.2f}%</code>
"""

    # Tomorrow's outlook
    if prediction:
        next_direction = prediction['direction']
        next_conf = prediction['confidence']
        conf_tier, conf_emoji = get_confidence_tier(next_conf)

        msg += f"""
📈 <b>Looking Ahead (Tomorrow):</b>
• Expected Direction: {"BULLISH 📈" if next_direction == "UP" else "BEARISH 📉"}
• Confidence: {conf_tier} {conf_emoji} ({next_conf*100:.1f}%)
• New signal will be posted at market open!
"""

    msg += f"""
Thanks for following along today! We'll be back with more signals tomorrow.

🌙 Good night traders!

#EndOfDay #TradingSummary #MarketRecap #SP500
"""

    return send_telegram_message(msg)


def post_late_night_update():
    """
    6. Late Night Update (7:00 PM ET / 1:00 AM Morocco) - Optional
    """
    print("\n" + "="*60)
    print("Posting Late Night Update...")
    print("="*60)

    date_str = format_date_display()
    prediction = get_latest_prediction()
    stats = get_performance_stats()

    msg = f"""
🌙 <b>LATE NIGHT UPDATE</b>
<b>{date_str}</b>

As we wrap up the trading day, here's one final alert:

📝 <b>Key Takeaways from Today:</b>
"""

    if stats:
        if stats['win_rate'] >= 60:
            msg += "• Model performance remains strong 💪\n"
        else:
            msg += "• Market conditions were challenging today 📊\n"

    if prediction:
        direction = prediction['direction']
        confidence = prediction['confidence']

        msg += f"""
🔮 <b>Tomorrow's Preliminary Outlook:</b>
• Direction: {"BULLISH 📈" if direction == "UP" else "BEARISH 📉"}
• Confidence: {confidence*100:.1f}%
• Full signal at 10:00 AM ET tomorrow
"""

    msg += """
⚠️ <b>Reminders:</b>
• Review your trades from today
• Set up price alerts for tomorrow
• Get adequate rest before the next session

See you tomorrow at market open! 💤

#LateNightUpdate #MarketAlert #TradingReminder
"""

    return send_telegram_message(msg)


# ============================================================================
# SCHEDULER
# ============================================================================

def check_and_post():
    """Check current time and post appropriate message"""
    now_et = get_current_time_et()
    hour = now_et.hour
    minute = now_et.minute
    weekday = now_et.weekday()

    print(f"\nCurrent time (ET): {now_et.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Day of week: {weekday} (0=Mon, 6=Sun)")

    # Skip weekends
    if weekday >= 5:
        print("Weekend - no messages")
        return None

    # Define time windows (hour, minute_start, minute_end, function)
    schedule = [
        (8, 0, 15, "market_opening", post_market_opening_update),
        (10, 0, 15, "first_signal", post_first_signal_update),
        (12, 0, 15, "midday_review", post_midday_review),
        (15, 0, 15, "preclose", post_preclose_update),
        (17, 0, 15, "end_of_day", post_end_of_day_summary),
        (19, 0, 15, "late_night", post_late_night_update),
    ]

    for sched_hour, min_start, min_end, name, func in schedule:
        if hour == sched_hour and min_start <= minute <= min_end:
            print(f"Time for: {name}")
            return func()

    print(f"No scheduled message for {hour}:{minute:02d}")
    return None


def run_specific_message(message_type):
    """Run a specific message type"""
    message_map = {
        "opening": post_market_opening_update,
        "signal": post_first_signal_update,
        "midday": post_midday_review,
        "preclose": post_preclose_update,
        "summary": post_end_of_day_summary,
        "night": post_late_night_update,
    }

    if message_type in message_map:
        return message_map[message_type]()
    else:
        print(f"Unknown message type: {message_type}")
        print(f"Available: {', '.join(message_map.keys())}")
        return False


def run_all_test():
    """Send all messages for testing"""
    print("\n" + "="*60)
    print("RUNNING ALL MESSAGES (TEST MODE)")
    print("="*60)

    messages = [
        ("Market Opening", post_market_opening_update),
        ("First Signal", post_first_signal_update),
        ("Mid-Day Review", post_midday_review),
        ("Pre-Close Update", post_preclose_update),
        ("End of Day Summary", post_end_of_day_summary),
        ("Late Night Update", post_late_night_update),
    ]

    for name, func in messages:
        print(f"\n>>> Sending: {name}")
        input("Press Enter to send...")
        func()
        print(f"<<< {name} sent")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("S&P 500 PROFESSIONAL TELEGRAM BOT")
    print("="*60)

    now_et = get_current_time_et()
    now_morocco = get_current_time_morocco()
    print(f"Current Time (ET):      {now_et.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Current Time (Morocco): {now_morocco.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == "check":
            # Check time and send appropriate message
            check_and_post()
        elif cmd == "test":
            # Interactive test all messages
            run_all_test()
        elif cmd in ["opening", "signal", "midday", "preclose", "summary", "night"]:
            # Send specific message
            run_specific_message(cmd)
        elif cmd == "help":
            print("""
Usage: python telegram_bot_pro.py [command]

Commands:
  check     - Check time and send scheduled message
  opening   - Send Market Opening Update
  signal    - Send First Signal Update
  midday    - Send Mid-Day Review
  preclose  - Send Pre-Close Update
  summary   - Send End of Day Summary
  night     - Send Late Night Update
  test      - Interactive test (all messages)
  help      - Show this help
            """)
        else:
            print(f"Unknown command: {cmd}")
            print("Use 'help' for available commands")
    else:
        # Default: check and post
        check_and_post()
