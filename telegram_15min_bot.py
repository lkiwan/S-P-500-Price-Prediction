# -*- coding: utf-8 -*-
"""
S&P 500 Telegram Bot - 15-Minute Educational & Analysis Posts
==============================================================
Posts rotating content every 15 minutes during market hours:
- Technical Analysis
- Fundamental Analysis
- Historical Quotes
- Market History (Best/Worst Periods)
- News & Sentiment
- Trading Tips
- Market Statistics
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import warnings
import json
import random
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
    """Load features data with technical indicators"""
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


# ============================================================================
# HISTORICAL QUOTES DATABASE
# ============================================================================

FAMOUS_QUOTES = [
    # Warren Buffett
    ("Be fearful when others are greedy and greedy when others are fearful.", "Warren Buffett", "Value Investing"),
    ("The stock market is a device for transferring money from the impatient to the patient.", "Warren Buffett", "Patience"),
    ("Price is what you pay. Value is what you get.", "Warren Buffett", "Value Investing"),
    ("Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1.", "Warren Buffett", "Risk Management"),
    ("It's far better to buy a wonderful company at a fair price than a fair company at a wonderful price.", "Warren Buffett", "Quality"),
    ("Our favorite holding period is forever.", "Warren Buffett", "Long-term"),
    ("Risk comes from not knowing what you're doing.", "Warren Buffett", "Education"),

    # Peter Lynch
    ("Know what you own, and know why you own it.", "Peter Lynch", "Research"),
    ("The key to making money in stocks is not to get scared out of them.", "Peter Lynch", "Psychology"),
    ("Go for a business that any idiot can run – because sooner or later, any idiot is probably going to run it.", "Peter Lynch", "Simplicity"),
    ("In this business, if you're good, you're right six times out of ten.", "Peter Lynch", "Expectations"),

    # Benjamin Graham
    ("In the short run, the market is a voting machine but in the long run, it is a weighing machine.", "Benjamin Graham", "Value Investing"),
    ("The intelligent investor is a realist who sells to optimists and buys from pessimists.", "Benjamin Graham", "Contrarian"),
    ("The investor's chief problem – and even his worst enemy – is likely to be himself.", "Benjamin Graham", "Psychology"),

    # Jesse Livermore
    ("There is nothing new in Wall Street. There can't be because speculation is as old as the hills.", "Jesse Livermore", "History"),
    ("The market does not beat them. They beat themselves.", "Jesse Livermore", "Psychology"),
    ("It never was my thinking that made the big money for me. It always was my sitting.", "Jesse Livermore", "Patience"),

    # George Soros
    ("It's not whether you're right or wrong that's important, but how much money you make when you're right.", "George Soros", "Risk/Reward"),
    ("Markets are constantly in a state of uncertainty and flux.", "George Soros", "Volatility"),

    # John Templeton
    ("The four most dangerous words in investing are: 'This time it's different.'", "John Templeton", "Cycles"),
    ("Bull markets are born on pessimism, grow on skepticism, mature on optimism, and die on euphoria.", "John Templeton", "Market Cycles"),

    # Ray Dalio
    ("He who lives by the crystal ball will eat shattered glass.", "Ray Dalio", "Predictions"),
    ("Pain + Reflection = Progress", "Ray Dalio", "Learning"),

    # Charlie Munger
    ("The big money is not in the buying and selling, but in the waiting.", "Charlie Munger", "Patience"),
    ("Invert, always invert.", "Charlie Munger", "Thinking"),

    # Paul Tudor Jones
    ("The secret to being successful from a trading perspective is to have an indefatigable thirst for knowledge.", "Paul Tudor Jones", "Education"),
    ("Losers average losers.", "Paul Tudor Jones", "Risk Management"),

    # Mark Douglas
    ("Trading is a psychological game. Most people think they are playing the market, but the market is playing them.", "Mark Douglas", "Psychology"),
]

# ============================================================================
# MARKET HISTORY DATABASE
# ============================================================================

MARKET_HISTORY = {
    "crashes": [
        {
            "name": "Black Monday (1987)",
            "date": "October 19, 1987",
            "drop": "-22.6%",
            "description": "Largest single-day percentage drop in S&P 500 history. Caused by program trading and portfolio insurance.",
            "recovery": "Recovered within 2 years",
            "lesson": "Automated trading can amplify market moves"
        },
        {
            "name": "2008 Financial Crisis",
            "date": "September-October 2008",
            "drop": "-57% (peak to trough)",
            "description": "Subprime mortgage crisis led to banking collapse. Lehman Brothers bankruptcy triggered panic.",
            "recovery": "Took 5.5 years to recover",
            "lesson": "Leverage and interconnected risks can be catastrophic"
        },
        {
            "name": "COVID-19 Crash (2020)",
            "date": "February-March 2020",
            "drop": "-34% in 33 days",
            "description": "Fastest bear market in history. Global pandemic fears caused massive selloff.",
            "recovery": "Recovered in just 5 months",
            "lesson": "Markets can recover faster than expected"
        },
        {
            "name": "Dot-Com Bubble (2000-2002)",
            "date": "March 2000 - October 2002",
            "drop": "-49%",
            "description": "Tech bubble burst after excessive speculation in internet stocks.",
            "recovery": "Took 7 years to recover",
            "lesson": "Valuations matter; speculation ends badly"
        },
        {
            "name": "Black Tuesday (1929)",
            "date": "October 29, 1929",
            "drop": "-12% (single day), -89% (total)",
            "description": "Start of the Great Depression. Market didn't recover for 25 years.",
            "recovery": "25 years to recover",
            "lesson": "The importance of diversification and cash reserves"
        },
    ],
    "bull_runs": [
        {
            "name": "Post-WWII Bull Market",
            "period": "1949-1956",
            "gain": "+267%",
            "description": "Economic expansion after World War II drove massive growth.",
            "lesson": "Economic recovery drives markets"
        },
        {
            "name": "1990s Tech Boom",
            "period": "1990-2000",
            "gain": "+417%",
            "description": "Internet revolution and tech innovation drove unprecedented gains.",
            "lesson": "Innovation creates wealth, but watch valuations"
        },
        {
            "name": "2009-2020 Bull Market",
            "period": "March 2009 - February 2020",
            "gain": "+400%",
            "description": "Longest bull market in history. Fed support and tech growth.",
            "lesson": "Don't fight the Fed"
        },
        {
            "name": "Post-COVID Rally",
            "period": "March 2020 - December 2021",
            "gain": "+114%",
            "description": "Stimulus and reopening drove explosive recovery.",
            "lesson": "Markets climb a wall of worry"
        },
    ],
    "best_days": [
        {"date": "October 13, 2008", "gain": "+11.6%", "context": "During financial crisis - relief rally"},
        {"date": "October 28, 2008", "gain": "+10.8%", "context": "During financial crisis"},
        {"date": "March 24, 2020", "gain": "+9.4%", "context": "COVID stimulus announcement"},
        {"date": "March 13, 2020", "gain": "+9.3%", "context": "COVID emergency measures"},
        {"date": "March 15, 1933", "gain": "+15.3%", "context": "FDR bank holiday end"},
    ],
    "worst_days": [
        {"date": "October 19, 1987", "loss": "-22.6%", "context": "Black Monday"},
        {"date": "October 28, 1929", "loss": "-12.8%", "context": "Great Depression start"},
        {"date": "March 16, 2020", "loss": "-12.0%", "context": "COVID panic"},
        {"date": "October 29, 1929", "loss": "-11.7%", "context": "Black Tuesday"},
        {"date": "December 1, 2008", "loss": "-8.9%", "context": "Recession confirmed"},
    ],
    "seasonality": [
        {"pattern": "January Effect", "description": "Stocks tend to rise in January, especially small caps. Historically +1.2% average."},
        {"pattern": "Sell in May", "description": "'Sell in May and go away' - Summer months historically weaker. May-Oct avg +1.8% vs Nov-Apr +7.1%"},
        {"pattern": "Santa Claus Rally", "description": "Last 5 days of December + first 2 of January tend to be bullish. ~75% success rate."},
        {"pattern": "September Effect", "description": "Historically the worst month for stocks. Average return -1.0% since 1928."},
        {"pattern": "Pre-Holiday Effect", "description": "Day before major US holidays tends to be positive ~65% of the time."},
        {"pattern": "Monday Effect", "description": "Mondays historically show lower returns than other days."},
    ]
}

# ============================================================================
# TRADING TIPS DATABASE
# ============================================================================

TRADING_TIPS = [
    # Risk Management
    ("Never risk more than 1-2% of your capital on a single trade.", "Risk Management", "Position Sizing"),
    ("Always use stop losses - they're your insurance policy.", "Risk Management", "Stop Loss"),
    ("The first loss is the best loss - cut losers quickly.", "Risk Management", "Loss Cutting"),
    ("Don't add to a losing position (averaging down without a plan).", "Risk Management", "Averaging"),
    ("Risk/Reward should be at least 1:2 - risk $1 to make $2.", "Risk Management", "R:R Ratio"),

    # Psychology
    ("Trade the plan, not your emotions.", "Psychology", "Discipline"),
    ("Fear and greed are your worst enemies.", "Psychology", "Emotions"),
    ("Keep a trading journal - review wins AND losses.", "Psychology", "Journaling"),
    ("Accept that losses are part of trading - no one wins 100%.", "Psychology", "Acceptance"),
    ("Don't revenge trade after a loss.", "Psychology", "Revenge Trading"),
    ("Take breaks - overtrading leads to mistakes.", "Psychology", "Rest"),

    # Technical
    ("The trend is your friend - until it ends.", "Technical", "Trends"),
    ("Support and resistance levels are not exact - use zones.", "Technical", "S&R"),
    ("Volume confirms price moves - watch for divergences.", "Technical", "Volume"),
    ("Multiple timeframe analysis gives better context.", "Technical", "Timeframes"),
    ("Don't fight the trend - it's easier to swim with the current.", "Technical", "Trend Following"),

    # Strategy
    ("Have a written trading plan before entering any trade.", "Strategy", "Planning"),
    ("Know your exit before your entry.", "Strategy", "Exit Planning"),
    ("Backtest your strategy before using real money.", "Strategy", "Backtesting"),
    ("Paper trade new strategies first.", "Strategy", "Paper Trading"),
    ("Specialize in one market or strategy before diversifying.", "Strategy", "Focus"),

    # Money Management
    ("Protect your capital - you need it to trade tomorrow.", "Money", "Capital Preservation"),
    ("Don't trade with money you can't afford to lose.", "Money", "Risk Capital"),
    ("Compound gains - let winners run with trailing stops.", "Money", "Compounding"),
    ("Withdraw some profits - enjoy your success.", "Money", "Profit Taking"),
]

# ============================================================================
# FUNDAMENTAL ANALYSIS DATA
# ============================================================================

FUNDAMENTAL_CONCEPTS = [
    {
        "title": "P/E Ratio (Price-to-Earnings)",
        "formula": "Stock Price / Earnings Per Share",
        "interpretation": "Lower P/E may indicate undervalued stock. S&P 500 historical average: 15-17x",
        "current_note": "Above 20 = expensive, Below 15 = cheap (generally)"
    },
    {
        "title": "PEG Ratio",
        "formula": "P/E Ratio / Earnings Growth Rate",
        "interpretation": "PEG < 1 suggests stock may be undervalued relative to growth",
        "current_note": "Accounts for growth, unlike simple P/E"
    },
    {
        "title": "Dividend Yield",
        "formula": "Annual Dividend / Stock Price",
        "interpretation": "S&P 500 average yield: 1.5-2%. Higher = income, but check sustainability",
        "current_note": "Compare to 10-year Treasury yield"
    },
    {
        "title": "Price-to-Book (P/B)",
        "formula": "Stock Price / Book Value per Share",
        "interpretation": "P/B < 1 means trading below asset value. Banks typically 1-1.5x",
        "current_note": "Less useful for tech companies"
    },
    {
        "title": "Debt-to-Equity Ratio",
        "formula": "Total Debt / Shareholders' Equity",
        "interpretation": "Higher ratio = more leverage/risk. Varies by industry",
        "current_note": "Watch for increasing debt levels"
    },
    {
        "title": "Free Cash Flow",
        "formula": "Operating Cash Flow - Capital Expenditures",
        "interpretation": "Positive FCF = company generates cash after investments",
        "current_note": "More reliable than earnings (harder to manipulate)"
    },
    {
        "title": "Return on Equity (ROE)",
        "formula": "Net Income / Shareholders' Equity",
        "interpretation": "Higher ROE = more efficient use of equity. >15% is good",
        "current_note": "Compare within same industry"
    },
    {
        "title": "Earnings Growth Rate",
        "formula": "Year-over-Year EPS Change",
        "interpretation": "Consistent growth is key. Look for 10%+ annual growth",
        "current_note": "Check multi-year trend, not just one quarter"
    },
]

ECONOMIC_INDICATORS = [
    {
        "name": "Federal Funds Rate",
        "impact": "Higher rates = bearish for stocks (usually), Lower rates = bullish",
        "why": "Affects borrowing costs for companies and consumers"
    },
    {
        "name": "GDP Growth",
        "impact": "Strong GDP = bullish, Negative GDP = recession risk",
        "why": "Measures overall economic health"
    },
    {
        "name": "Unemployment Rate",
        "impact": "Low unemployment = strong economy, but watch for Fed response",
        "why": "Indicates labor market health"
    },
    {
        "name": "CPI (Inflation)",
        "impact": "High inflation = Fed may raise rates = bearish pressure",
        "why": "Fed's primary concern affecting monetary policy"
    },
    {
        "name": "PMI (Manufacturing)",
        "impact": "Above 50 = expansion, Below 50 = contraction",
        "why": "Leading indicator of economic activity"
    },
    {
        "name": "Consumer Confidence",
        "impact": "High confidence = consumers spend more = bullish",
        "why": "Consumer spending is 70% of US GDP"
    },
    {
        "name": "10-Year Treasury Yield",
        "impact": "Rising yields compete with stocks for investment",
        "why": "Benchmark for mortgage rates and stock valuations"
    },
    {
        "name": "Yield Curve (10Y-2Y)",
        "impact": "Inverted curve (negative) has predicted every recession since 1955",
        "why": "Shows market expectations for future growth"
    },
]

# ============================================================================
# POST GENERATION FUNCTIONS
# ============================================================================

def post_technical_analysis():
    """Post technical analysis update"""
    df = get_features_data()
    price_df = get_price_data(30)

    if df.empty or price_df.empty:
        return post_technical_education()

    latest = df.iloc[-1]
    current_price = price_df['Close'].iloc[-1]

    # Get indicators
    rsi = latest.get('rsi_14', 50)
    macd = latest.get('macd', 0)
    macd_signal = latest.get('macd_signal', 0)
    macd_hist = latest.get('macd_histogram', 0)
    bb_upper = latest.get('bb_upper', current_price * 1.02)
    bb_lower = latest.get('bb_lower', current_price * 0.98)
    sma_20 = latest.get('sma_20', current_price)
    sma_50 = latest.get('sma_50', current_price)

    # RSI interpretation
    if rsi > 70:
        rsi_signal = "OVERBOUGHT - Potential pullback"
        rsi_emoji = "🔴"
    elif rsi < 30:
        rsi_signal = "OVERSOLD - Potential bounce"
        rsi_emoji = "🟢"
    elif rsi > 60:
        rsi_signal = "Bullish momentum"
        rsi_emoji = "📈"
    elif rsi < 40:
        rsi_signal = "Bearish momentum"
        rsi_emoji = "📉"
    else:
        rsi_signal = "Neutral zone"
        rsi_emoji = "➡️"

    # MACD interpretation
    if macd > macd_signal and macd_hist > 0:
        macd_signal_text = "BULLISH - Above signal line"
        macd_emoji = "🟢"
    elif macd < macd_signal and macd_hist < 0:
        macd_signal_text = "BEARISH - Below signal line"
        macd_emoji = "🔴"
    else:
        macd_signal_text = "Crossover zone - Watch closely"
        macd_emoji = "⚠️"

    # Bollinger Bands position
    bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) * 100
    if bb_position > 80:
        bb_signal = "Near upper band - Extended"
        bb_emoji = "🔴"
    elif bb_position < 20:
        bb_signal = "Near lower band - Oversold"
        bb_emoji = "🟢"
    else:
        bb_signal = "Within normal range"
        bb_emoji = "➡️"

    # Trend (SMA)
    if current_price > sma_20 > sma_50:
        trend = "UPTREND - Price above all MAs"
        trend_emoji = "📈"
    elif current_price < sma_20 < sma_50:
        trend = "DOWNTREND - Price below all MAs"
        trend_emoji = "📉"
    else:
        trend = "MIXED - Possible transition"
        trend_emoji = "↔️"

    msg = f"""
📊 <b>TECHNICAL ANALYSIS UPDATE</b>
<i>{datetime.now().strftime('%H:%M')} ET</i>

<b>S&P 500: ${current_price:,.2f}</b>

{trend_emoji} <b>Trend:</b> {trend}

📈 <b>Indicators:</b>

{rsi_emoji} <b>RSI (14):</b> {rsi:.1f}
   └─ {rsi_signal}

{macd_emoji} <b>MACD:</b> {macd:.2f}
   └─ {macd_signal_text}

{bb_emoji} <b>Bollinger Bands:</b>
   └─ Upper: ${bb_upper:,.2f}
   └─ Lower: ${bb_lower:,.2f}
   └─ Position: {bb_position:.0f}% ({bb_signal})

📏 <b>Moving Averages:</b>
   └─ SMA 20: ${sma_20:,.2f}
   └─ SMA 50: ${sma_50:,.2f}

#TechnicalAnalysis #SP500 #RSI #MACD #Trading
"""
    return send_telegram_message(msg)


def post_technical_education():
    """Post educational technical analysis content"""
    topics = [
        {
            "title": "RSI (Relative Strength Index)",
            "content": """
📊 <b>RSI - Relative Strength Index</b>

<b>What it is:</b>
Momentum indicator measuring speed of price changes (0-100)

<b>Key Levels:</b>
• Above 70 = OVERBOUGHT (potential sell)
• Below 30 = OVERSOLD (potential buy)
• 50 = Neutral line

<b>How to use:</b>
• Look for divergences with price
• Combine with trend direction
• Don't trade RSI alone

⚠️ In strong trends, RSI can stay overbought/oversold for extended periods!

#RSI #TechnicalAnalysis #Education"""
        },
        {
            "title": "MACD",
            "content": """
📊 <b>MACD - Moving Average Convergence Divergence</b>

<b>Components:</b>
• MACD Line = 12 EMA - 26 EMA
• Signal Line = 9 EMA of MACD
• Histogram = MACD - Signal

<b>Signals:</b>
🟢 BUY: MACD crosses ABOVE signal line
🔴 SELL: MACD crosses BELOW signal line

<b>Tips:</b>
• Watch for divergences with price
• Histogram shows momentum strength
• Works best in trending markets

#MACD #TechnicalAnalysis #Education"""
        },
        {
            "title": "Bollinger Bands",
            "content": """
📊 <b>Bollinger Bands</b>

<b>Structure:</b>
• Middle = 20-day SMA
• Upper = SMA + 2 standard deviations
• Lower = SMA - 2 standard deviations

<b>Signals:</b>
• Price at upper band = Overbought
• Price at lower band = Oversold
• Band squeeze = Low volatility, breakout coming

<b>Strategy:</b>
Mean reversion: Buy at lower, sell at upper (in ranges)
Breakout: Trade in direction of band break

#BollingerBands #TechnicalAnalysis #Volatility"""
        },
        {
            "title": "Support & Resistance",
            "content": """
📊 <b>Support & Resistance Levels</b>

<b>Support:</b>
Price level where buying pressure exceeds selling
• Previous lows
• Round numbers ($5000, $5500)
• Moving averages

<b>Resistance:</b>
Price level where selling pressure exceeds buying
• Previous highs
• Round numbers
• Trendlines

<b>Key Rules:</b>
• The more touches, the stronger the level
• Broken support becomes resistance (and vice versa)
• Use zones, not exact prices

#SupportResistance #TechnicalAnalysis #PriceAction"""
        },
        {
            "title": "Candlestick Patterns",
            "content": """
📊 <b>Key Candlestick Patterns</b>

<b>Bullish Patterns:</b>
🟢 Hammer - Long lower wick, small body at top
🟢 Engulfing - Green candle engulfs previous red
🟢 Morning Star - 3-candle reversal pattern

<b>Bearish Patterns:</b>
🔴 Shooting Star - Long upper wick, small body at bottom
🔴 Engulfing - Red candle engulfs previous green
🔴 Evening Star - 3-candle reversal pattern

<b>Doji:</b>
⚪ Indecision - Open = Close, watch next candle

#Candlesticks #TechnicalAnalysis #PriceAction"""
        },
    ]

    topic = random.choice(topics)
    return send_telegram_message(topic["content"])


def post_fundamental_analysis():
    """Post fundamental analysis education"""
    # Randomly choose between concepts and indicators
    if random.random() > 0.5:
        concept = random.choice(FUNDAMENTAL_CONCEPTS)
        msg = f"""
📚 <b>FUNDAMENTAL ANALYSIS</b>
<i>Understanding the Numbers</i>

📖 <b>{concept['title']}</b>

<b>Formula:</b>
<code>{concept['formula']}</code>

<b>Interpretation:</b>
{concept['interpretation']}

💡 <b>Note:</b>
{concept['current_note']}

#FundamentalAnalysis #Investing #Education
"""
    else:
        indicator = random.choice(ECONOMIC_INDICATORS)
        msg = f"""
🏛️ <b>ECONOMIC INDICATOR</b>
<i>What Moves Markets</i>

📊 <b>{indicator['name']}</b>

<b>Market Impact:</b>
{indicator['impact']}

<b>Why it matters:</b>
{indicator['why']}

💡 Watch for releases on the economic calendar!

#Economics #MacroAnalysis #FederalReserve
"""

    return send_telegram_message(msg)


def post_historical_quote():
    """Post a famous trading/investing quote"""
    quote, author, category = random.choice(FAMOUS_QUOTES)

    msg = f"""
💬 <b>WISDOM FROM THE MASTERS</b>

<i>"{quote}"</i>

— <b>{author}</b>

📚 Category: {category}

#TradingWisdom #Quotes #{author.replace(' ', '')}
"""
    return send_telegram_message(msg)


def post_market_history():
    """Post market history facts"""
    category = random.choice(["crashes", "bull_runs", "best_days", "worst_days", "seasonality"])

    if category == "crashes":
        event = random.choice(MARKET_HISTORY["crashes"])
        msg = f"""
📉 <b>MARKET HISTORY: CRASHES</b>

<b>{event['name']}</b>
📅 {event['date']}

<b>Drop:</b> <code>{event['drop']}</code>

<b>What happened:</b>
{event['description']}

<b>Recovery:</b> {event['recovery']}

💡 <b>Lesson:</b>
{event['lesson']}

#MarketHistory #StockMarketCrash #Investing
"""

    elif category == "bull_runs":
        event = random.choice(MARKET_HISTORY["bull_runs"])
        msg = f"""
📈 <b>MARKET HISTORY: BULL MARKETS</b>

<b>{event['name']}</b>
📅 {event['period']}

<b>Gain:</b> <code>{event['gain']}</code>

<b>What happened:</b>
{event['description']}

💡 <b>Lesson:</b>
{event['lesson']}

#MarketHistory #BullMarket #Investing
"""

    elif category == "best_days":
        day = random.choice(MARKET_HISTORY["best_days"])
        msg = f"""
🚀 <b>MARKET HISTORY: BEST DAYS</b>

📅 <b>{day['date']}</b>

<b>S&P 500 Gain:</b> <code>{day['gain']}</code>

<b>Context:</b>
{day['context']}

💡 Fun fact: The best days often occur during bear markets!

#MarketHistory #StockMarket #BestDays
"""

    elif category == "worst_days":
        day = random.choice(MARKET_HISTORY["worst_days"])
        msg = f"""
💥 <b>MARKET HISTORY: WORST DAYS</b>

📅 <b>{day['date']}</b>

<b>S&P 500 Loss:</b> <code>{day['loss']}</code>

<b>Context:</b>
{day['context']}

💡 Reminder: Markets always recovered eventually!

#MarketHistory #StockMarket #WorstDays
"""

    else:  # seasonality
        pattern = random.choice(MARKET_HISTORY["seasonality"])
        msg = f"""
📆 <b>MARKET SEASONALITY</b>

<b>{pattern['pattern']}</b>

{pattern['description']}

⚠️ Past patterns don't guarantee future results!

#Seasonality #MarketPatterns #Trading
"""

    return send_telegram_message(msg)


def post_trading_tip():
    """Post a trading tip"""
    tip, category, subcategory = random.choice(TRADING_TIPS)

    emojis = {
        "Risk Management": "🛡️",
        "Psychology": "🧠",
        "Technical": "📊",
        "Strategy": "🎯",
        "Money": "💰"
    }

    emoji = emojis.get(category, "💡")

    msg = f"""
{emoji} <b>TRADING TIP</b>
<i>{category} - {subcategory}</i>

💡 <b>{tip}</b>

Save this for later! ⭐

#TradingTips #{category.replace(' ', '')} #Education
"""
    return send_telegram_message(msg)


def post_market_stats():
    """Post current market statistics"""
    df = get_price_data(252)  # 1 year of data

    if df.empty:
        return post_trading_tip()

    current_price = df['Close'].iloc[-1]

    # Calculate various stats
    day_change = ((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100
    week_change = ((df['Close'].iloc[-1] / df['Close'].iloc[-5]) - 1) * 100 if len(df) > 5 else 0
    month_change = ((df['Close'].iloc[-1] / df['Close'].iloc[-22]) - 1) * 100 if len(df) > 22 else 0
    ytd_change = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100

    # High/Low
    high_52w = df['High'].max()
    low_52w = df['Low'].min()
    from_high = ((current_price - high_52w) / high_52w) * 100
    from_low = ((current_price - low_52w) / low_52w) * 100

    # Volatility
    daily_returns = df['Close'].pct_change().dropna()
    volatility = daily_returns.std() * np.sqrt(252) * 100

    # Trend indicator
    if day_change > 0:
        day_emoji = "🟢"
    elif day_change < 0:
        day_emoji = "🔴"
    else:
        day_emoji = "⚪"

    msg = f"""
📊 <b>MARKET STATISTICS</b>
<i>S&P 500 Overview</i>

💰 <b>Current Price:</b> <code>${current_price:,.2f}</code>

<b>Performance:</b>
{day_emoji} Today: <code>{day_change:+.2f}%</code>
📅 Week: <code>{week_change:+.2f}%</code>
📆 Month: <code>{month_change:+.2f}%</code>
📈 YTD: <code>{ytd_change:+.2f}%</code>

<b>52-Week Range:</b>
🔺 High: <code>${high_52w:,.2f}</code> ({from_high:.1f}% from high)
🔻 Low: <code>${low_52w:,.2f}</code> (+{from_low:.1f}% from low)

<b>Volatility (Annualized):</b>
📊 <code>{volatility:.1f}%</code>

#MarketStats #SP500 #StockMarket
"""
    return send_telegram_message(msg)


def post_did_you_know():
    """Post interesting market facts"""
    facts = [
        "The S&P 500 has returned an average of ~10% per year since 1926, including dividends.",
        "If you invested $10,000 in the S&P 500 in 1980, it would be worth over $1 million today.",
        "The stock market has been positive in about 70% of all years since 1928.",
        "Missing the 10 best days in the market over 20 years can cut your returns in half.",
        "The S&P 500 index was created in 1957, but was backdated to 1928.",
        "Only 4% of stocks account for all the net gains in the stock market since 1926.",
        "The average bull market lasts 5.5 years; the average bear market lasts 1.3 years.",
        "January has historically been one of the best months for stocks (+1.2% average).",
        "The term 'bull market' comes from how bulls attack: thrusting horns upward.",
        "The term 'bear market' comes from how bears attack: swiping paws downward.",
        "Monday is historically the worst day for stock returns.",
        "The VIX (fear index) tends to spike during market crashes and fall during rallies.",
        "Warren Buffett has beaten the S&P 500 over his career with ~20% annual returns.",
        "Index funds now hold over 50% of all US stock fund assets.",
        "The Flash Crash of 2010 saw the Dow drop 1,000 points in minutes, then recover.",
    ]

    fact = random.choice(facts)

    msg = f"""
🤔 <b>DID YOU KNOW?</b>

💡 {fact}

#DidYouKnow #MarketFacts #Investing
"""
    return send_telegram_message(msg)


# ============================================================================
# CONTENT ROTATION SYSTEM
# ============================================================================

# Define content types and their weights (probability)
CONTENT_TYPES = [
    (post_technical_analysis, 20),      # 20% chance
    (post_fundamental_analysis, 15),    # 15% chance
    (post_historical_quote, 15),        # 15% chance
    (post_market_history, 15),          # 15% chance
    (post_trading_tip, 15),             # 15% chance
    (post_market_stats, 10),            # 10% chance
    (post_did_you_know, 10),            # 10% chance
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

    return CONTENT_TYPES[0][0]  # Default fallback


def post_15min_content():
    """Post content for 15-minute interval"""
    print(f"\n{'='*60}")
    print(f"Posting 15-minute content...")
    print(f"Time (ET): {get_current_time_et().strftime('%H:%M:%S')}")
    print(f"Time (Morocco): {get_current_time_morocco().strftime('%H:%M:%S')}")
    print(f"{'='*60}")

    # Get random content type
    content_func = get_weighted_random_content()
    print(f"Selected content: {content_func.__name__}")

    return content_func()


def post_specific_content(content_type):
    """Post specific content type"""
    content_map = {
        "technical": post_technical_analysis,
        "fundamental": post_fundamental_analysis,
        "quote": post_historical_quote,
        "history": post_market_history,
        "tip": post_trading_tip,
        "stats": post_market_stats,
        "fact": post_did_you_know,
    }

    if content_type in content_map:
        return content_map[content_type]()
    else:
        print(f"Unknown content type: {content_type}")
        print(f"Available: {', '.join(content_map.keys())}")
        return False


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("S&P 500 - 15-MINUTE CONTENT BOT")
    print("="*60)

    now_et = get_current_time_et()
    now_morocco = get_current_time_morocco()
    print(f"Time (ET):      {now_et.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Time (Morocco): {now_morocco.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == "auto":
            # Auto post random content
            post_15min_content()
        elif cmd in ["technical", "fundamental", "quote", "history", "tip", "stats", "fact"]:
            post_specific_content(cmd)
        elif cmd == "test":
            # Test all content types
            print("\nTesting all content types...")
            for func, _ in CONTENT_TYPES:
                print(f"\n>>> Testing: {func.__name__}")
                input("Press Enter to send...")
                func()
        elif cmd == "help":
            print("""
Usage: python telegram_15min_bot.py [command]

Commands:
  auto        - Post random content (for scheduler)
  technical   - Post technical analysis
  fundamental - Post fundamental analysis
  quote       - Post famous quote
  history     - Post market history
  tip         - Post trading tip
  stats       - Post market statistics
  fact        - Post "Did you know"
  test        - Test all content types interactively
  help        - Show this help
            """)
        else:
            print(f"Unknown command: {cmd}")
    else:
        # Default: auto post
        post_15min_content()
