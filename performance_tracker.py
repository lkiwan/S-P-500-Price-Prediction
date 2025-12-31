# -*- coding: utf-8 -*-
"""
S&P 500 Performance Tracker
============================
- Tracks all signals with $1000 starting balance
- Records wins/losses based on TP/SL hits
- Posts daily performance summary to Telegram
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import requests
import warnings
warnings.filterwarnings('ignore')

# Configuration
TELEGRAM_BOT_TOKEN = "7125291296:AAFG1rkGILb22CVnYSr3UEmUxXg_8ikcHMQ"
TELEGRAM_CHAT_ID = "@lkiwanSP500"
STARTING_BALANCE = 1000.0
RISK_PER_TRADE = 0.02  # Risk 2% per trade

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRADES_FILE = os.path.join(BASE_DIR, 'trades_history.csv')
PERFORMANCE_FILE = os.path.join(BASE_DIR, 'performance_summary.csv')


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
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def init_trades_file():
    """Initialize trades history file if it doesn't exist"""
    if not os.path.exists(TRADES_FILE):
        df = pd.DataFrame(columns=[
            'date', 'signal_type', 'entry_price', 'take_profit', 'stop_loss',
            'confidence', 'status', 'exit_price', 'exit_date', 'pnl_percent',
            'pnl_dollars', 'balance_after'
        ])
        df.to_csv(TRADES_FILE, index=False)
        print(f"Created trades history file: {TRADES_FILE}")
    return pd.read_csv(TRADES_FILE)


def get_current_balance():
    """Get current balance from trades history"""
    df = init_trades_file()
    if df.empty or 'balance_after' not in df.columns:
        return STARTING_BALANCE

    completed = df[df['status'] == 'CLOSED']
    if completed.empty:
        return STARTING_BALANCE

    return float(completed.iloc[-1]['balance_after'])


def record_signal(signal_type, entry_price, take_profit, stop_loss, confidence):
    """Record a new signal to trades history"""
    df = init_trades_file()

    new_trade = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'signal_type': signal_type.upper(),
        'entry_price': entry_price,
        'take_profit': take_profit,
        'stop_loss': stop_loss,
        'confidence': confidence,
        'status': 'OPEN',
        'exit_price': None,
        'exit_date': None,
        'pnl_percent': None,
        'pnl_dollars': None,
        'balance_after': None
    }

    df = pd.concat([df, pd.DataFrame([new_trade])], ignore_index=True)
    df.to_csv(TRADES_FILE, index=False)
    print(f"Recorded new {signal_type} signal at ${entry_price}")
    return True


def get_sp500_price():
    """Get current S&P 500 price"""
    try:
        ticker = yf.Ticker("^GSPC")
        data = ticker.history(period="1d")
        if not data.empty:
            return float(data['Close'].iloc[-1])
    except Exception as e:
        print(f"Error getting price: {e}")
    return None


def check_open_trades():
    """Check open trades and close them if TP/SL hit"""
    df = init_trades_file()

    open_trades = df[df['status'] == 'OPEN']
    if open_trades.empty:
        print("No open trades")
        return

    current_price = get_sp500_price()
    if not current_price:
        print("Could not get current price")
        return

    print(f"Current S&P 500 price: ${current_price:,.2f}")

    current_balance = get_current_balance()

    for idx, trade in open_trades.iterrows():
        entry = float(trade['entry_price'])
        tp = float(trade['take_profit'])
        sl = float(trade['stop_loss'])
        signal_type = trade['signal_type']

        result = None
        exit_price = None

        if signal_type == 'BUY':
            if current_price >= tp:
                result = 'WIN'
                exit_price = tp
            elif current_price <= sl:
                result = 'LOSS'
                exit_price = sl
        else:  # SELL
            if current_price <= tp:
                result = 'WIN'
                exit_price = tp
            elif current_price >= sl:
                result = 'LOSS'
                exit_price = sl

        if result:
            # Calculate P&L
            if signal_type == 'BUY':
                pnl_percent = ((exit_price - entry) / entry) * 100
            else:
                pnl_percent = ((entry - exit_price) / entry) * 100

            # Calculate dollar P&L (using 2% risk per trade)
            risk_amount = current_balance * RISK_PER_TRADE
            if result == 'WIN':
                # Use risk/reward ratio
                risk_reward = abs(tp - entry) / abs(entry - sl)
                pnl_dollars = risk_amount * risk_reward
            else:
                pnl_dollars = -risk_amount

            new_balance = current_balance + pnl_dollars

            # Update trade
            df.loc[idx, 'status'] = 'CLOSED'
            df.loc[idx, 'exit_price'] = exit_price
            df.loc[idx, 'exit_date'] = datetime.now().strftime('%Y-%m-%d')
            df.loc[idx, 'pnl_percent'] = round(pnl_percent, 2)
            df.loc[idx, 'pnl_dollars'] = round(pnl_dollars, 2)
            df.loc[idx, 'balance_after'] = round(new_balance, 2)

            current_balance = new_balance

            print(f"Trade closed: {result} | P&L: ${pnl_dollars:+.2f} | Balance: ${new_balance:,.2f}")

    df.to_csv(TRADES_FILE, index=False)


def get_performance_stats():
    """Calculate overall performance statistics"""
    df = init_trades_file()

    closed = df[df['status'] == 'CLOSED']

    if closed.empty:
        return {
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'current_balance': STARTING_BALANCE,
            'total_return': 0
        }

    wins = len(closed[closed['pnl_dollars'] > 0])
    losses = len(closed[closed['pnl_dollars'] <= 0])
    total_trades = len(closed)

    current_balance = get_current_balance()
    total_pnl = current_balance - STARTING_BALANCE
    total_return = ((current_balance - STARTING_BALANCE) / STARTING_BALANCE) * 100

    return {
        'total_trades': total_trades,
        'wins': wins,
        'losses': losses,
        'win_rate': (wins / total_trades * 100) if total_trades > 0 else 0,
        'total_pnl': total_pnl,
        'current_balance': current_balance,
        'total_return': total_return
    }


def post_daily_performance():
    """Post daily performance summary to Telegram"""
    stats = get_performance_stats()

    # Determine overall status
    if stats['total_pnl'] > 0:
        status_emoji = "📈"
        status_text = "PROFIT"
    elif stats['total_pnl'] < 0:
        status_emoji = "📉"
        status_text = "LOSS"
    else:
        status_emoji = "➖"
        status_text = "BREAKEVEN"

    # Calculate today's trades
    df = init_trades_file()
    today = datetime.now().strftime('%Y-%m-%d')
    today_trades = df[(df['exit_date'] == today) & (df['status'] == 'CLOSED')]

    today_pnl = today_trades['pnl_dollars'].sum() if not today_trades.empty else 0
    today_wins = len(today_trades[today_trades['pnl_dollars'] > 0])
    today_losses = len(today_trades[today_trades['pnl_dollars'] <= 0])

    msg = f"""
{status_emoji}{status_emoji}{status_emoji} <b>DAILY PERFORMANCE REPORT</b> {status_emoji}{status_emoji}{status_emoji}

<b>Today's Results:</b>
   Trades: {len(today_trades)} ({today_wins}W / {today_losses}L)
   P&L: <code>${today_pnl:+,.2f}</code>

<b>Overall Performance:</b>
   Starting Balance: <code>$1,000.00</code>
   Current Balance: <code>${stats['current_balance']:,.2f}</code>

   Total P&L: <code>${stats['total_pnl']:+,.2f}</code>
   Total Return: <code>{stats['total_return']:+.2f}%</code>

<b>Statistics:</b>
   Total Trades: {stats['total_trades']}
   Wins: {stats['wins']} | Losses: {stats['losses']}
   Win Rate: {stats['win_rate']:.1f}%

<b>Status:</b> {status_text}

{datetime.now().strftime('%B %d, %Y')}
#SP500 #Performance #Trading
"""

    return send_telegram_message(msg)


def post_trade_result(trade_data):
    """Post individual trade result to Telegram"""
    result = "WIN" if trade_data['pnl_dollars'] > 0 else "LOSS"
    emoji = "✅" if result == "WIN" else "❌"

    stats = get_performance_stats()

    msg = f"""
{emoji} <b>TRADE CLOSED - {result}</b> {emoji}

<b>Signal:</b> {trade_data['signal_type']}
<b>Entry:</b> ${trade_data['entry_price']:,.2f}
<b>Exit:</b> ${trade_data['exit_price']:,.2f}

<b>Result:</b>
   P&L: <code>${trade_data['pnl_dollars']:+,.2f}</code> ({trade_data['pnl_percent']:+.2f}%)

<b>Account:</b>
   Balance: <code>${stats['current_balance']:,.2f}</code>
   Total Return: <code>{stats['total_return']:+.2f}%</code>

#SP500 #TradeResult #{result}
"""
    return send_telegram_message(msg)


def manual_close_trade(exit_price=None):
    """Manually close the most recent open trade"""
    df = init_trades_file()

    open_trades = df[df['status'] == 'OPEN']
    if open_trades.empty:
        print("No open trades to close")
        return False

    if exit_price is None:
        exit_price = get_sp500_price()
        if not exit_price:
            print("Could not get current price")
            return False

    idx = open_trades.index[-1]  # Most recent open trade
    trade = df.loc[idx]

    entry = float(trade['entry_price'])
    tp = float(trade['take_profit'])
    sl = float(trade['stop_loss'])
    signal_type = trade['signal_type']

    current_balance = get_current_balance()

    # Calculate P&L
    if signal_type == 'BUY':
        pnl_percent = ((exit_price - entry) / entry) * 100
    else:
        pnl_percent = ((entry - exit_price) / entry) * 100

    # Calculate dollar P&L
    risk_amount = current_balance * RISK_PER_TRADE
    risk_reward = abs(tp - entry) / abs(entry - sl)

    if pnl_percent > 0:
        actual_rr = abs(exit_price - entry) / abs(entry - sl)
        pnl_dollars = risk_amount * actual_rr
    else:
        actual_rr = abs(exit_price - entry) / abs(entry - sl)
        pnl_dollars = -risk_amount * actual_rr

    new_balance = current_balance + pnl_dollars

    # Update trade
    df.loc[idx, 'status'] = 'CLOSED'
    df.loc[idx, 'exit_price'] = exit_price
    df.loc[idx, 'exit_date'] = datetime.now().strftime('%Y-%m-%d')
    df.loc[idx, 'pnl_percent'] = round(pnl_percent, 2)
    df.loc[idx, 'pnl_dollars'] = round(pnl_dollars, 2)
    df.loc[idx, 'balance_after'] = round(new_balance, 2)

    df.to_csv(TRADES_FILE, index=False)

    trade_result = {
        'signal_type': signal_type,
        'entry_price': entry,
        'exit_price': exit_price,
        'pnl_percent': round(pnl_percent, 2),
        'pnl_dollars': round(pnl_dollars, 2)
    }

    post_trade_result(trade_result)
    print(f"Trade closed at ${exit_price:,.2f} | P&L: ${pnl_dollars:+,.2f}")
    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == "stats":
            stats = get_performance_stats()
            print("\n=== Performance Stats ===")
            print(f"Balance: ${stats['current_balance']:,.2f}")
            print(f"Total P&L: ${stats['total_pnl']:+,.2f}")
            print(f"Return: {stats['total_return']:+.2f}%")
            print(f"Trades: {stats['total_trades']} ({stats['wins']}W/{stats['losses']}L)")
            print(f"Win Rate: {stats['win_rate']:.1f}%")

        elif cmd == "check":
            check_open_trades()

        elif cmd == "report":
            post_daily_performance()
            print("Daily report posted!")

        elif cmd == "close":
            price = float(sys.argv[2]) if len(sys.argv) > 2 else None
            manual_close_trade(price)

        elif cmd == "balance":
            print(f"Current Balance: ${get_current_balance():,.2f}")

        else:
            print(f"Unknown command: {cmd}")
            print("Commands: stats, check, report, close [price], balance")
    else:
        print("S&P 500 Performance Tracker")
        print("Commands: stats, check, report, close [price], balance")
