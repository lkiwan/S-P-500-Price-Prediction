# -*- coding: utf-8 -*-
"""
S&P 500 Professional Trading Signals Bot
=========================================
- Posts BUY/SELL signals when confidence > 60%
- Market open/close notifications
- Professional styling
- Performance tracking with $1000 starting balance
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import warnings
warnings.filterwarnings('ignore')

# Import performance tracker
try:
    from performance_tracker import (
        record_signal, check_open_trades, get_current_balance,
        get_performance_stats, post_daily_performance
    )
    TRACKER_AVAILABLE = True
except ImportError:
    TRACKER_AVAILABLE = False

# Configuration
TELEGRAM_BOT_TOKEN = "7125291296:AAFG1rkGILb22CVnYSr3UEmUxXg_8ikcHMQ"
TELEGRAM_CHAT_ID = "@lkiwanSP500"
MIN_CONFIDENCE = 0.60  # Only post if confidence > 60%

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREDICTIONS_FILE = os.path.join(BASE_DIR, 'predictions_with_accuracy.csv')
PREDICTIONS_HISTORY = os.path.join(BASE_DIR, 'predictions_history.csv')
SIGNALS_DIR = os.path.join(BASE_DIR, 'data', 'trading_signals')


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


def send_telegram_photo_bytes(photo_bytes, caption=""):
    """Send a photo from bytes to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    try:
        files = {'photo': ('signal.png', photo_bytes, 'image/png')}
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': caption,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, files=files, data=data, timeout=60, verify=False)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def create_signal_image(direction, confidence, entry=None, tp=None, sl=None):
    """Create a professional signal image"""
    width, height = 800, 600

    is_buy = direction.upper() in ['UP', 'LONG', 'BUY']

    if is_buy:
        bg_color = (16, 185, 129)  # Green
        action = "BUY"
        emoji_text = "BULLISH"
    else:
        bg_color = (239, 68, 68)  # Red
        action = "SELL"
        emoji_text = "BEARISH"

    # Create gradient background
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Gradient effect
    for y in range(height):
        ratio = y / height
        r = int(bg_color[0] * (1 - ratio * 0.3))
        g = int(bg_color[1] * (1 - ratio * 0.3))
        b = int(bg_color[2] * (1 - ratio * 0.3))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Try fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        big_font = ImageFont.truetype("arial.ttf", 72)
        medium_font = ImageFont.truetype("arial.ttf", 32)
        small_font = ImageFont.truetype("arial.ttf", 24)
    except:
        title_font = ImageFont.load_default()
        big_font = title_font
        medium_font = title_font
        small_font = title_font

    white = (255, 255, 255)

    # Header
    draw.text((width//2, 30), "S&P 500 TRADING SIGNAL", font=title_font, fill=white, anchor="mt")

    # Main action
    draw.text((width//2, 120), action, font=big_font, fill=white, anchor="mt")
    draw.text((width//2, 200), emoji_text, font=medium_font, fill=white, anchor="mt")

    # Confidence
    conf_percent = int(confidence * 100)
    draw.text((width//2, 270), f"Confidence: {conf_percent}%", font=medium_font, fill=white, anchor="mt")

    # Confidence bar
    bar_width = 500
    bar_height = 25
    bar_x = (width - bar_width) // 2
    bar_y = 320

    # Background bar
    draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
                   fill=(255, 255, 255, 80), outline=white, width=2)
    # Filled bar
    filled_width = int(bar_width * confidence)
    draw.rectangle([bar_x + 2, bar_y + 2, bar_x + filled_width - 2, bar_y + bar_height - 2],
                   fill=white)

    # Trading levels
    y_pos = 380
    if entry:
        draw.text((width//2, y_pos), f"Entry Price: ${entry:,.2f}", font=medium_font, fill=white, anchor="mt")
        y_pos += 45
    if tp:
        draw.text((width//2, y_pos), f"Take Profit: ${tp:,.2f}", font=medium_font, fill=white, anchor="mt")
        y_pos += 45
    if sl:
        draw.text((width//2, y_pos), f"Stop Loss: ${sl:,.2f}", font=medium_font, fill=white, anchor="mt")

    # Footer
    now = datetime.now().strftime("%B %d, %Y - %H:%M UTC")
    draw.text((width//2, height - 40), now, font=small_font, fill=white, anchor="mt")

    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.read()


def get_latest_prediction():
    """Get the latest prediction from CSV"""
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
        'direction': latest.get('direction', 'N/A'),
        'confidence': float(latest.get('confidence', 0.5)),
        'prob_up': float(latest.get('prob_up', 0.5)),
        'prob_down': float(latest.get('prob_down', 0.5))
    }


def get_trading_signal():
    """Get the latest trading signal with TP/SL levels"""
    signals_file = os.path.join(SIGNALS_DIR, 'signals_history.csv')

    if os.path.exists(signals_file):
        df = pd.read_csv(signals_file)
        if not df.empty:
            latest = df.iloc[-1]
            return {
                'direction': latest.get('direction', 'N/A'),
                'entry_price': float(latest.get('entry_price', 0)),
                'take_profit': float(latest.get('take_profit', 0)),
                'stop_loss': float(latest.get('stop_loss', 0)),
                'confidence': float(latest.get('confidence', 0.5)),
                'risk_reward': float(latest.get('risk_reward', 0)),
            }
    return None


def format_signal_message(prediction, signal=None):
    """Format a professional trading signal message"""
    direction = prediction['direction']
    confidence = prediction['confidence']

    is_buy = direction.upper() in ['UP', 'LONG', 'BUY']

    if is_buy:
        action_emoji = "🟢"
        action = "BUY"
        trend = "BULLISH"
        arrow = "📈"
    else:
        action_emoji = "🔴"
        action = "SELL"
        trend = "BEARISH"
        arrow = "📉"

    # Confidence description
    if confidence >= 0.80:
        strength = "🔥 STRONG SIGNAL"
    elif confidence >= 0.70:
        strength = "✅ HIGH CONFIDENCE"
    elif confidence >= 0.60:
        strength = "📊 MODERATE"
    else:
        strength = "⚠️ WEAK"

    # Build message
    msg = f"""
{action_emoji}{action_emoji}{action_emoji} <b>S&P 500 SIGNAL</b> {action_emoji}{action_emoji}{action_emoji}

{arrow} <b>Action:</b> {action}
📊 <b>Trend:</b> {trend}
💪 <b>Strength:</b> {strength}
🎯 <b>Confidence:</b> {confidence*100:.1f}%

<b>Probabilities:</b>
   📈 UP: {prediction['prob_up']*100:.1f}%
   📉 DOWN: {prediction['prob_down']*100:.1f}%
"""

    if signal and signal.get('entry_price', 0) > 0:
        msg += f"""
<b>💰 Trading Levels:</b>
   ▫️ Entry: <code>${signal['entry_price']:,.2f}</code>
   ▫️ Take Profit: <code>${signal['take_profit']:,.2f}</code>
   ▫️ Stop Loss: <code>${signal['stop_loss']:,.2f}</code>
   ▫️ Risk/Reward: <code>{signal['risk_reward']:.2f}</code>
"""

    # Add account balance if tracker available
    if TRACKER_AVAILABLE:
        try:
            stats = get_performance_stats()
            balance = stats['current_balance']
            total_return = stats['total_return']
            win_rate = stats['win_rate']
            msg += f"""
<b>💼 Account Status:</b>
   Balance: <code>${balance:,.2f}</code>
   Return: <code>{total_return:+.2f}%</code>
   Win Rate: <code>{win_rate:.1f}%</code>
"""
        except:
            pass

    msg += f"""
📅 <b>Date:</b> {datetime.now().strftime("%B %d, %Y")}

#SP500 #Trading #Stocks #{action}
"""
    return msg


def post_market_open():
    """Post market open notification"""
    msg = """
🔔🔔🔔 <b>MARKET OPEN</b> 🔔🔔🔔

🇺🇸 <b>US Stock Market is NOW OPEN!</b>

⏰ Trading Hours: 9:30 AM - 4:00 PM ET
📊 Index: S&P 500

Good luck traders! 💪

#MarketOpen #SP500 #Trading
"""
    return send_telegram_message(msg)


def post_market_close():
    """Post market close notification with performance summary"""
    # Check and close any open trades first
    if TRACKER_AVAILABLE:
        try:
            check_open_trades()
        except:
            pass

    # Get performance stats
    performance_text = ""
    if TRACKER_AVAILABLE:
        try:
            stats = get_performance_stats()
            if stats['total_trades'] > 0:
                status = "PROFIT" if stats['total_pnl'] > 0 else "LOSS" if stats['total_pnl'] < 0 else "BREAKEVEN"
                performance_text = f"""
<b>📊 Account Performance:</b>
   Balance: <code>${stats['current_balance']:,.2f}</code>
   Total P&L: <code>${stats['total_pnl']:+,.2f}</code>
   Return: <code>{stats['total_return']:+.2f}%</code>
   Win Rate: <code>{stats['win_rate']:.1f}%</code>
   Status: {status}
"""
        except:
            pass

    msg = f"""
🔔🔔🔔 <b>MARKET CLOSED</b> 🔔🔔🔔

🇺🇸 <b>US Stock Market is NOW CLOSED!</b>

📊 Today's session has ended.
⏰ Next open: Tomorrow 9:30 AM ET
{performance_text}
See you tomorrow! 👋

#MarketClose #SP500 #Trading
"""
    return send_telegram_message(msg)


def post_daily_signal():
    """Post the daily trading signal to Telegram"""
    print("=" * 50)
    print("S&P 500 Telegram Signal Bot")
    print("=" * 50)

    prediction = get_latest_prediction()
    if not prediction:
        print("No prediction data found")
        return False

    confidence = prediction['confidence']
    print(f"Prediction: {prediction['direction']} ({confidence*100:.1f}%)")

    # Check minimum confidence
    if confidence < MIN_CONFIDENCE:
        print(f"Confidence {confidence*100:.1f}% < {MIN_CONFIDENCE*100:.0f}% minimum. Not posting.")
        return False

    signal = get_trading_signal()

    print("Creating signal image...")
    img_bytes = create_signal_image(
        direction=prediction['direction'],
        confidence=confidence,
        entry=signal['entry_price'] if signal else None,
        tp=signal['take_profit'] if signal else None,
        sl=signal['stop_loss'] if signal else None
    )

    message = format_signal_message(prediction, signal)

    print("Sending to Telegram...")
    success = send_telegram_photo_bytes(img_bytes, message)

    if success:
        print("Signal posted successfully!")
        # Record signal for performance tracking
        if TRACKER_AVAILABLE and signal:
            try:
                signal_type = 'BUY' if prediction['direction'].upper() in ['UP', 'LONG', 'BUY'] else 'SELL'
                record_signal(
                    signal_type=signal_type,
                    entry_price=signal['entry_price'],
                    take_profit=signal['take_profit'],
                    stop_loss=signal['stop_loss'],
                    confidence=confidence
                )
                print("Signal recorded for tracking!")
            except Exception as e:
                print(f"Could not record signal: {e}")
    else:
        print("Image failed, sending text only...")
        success = send_telegram_message(message)
        print("Text sent!" if success else "Failed!")

    return success


def check_and_post():
    """Check market status and post accordingly"""
    from datetime import datetime
    import pytz

    try:
        et = pytz.timezone('US/Eastern')
        now_et = datetime.now(et)
    except:
        # Fallback if pytz not available
        now_et = datetime.now()

    hour = now_et.hour
    minute = now_et.minute
    weekday = now_et.weekday()

    # Skip weekends
    if weekday >= 5:
        print("Weekend - market closed")
        return

    # Market open at 9:30 AM ET
    if hour == 9 and 25 <= minute <= 35:
        print("Posting market open notification...")
        post_market_open()
        return

    # Market close at 4:00 PM ET
    if hour == 16 and 0 <= minute <= 10:
        print("Posting market close notification...")
        post_market_close()
        return

    # Post signal before market open (9:00 AM)
    if hour == 9 and 0 <= minute <= 10:
        print("Posting daily signal...")
        post_daily_signal()
        return

    print(f"Current time: {now_et.strftime('%H:%M')} ET - No action needed")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == "signal":
            post_daily_signal()
        elif cmd == "open":
            post_market_open()
        elif cmd == "close":
            post_market_close()
        elif cmd == "check":
            check_and_post()
        elif cmd == "test":
            send_telegram_message("Test message - Bot is working!")
        else:
            print(f"Unknown command: {cmd}")
            print("Commands: signal, open, close, check, test")
    else:
        # Default: check and post based on time
        check_and_post()
