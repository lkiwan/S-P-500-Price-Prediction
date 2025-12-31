# -*- coding: utf-8 -*-
"""
S&P 500 AI-Powered Telegram Bot
================================
Uses Groq AI (Llama 3) for intelligent message generation.
Posts every 15 minutes with AI-generated educational content.

Get FREE Groq API key: https://console.groq.com/keys
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import warnings
import random
import pytz
warnings.filterwarnings('ignore')

# Import Groq AI module
try:
    from groq_ai import (
        call_groq_api,
        generate_technical_analysis,
        generate_market_insight,
        generate_quote_analysis,
        generate_market_history_insight,
        generate_trading_tip,
        generate_did_you_know,
        generate_fundamental_insight,
        generate_signal_analysis,
        GROQ_API_KEY
    )
    GROQ_AVAILABLE = GROQ_API_KEY != "YOUR_GROQ_API_KEY_HERE" and GROQ_API_KEY != ""
except ImportError:
    GROQ_AVAILABLE = False
    print("[WARNING] groq_ai.py not found. AI features disabled.")

# Import News Fetcher module
try:
    from news_fetcher import get_news_for_telegram, fetch_market_news
    NEWS_AVAILABLE = True
except ImportError:
    NEWS_AVAILABLE = False
    print("[WARNING] news_fetcher.py not found. News features disabled.")

# Import Image Generator module
try:
    from image_generator import (
        create_technical_chart,
        create_quote_card,
        create_news_banner,
        create_stats_graphic,
        create_tip_card,
        UNSPLASH_AVAILABLE
    )
    IMAGES_AVAILABLE = True
except ImportError:
    IMAGES_AVAILABLE = False
    UNSPLASH_AVAILABLE = False
    print("[WARNING] image_generator.py not found. Image features disabled.")

# Configuration
TELEGRAM_BOT_TOKEN = "7125291296:AAFG1rkGILb22CVnYSr3UEmUxXg_8ikcHMQ"
TELEGRAM_CHAT_ID = "@lkiwanSP500"

# Time zones
ET_TIMEZONE = pytz.timezone('US/Eastern')
MOROCCO_TIMEZONE = pytz.timezone('Africa/Casablanca')

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRICE_DATA_FILE = os.path.join(BASE_DIR, 'data', 'raw', 'price_data.csv')
FEATURES_FILE = os.path.join(BASE_DIR, 'data', 'features', 'features_complete.csv')
PREDICTIONS_FILE = os.path.join(BASE_DIR, 'predictions_with_accuracy.csv')
SIGNALS_FILE = os.path.join(BASE_DIR, 'data', 'trading_signals', 'signals_history.csv')


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
            print(f"[ERROR] Failed: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def send_telegram_photo(photo_bytes, caption=None, parse_mode="HTML"):
    """Send a photo to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

    try:
        # Prepare the photo
        if hasattr(photo_bytes, 'read'):
            photo_bytes.seek(0)
            photo_data = photo_bytes.read()
            photo_bytes.seek(0)
        else:
            photo_data = photo_bytes

        files = {
            'photo': ('image.png', photo_data, 'image/png')
        }

        data = {
            'chat_id': TELEGRAM_CHAT_ID,
        }

        if caption:
            data['caption'] = caption
            data['parse_mode'] = parse_mode

        response = requests.post(url, data=data, files=files, timeout=60, verify=False)

        if response.status_code == 200:
            print(f"[OK] Photo sent successfully")
            return True
        else:
            print(f"[ERROR] Photo failed: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Photo error: {e}")
        return False


def get_price_data(days=60):
    """Load price data"""
    try:
        df = pd.read_csv(PRICE_DATA_FILE)
        df.columns = [c.capitalize() if c.lower() in ['open', 'high', 'low', 'close', 'volume', 'date'] else c for c in df.columns]
        if 'Date' not in df.columns and 'date' in df.columns:
            df.rename(columns={'date': 'Date'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date'], format='mixed')
        df = df.sort_values('Date').tail(days)
        return df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()


def get_features_data():
    """Load features data"""
    try:
        df = pd.read_csv(FEATURES_FILE)
        df['date'] = pd.to_datetime(df['date'], format='mixed')
        return df.sort_values('date')
    except:
        return pd.DataFrame()


def get_current_time_et():
    return datetime.now(ET_TIMEZONE)


def get_current_time_morocco():
    return datetime.now(MOROCCO_TIMEZONE)


def clean_ai_content(text, max_length=400):
    """Clean AI-generated content for Telegram captions"""
    if not text:
        return ""
    # Remove HTML tags that might be unclosed
    clean = text.replace('<b>', '').replace('</b>', '')
    clean = clean.replace('<i>', '').replace('</i>', '')
    clean = clean.replace('<code>', '').replace('</code>', '')
    clean = clean.replace('<pre>', '').replace('</pre>', '')
    clean = clean.replace('<a>', '').replace('</a>', '')
    # Limit length
    if len(clean) > max_length:
        clean = clean[:max_length] + "..."
    return clean


# ============================================================================
# FAMOUS QUOTES DATABASE (for fallback and AI analysis)
# ============================================================================

FAMOUS_QUOTES = [
    ("Be fearful when others are greedy and greedy when others are fearful.", "Warren Buffett"),
    ("The stock market is a device for transferring money from the impatient to the patient.", "Warren Buffett"),
    ("In the short run, the market is a voting machine but in the long run, it is a weighing machine.", "Benjamin Graham"),
    ("The four most dangerous words in investing are: 'This time it's different.'", "John Templeton"),
    ("Know what you own, and know why you own it.", "Peter Lynch"),
    ("Risk comes from not knowing what you're doing.", "Warren Buffett"),
    ("The trend is your friend until it ends.", "Ed Seykota"),
    ("It's not whether you're right or wrong that's important, but how much money you make when you're right.", "George Soros"),
    ("The key to making money in stocks is not to get scared out of them.", "Peter Lynch"),
    ("Bull markets are born on pessimism, grow on skepticism, mature on optimism, and die on euphoria.", "John Templeton"),
]

MARKET_EVENTS = [
    ("Black Monday 1987", "October 19, 1987 - S&P 500 dropped 22.6% in a single day, the largest one-day percentage decline in history."),
    ("2008 Financial Crisis", "The subprime mortgage crisis led to a 57% drop in the S&P 500 from peak to trough."),
    ("COVID-19 Crash 2020", "The fastest bear market in history - S&P 500 fell 34% in just 33 days, then recovered in 5 months."),
    ("Dot-Com Bubble 2000", "Tech speculation led to a 49% S&P 500 decline over 2.5 years."),
    ("1990s Bull Market", "One of the longest bull runs in history, with the S&P 500 gaining over 400%."),
]


# ============================================================================
# AI-POWERED MESSAGE FUNCTIONS
# ============================================================================

def post_ai_technical_analysis():
    """Post AI-generated technical analysis with chart image"""
    print("Generating AI Technical Analysis...")

    df = get_features_data()
    price_df = get_price_data(60)

    if df.empty or price_df.empty:
        return post_ai_market_insight()

    latest = df.iloc[-1]
    current_price = float(price_df['Close'].iloc[-1])

    # Get indicators
    rsi = float(latest.get('rsi_14', 50))
    macd = float(latest.get('macd', 0))
    sma_20 = float(latest.get('sma_20', current_price))
    sma_50 = float(latest.get('sma_50', current_price))

    # Determine trend
    if current_price > sma_20 > sma_50:
        trend = "UPTREND"
        trend_emoji = "🚀"
    elif current_price < sma_20 < sma_50:
        trend = "DOWNTREND"
        trend_emoji = "📉"
    else:
        trend = "SIDEWAYS"
        trend_emoji = "↔️"

    # Calculate ATR
    if len(price_df) >= 14:
        high = price_df['High']
        low = price_df['Low']
        close = price_df['Close']
        tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])
    else:
        atr = current_price * 0.01

    # Generate chart image
    chart_image = None
    if IMAGES_AVAILABLE:
        try:
            print("Creating technical chart...")
            chart_image = create_technical_chart(price_df)
        except Exception as e:
            print(f"Chart error: {e}")

    # Generate caption
    rsi_signal = "🔴 Overbought" if rsi > 70 else "🟢 Oversold" if rsi < 30 else "⚪ Neutral"
    macd_signal = "🟢 Bullish" if macd > 0 else "🔴 Bearish"

    caption = f"""📊📊📊 <b>TECHNICAL ANALYSIS</b> 📊📊📊

━━━━━━━━━━━━━━━━━━━━━━

💰 <b>S&P 500:</b> <code>${current_price:,.2f}</code>

━━━━━━━━━━━━━━━━━━━━━━

{trend_emoji} <b>Trend:</b> {trend}
📊 <b>RSI (14):</b> {rsi:.1f} {rsi_signal}
📈 <b>MACD:</b> {macd:.2f} {macd_signal}
💨 <b>ATR:</b> {atr:.2f}

━━━━━━━━━━━━━━━━━━━━━━"""

    # Add AI insight if available
    if GROQ_AVAILABLE:
        ai_content = generate_technical_analysis(current_price, rsi, macd, trend, atr)
        if ai_content:
            clean_content = clean_ai_content(ai_content, 350)
            caption += f"\n\n🤖 <b>AI Insight:</b>\n{clean_content}"

    caption += "\n\n#TechnicalAnalysis #SP500 #Trading"

    # Send with or without image
    if chart_image:
        return send_telegram_photo(chart_image, caption)
    else:
        return send_telegram_message(caption)


def post_fallback_technical(price, rsi, macd, trend, atr):
    """Fallback technical analysis without AI"""
    rsi_signal = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
    macd_signal = "Bullish" if macd > 0 else "Bearish"

    msg = f"""
📊 <b>TECHNICAL ANALYSIS</b>
<i>{datetime.now().strftime('%H:%M')} ET</i>

<b>S&P 500: ${price:,.2f}</b>

📈 <b>Trend:</b> {trend}
📊 <b>RSI (14):</b> {rsi:.1f} - {rsi_signal}
📉 <b>MACD:</b> {macd:.2f} - {macd_signal}
💨 <b>ATR:</b> {atr:.2f}

#TechnicalAnalysis #SP500 #Trading
"""
    return send_telegram_message(msg)


def post_ai_market_insight():
    """Post AI-generated market insight"""
    print("Generating AI Market Insight...")

    if GROQ_AVAILABLE:
        ai_content = generate_market_insight()
        if ai_content:
            return send_telegram_message(ai_content)

    # Fallback
    msg = """
💡 <b>MARKET INSIGHT</b>

The best traders focus on process, not outcomes. A good trade can lose money, and a bad trade can make money.

What matters is:
• Did you follow your plan?
• Did you manage risk properly?
• Did you stay disciplined?

Focus on making good decisions consistently, and the profits will follow.

#TradingWisdom #Process #Discipline
"""
    return send_telegram_message(msg)


def post_ai_quote_analysis():
    """Post AI analysis of a famous quote with quote card image"""
    print("Generating AI Quote Analysis...")

    quote, author = random.choice(FAMOUS_QUOTES)

    # Generate quote card image
    quote_image = None
    if IMAGES_AVAILABLE:
        try:
            print("Creating quote card...")
            quote_image = create_quote_card(quote, author)
        except Exception as e:
            print(f"Quote card error: {e}")

    # Generate caption
    caption = f"""💬💬💬 <b>WISDOM FROM THE MASTERS</b> 💬💬💬

━━━━━━━━━━━━━━━━━━━━━━

<i>"{quote}"</i>

— <b>{author}</b>

━━━━━━━━━━━━━━━━━━━━━━"""

    # Add AI analysis if available
    if GROQ_AVAILABLE:
        ai_content = generate_quote_analysis(quote, author)
        if ai_content:
            clean_content = clean_ai_content(ai_content, 350)
            caption += f"\n\n🤖 <b>AI Analysis:</b>\n{clean_content}"

    caption += f"\n\n#TradingWisdom #Quotes #{author.replace(' ', '')}"

    # Send with or without image
    if quote_image:
        return send_telegram_photo(quote_image, caption)
    else:
        return send_telegram_message(caption)


def post_ai_market_history():
    """Post AI insight about market history"""
    print("Generating AI Market History...")

    event_name, event_details = random.choice(MARKET_EVENTS)

    if GROQ_AVAILABLE:
        ai_content = generate_market_history_insight(event_name, event_details)
        if ai_content:
            return send_telegram_message(ai_content)

    # Fallback
    msg = f"""
📚 <b>MARKET HISTORY</b>

<b>{event_name}</b>

{event_details}

<b>Key Lesson:</b> Markets are cyclical. Crashes happen, but recoveries follow. Stay prepared, stay diversified.

#MarketHistory #Investing #Education
"""
    return send_telegram_message(msg)


def post_ai_trading_tip():
    """Post AI-generated trading tip with tip card image"""
    print("Generating AI Trading Tip...")

    # Fallback tips
    tips = [
        "Never risk more than 2% of your portfolio on a single trade.",
        "The best trade is often no trade at all.",
        "Cut your losses short and let your winners run.",
        "Trade the plan, not your emotions.",
        "The trend is your friend - don't fight it.",
        "Position sizing is more important than entry timing.",
        "Always know your exit before you enter.",
        "The market can stay irrational longer than you can stay solvent.",
    ]

    tip_number = random.randint(1, 100)

    # Get AI tip or use fallback
    if GROQ_AVAILABLE:
        ai_tip = generate_trading_tip()
        if ai_tip:
            # Clean the tip text for the image
            tip_text = ai_tip.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '')
            tip_text = tip_text.split('\n')[0][:200]  # First line, max 200 chars
        else:
            tip_text = random.choice(tips)
    else:
        tip_text = random.choice(tips)

    # Generate tip card image
    tip_image = None
    if IMAGES_AVAILABLE:
        try:
            print("Creating tip card...")
            tip_image = create_tip_card(tip_text, tip_number)
        except Exception as e:
            print(f"Tip card error: {e}")

    # Generate caption
    caption = f"""💡💡💡 <b>TRADING TIP #{tip_number}</b> 💡💡💡

━━━━━━━━━━━━━━━━━━━━━━

{tip_text}

━━━━━━━━━━━━━━━━━━━━━━

📌 <i>Consistent small gains beat occasional big wins. Focus on risk management first!</i>

#TradingTips #RiskManagement #Education"""

    # Send with or without image
    if tip_image:
        return send_telegram_photo(tip_image, caption)
    else:
        return send_telegram_message(caption)


def post_ai_did_you_know():
    """Post AI-generated market fact"""
    print("Generating AI Did You Know...")

    if GROQ_AVAILABLE:
        ai_content = generate_did_you_know()
        if ai_content:
            return send_telegram_message(ai_content)

    # Fallback
    facts = [
        "The S&P 500 has been positive in about 70% of all years since 1928.",
        "Missing the 10 best days in the market over 20 years can cut your returns in half.",
        "The average bull market lasts 5.5 years; the average bear market lasts 1.3 years.",
        "Only 4% of stocks account for all net gains in the market since 1926."
    ]
    fact = random.choice(facts)

    msg = f"""
🤔 <b>DID YOU KNOW?</b>

{fact}

The more you know about market history, the better prepared you'll be for the future.

#DidYouKnow #MarketFacts #Education
"""
    return send_telegram_message(msg)


def post_ai_fundamental():
    """Post AI fundamental analysis education"""
    print("Generating AI Fundamental Analysis...")

    if GROQ_AVAILABLE:
        ai_content = generate_fundamental_insight()
        if ai_content:
            return send_telegram_message(ai_content)

    # Fallback
    msg = """
📚 <b>FUNDAMENTAL ANALYSIS</b>

<b>P/E Ratio (Price-to-Earnings)</b>

Formula: Stock Price / Earnings Per Share

<b>What it tells you:</b>
• Low P/E: Stock may be undervalued
• High P/E: Stock may be overvalued or high growth expected

<b>S&P 500 Average:</b> 15-17x historically

Always compare P/E within the same industry!

#FundamentalAnalysis #PE #Education
"""
    return send_telegram_message(msg)


def post_ai_market_stats():
    """Post market statistics with AI commentary and stats graphic"""
    print("Generating Market Stats...")

    df = get_price_data(252)
    if df.empty:
        return post_ai_trading_tip()

    current_price = float(df['Close'].iloc[-1])
    day_change = ((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100
    week_change = ((df['Close'].iloc[-1] / df['Close'].iloc[-5]) - 1) * 100 if len(df) > 5 else 0
    month_change = ((df['Close'].iloc[-1] / df['Close'].iloc[-22]) - 1) * 100 if len(df) > 22 else 0
    ytd_change = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100 if len(df) > 22 else 0

    high_52w = float(df['High'].max())
    low_52w = float(df['Low'].min())
    from_high = ((current_price - high_52w) / high_52w) * 100

    day_emoji = "🟢" if day_change > 0 else "🔴" if day_change < 0 else "⚪"
    week_emoji = "🟢" if week_change > 0 else "🔴" if week_change < 0 else "⚪"
    month_emoji = "🟢" if month_change > 0 else "🔴" if month_change < 0 else "⚪"

    # Generate stats graphic
    stats_image = None
    if IMAGES_AVAILABLE:
        try:
            print("Creating stats graphic...")
            stats_data = {
                'price': current_price,
                'day_change': day_change,
                'week_change': week_change,
                'month_change': month_change,
                'ytd_change': ytd_change
            }
            stats_image = create_stats_graphic(stats_data)
        except Exception as e:
            print(f"Stats graphic error: {e}")

    # AI commentary
    ai_comment = ""
    if GROQ_AVAILABLE:
        prompt = f"In one sentence, comment on S&P 500 at ${current_price:,.0f}, {day_change:+.2f}% today, {from_high:.1f}% from 52-week high. Be insightful."
        ai_response = call_groq_api(prompt, max_tokens=60, temperature=0.7)
        if ai_response:
            clean_response = clean_ai_content(ai_response, 150)
            ai_comment = f"\n\n🤖 {clean_response}"

    caption = f"""📊📊📊 <b>MARKET STATISTICS</b> 📊📊📊

━━━━━━━━━━━━━━━━━━━━━━

💰 <b>S&P 500:</b> <code>${current_price:,.2f}</code>

━━━━━━━━━━━━━━━━━━━━━━

<b>Performance:</b>
{day_emoji} Today: <code>{day_change:+.2f}%</code>
{week_emoji} Week: <code>{week_change:+.2f}%</code>
{month_emoji} Month: <code>{month_change:+.2f}%</code>

━━━━━━━━━━━━━━━━━━━━━━

<b>52-Week Range:</b>
🔺 High: ${high_52w:,.2f} ({from_high:.1f}%)
🔻 Low: ${low_52w:,.2f}
{ai_comment}

#MarketStats #SP500 #StockMarket"""

    # Send with or without image
    if stats_image:
        return send_telegram_photo(stats_image, caption)
    else:
        return send_telegram_message(caption)


def post_market_news():
    """Post market news update with news banner image"""
    print("Fetching Market News...")

    # Fetch news
    news_items = []
    if NEWS_AVAILABLE:
        news_items = fetch_market_news(5)

    # Generate news banner
    news_image = None
    headline = None
    if news_items:
        headline = news_items[0].get('title', '')

    if IMAGES_AVAILABLE:
        try:
            print("Creating news banner...")
            news_image = create_news_banner(headline)
        except Exception as e:
            print(f"News banner error: {e}")

    # Build caption
    date_str = datetime.now().strftime("%B %d, %Y • %H:%M")

    if news_items:
        caption = f"""📰📰📰 <b>MARKET NEWS UPDATE</b> 📰📰📰

📅 {date_str}

━━━━━━━━━━━━━━━━━━━━━━

📢 <b>Latest Headlines:</b>

"""
        for i, item in enumerate(news_items[:5], 1):
            title = item.get('title', '')
            source = item.get('source', 'News')

            if any(word in title.lower() for word in ['surge', 'jump', 'rally', 'gain', 'rise', 'up', 'bull']):
                emoji = "📈"
            elif any(word in title.lower() for word in ['drop', 'fall', 'crash', 'down', 'bear', 'loss']):
                emoji = "📉"
            elif any(word in title.lower() for word in ['fed', 'rate', 'inflation', 'economy']):
                emoji = "🏛️"
            else:
                emoji = "📌"

            caption += f"{emoji} <b>{i}.</b> {title}\n<i>— {source}</i>\n\n"

        caption += "━━━━━━━━━━━━━━━━━━━━━━\n"
        caption += "\n#MarketNews #SP500 #StockMarket"

    elif GROQ_AVAILABLE:
        print("No news available, generating AI commentary...")
        prompt = """Generate a brief market news update for S&P 500.
Include: market sentiment, key factors, brief outlook.
Use ONLY plain text with emojis. NO HTML tags. Keep under 150 words."""

        ai_news = call_groq_api(prompt, max_tokens=300, temperature=0.7)
        if ai_news:
            clean_news = clean_ai_content(ai_news, 500)
            caption = f"""📰📰📰 <b>MARKET UPDATE</b> 📰📰📰

📅 {date_str}

━━━━━━━━━━━━━━━━━━━━━━

{clean_news}

━━━━━━━━━━━━━━━━━━━━━━

🤖 AI-Generated Commentary

#MarketNews #SP500 #Trading"""
        else:
            caption = f"""📰 <b>MARKET UPDATE</b>

📅 {date_str}

Stay tuned for the latest market developments.

#MarketNews #SP500"""
    else:
        caption = f"""📰 <b>MARKET UPDATE</b>

📅 {date_str}

Stay tuned for the latest market developments.

#MarketNews #SP500"""

    # Send with or without image
    if news_image:
        return send_telegram_photo(news_image, caption)
    else:
        return send_telegram_message(caption)


# ============================================================================
# CONTENT ROTATION
# ============================================================================

CONTENT_TYPES = [
    (post_ai_technical_analysis, 20),
    (post_ai_fundamental, 15),
    (post_ai_quote_analysis, 15),
    (post_ai_market_history, 15),
    (post_ai_trading_tip, 15),
    (post_ai_market_stats, 10),
    (post_ai_did_you_know, 10),
]


def get_weighted_random_content():
    """Select content type based on weights"""
    total_weight = sum(weight for _, weight in CONTENT_TYPES)
    random_num = random.randint(1, total_weight)

    cumulative = 0
    for func, weight in CONTENT_TYPES:
        cumulative += weight
        if random_num <= cumulative:
            return func

    return CONTENT_TYPES[0][0]


def post_ai_content():
    """Post AI-generated content"""
    print(f"\n{'='*60}")
    print(f"AI-Powered Content Bot")
    print(f"Time (ET): {get_current_time_et().strftime('%H:%M:%S')}")
    print(f"Time (Morocco): {get_current_time_morocco().strftime('%H:%M:%S')}")
    print(f"Groq AI: {'ENABLED' if GROQ_AVAILABLE else 'DISABLED (using fallback)'}")
    print(f"{'='*60}")

    content_func = get_weighted_random_content()
    print(f"Selected: {content_func.__name__}")

    return content_func()


def post_specific_content(content_type):
    """Post specific content type"""
    content_map = {
        "technical": post_ai_technical_analysis,
        "fundamental": post_ai_fundamental,
        "quote": post_ai_quote_analysis,
        "history": post_ai_market_history,
        "tip": post_ai_trading_tip,
        "stats": post_ai_market_stats,
        "fact": post_ai_did_you_know,
        "insight": post_ai_market_insight,
        "news": post_market_news,
    }

    if content_type in content_map:
        return content_map[content_type]()
    else:
        print(f"Unknown: {content_type}")
        print(f"Available: {', '.join(content_map.keys())}")
        return False


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("S&P 500 AI-POWERED TELEGRAM BOT")
    print("="*60)
    print(f"Groq AI Status: {'ENABLED' if GROQ_AVAILABLE else 'DISABLED'}")

    if not GROQ_AVAILABLE:
        print("\n[!] To enable AI features:")
        print("1. Get free API key at: https://console.groq.com/keys")
        print("2. Edit groq_ai.py and replace YOUR_GROQ_API_KEY_HERE")

    print("="*60)

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == "auto":
            post_ai_content()
        elif cmd in ["technical", "fundamental", "quote", "history", "tip", "stats", "fact", "insight", "news"]:
            post_specific_content(cmd)
        elif cmd == "test":
            print("\nTesting all AI content types...")
            for func, _ in CONTENT_TYPES:
                print(f"\n>>> {func.__name__}")
                input("Press Enter...")
                func()
        elif cmd == "help":
            print("""
Usage: python telegram_ai_bot.py [command]

Commands:
  auto        - Post random AI content
  technical   - AI technical analysis
  fundamental - AI fundamental education
  quote       - AI quote analysis
  history     - AI market history
  tip         - AI trading tip
  stats       - Market statistics + AI comment
  fact        - AI "Did you know"
  insight     - AI market insight
  news        - Market news (Yahoo Finance + AI summary)
  test        - Test all types
  help        - Show this help
            """)
        else:
            print(f"Unknown: {cmd}. Use 'help'")
    else:
        post_ai_content()
