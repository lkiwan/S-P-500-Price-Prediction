# -*- coding: utf-8 -*-
"""
S&P 500 News Fetcher
====================
Fetches market news from free APIs and generates AI commentary.

APIs Used:
- Finnhub (Free: 60 req/min) - requires API key
- Yahoo Finance RSS (Free, no key needed)
- Groq AI for commentary generation
"""

import os
import requests
import json
from datetime import datetime, timedelta
import warnings
import re
import xml.etree.ElementTree as ET
warnings.filterwarnings('ignore')

# Try to import Groq AI
try:
    from groq_ai import call_groq_api, GROQ_API_KEY
    GROQ_AVAILABLE = GROQ_API_KEY and GROQ_API_KEY != ""
except:
    GROQ_AVAILABLE = False

# ============================================================================
# CONFIGURATION
# ============================================================================

# Finnhub API (get free key at: https://finnhub.io/register)
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")

# Try to load from config file
if not FINNHUB_API_KEY:
    config_file = os.path.join(os.path.dirname(__file__), '.finnhub_key')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            FINNHUB_API_KEY = f.read().strip()

FINNHUB_AVAILABLE = bool(FINNHUB_API_KEY)

# ============================================================================
# YAHOO FINANCE RSS (No API Key Needed)
# ============================================================================

def fetch_yahoo_finance_news(limit=5):
    """
    Fetch S&P 500 related news from Yahoo Finance RSS feed.
    No API key required.
    """
    news_items = []

    # Yahoo Finance RSS feeds
    feeds = [
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC&region=US&lang=en-US",  # S&P 500
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s=SPY&region=US&lang=en-US",  # SPY ETF
    ]

    for feed_url in feeds:
        try:
            response = requests.get(feed_url, timeout=10, verify=False)
            if response.status_code == 200:
                # Parse XML
                root = ET.fromstring(response.content)

                for item in root.findall('.//item'):
                    title = item.find('title')
                    link = item.find('link')
                    pub_date = item.find('pubDate')

                    if title is not None:
                        news_items.append({
                            'title': title.text,
                            'url': link.text if link is not None else '',
                            'published': pub_date.text if pub_date is not None else '',
                            'source': 'Yahoo Finance'
                        })
        except Exception as e:
            print(f"Error fetching Yahoo RSS: {e}")
            continue

    # Remove duplicates and limit
    seen_titles = set()
    unique_news = []
    for item in news_items:
        if item['title'] not in seen_titles:
            seen_titles.add(item['title'])
            unique_news.append(item)

    return unique_news[:limit]


# ============================================================================
# FINNHUB API (Free with API Key)
# ============================================================================

def fetch_finnhub_news(limit=5):
    """
    Fetch market news from Finnhub API.
    Requires free API key from https://finnhub.io/register
    """
    if not FINNHUB_AVAILABLE:
        return []

    url = "https://finnhub.io/api/v1/news"
    params = {
        "category": "general",
        "token": FINNHUB_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()

            news_items = []
            for item in data[:limit]:
                news_items.append({
                    'title': item.get('headline', ''),
                    'summary': item.get('summary', ''),
                    'url': item.get('url', ''),
                    'source': item.get('source', 'Finnhub'),
                    'published': datetime.fromtimestamp(item.get('datetime', 0)).strftime('%Y-%m-%d %H:%M')
                })

            return news_items
    except Exception as e:
        print(f"Error fetching Finnhub news: {e}")

    return []


# ============================================================================
# COMBINED NEWS FETCHER
# ============================================================================

def fetch_market_news(limit=5):
    """
    Fetch market news from available sources.
    Priority: Finnhub > Yahoo Finance
    """
    news = []

    # Try Finnhub first
    if FINNHUB_AVAILABLE:
        news = fetch_finnhub_news(limit)
        if news:
            return news

    # Fallback to Yahoo Finance RSS
    news = fetch_yahoo_finance_news(limit)

    return news


# ============================================================================
# AI-POWERED NEWS ANALYSIS
# ============================================================================

def generate_ai_market_news():
    """
    Generate AI-powered market news commentary.
    Uses current market data and AI to create insightful commentary.
    """
    if not GROQ_AVAILABLE:
        return None

    prompt = """Generate a brief market news update for a Telegram trading channel.

Create a realistic market commentary that includes:
1. Current market sentiment (bullish/bearish/neutral)
2. Key factors affecting S&P 500 today
3. What traders should watch for

Format for Telegram with:
- HTML tags (<b>, <i>, <code>)
- Emojis for visual appeal
- Clear sections with separators
- Keep it under 200 words
- Include hashtags at the end

Make it sound like a professional market analyst reporting current conditions."""

    system_prompt = """You are a professional S&P 500 market analyst providing daily market updates.
Your commentary should be:
- Professional but engaging
- Based on typical market factors (Fed policy, earnings, economic data, etc.)
- Educational for traders
- Include actionable insights"""

    return call_groq_api(prompt, system_prompt, max_tokens=400, temperature=0.7)


def generate_news_summary_with_ai(headlines):
    """
    Use AI to create a summary of news headlines.
    """
    if not GROQ_AVAILABLE or not headlines:
        return None

    headlines_text = "\n".join([f"- {h['title']}" for h in headlines[:5]])

    prompt = f"""Summarize these S&P 500 market news headlines for a Telegram channel:

{headlines_text}

Create a brief, engaging summary that:
1. Highlights the most important news
2. Explains potential market impact
3. Gives traders key takeaways

Format with HTML tags, emojis, and hashtags. Keep under 200 words."""

    return call_groq_api(prompt, max_tokens=350, temperature=0.6)


# ============================================================================
# TELEGRAM MESSAGE FORMATTERS
# ============================================================================

def format_news_message(news_items, include_ai_summary=True):
    """
    Format news items for Telegram posting.
    """
    if not news_items:
        return None

    date_str = datetime.now().strftime("%B %d, %Y • %H:%M")

    msg = f"""
📰📰📰 <b>MARKET NEWS UPDATE</b> 📰📰📰

📅 {date_str}

━━━━━━━━━━━━━━━━━━━━━━

📢 <b>Latest Headlines:</b>

"""

    for i, item in enumerate(news_items[:5], 1):
        title = item['title']
        source = item.get('source', 'News')

        # Emoji based on content
        if any(word in title.lower() for word in ['surge', 'jump', 'rally', 'gain', 'rise', 'up', 'bull']):
            emoji = "📈"
        elif any(word in title.lower() for word in ['drop', 'fall', 'crash', 'down', 'bear', 'loss', 'decline']):
            emoji = "📉"
        elif any(word in title.lower() for word in ['fed', 'rate', 'inflation', 'economy']):
            emoji = "🏛️"
        else:
            emoji = "📌"

        msg += f"   {emoji} <b>{i}.</b> {title}\n      <i>— {source}</i>\n\n"

    msg += "━━━━━━━━━━━━━━━━━━━━━━\n"

    # Add AI summary if available
    if include_ai_summary and GROQ_AVAILABLE:
        ai_summary = generate_news_summary_with_ai(news_items)
        if ai_summary:
            msg += f"\n🤖 <b>AI Analysis:</b>\n\n{ai_summary}\n\n"
            msg += "━━━━━━━━━━━━━━━━━━━━━━\n"

    msg += """
💡 <i>Stay informed, trade wisely!</i>

#MarketNews #SP500 #StockMarket #Trading
"""

    return msg


def get_news_for_telegram(include_ai=True):
    """
    Get formatted news message ready for Telegram.
    Returns AI-generated news if no real news available.
    """
    # Try to fetch real news
    news = fetch_market_news(5)

    if news:
        return format_news_message(news, include_ai_summary=include_ai)

    # Fallback to AI-generated commentary
    if GROQ_AVAILABLE:
        ai_news = generate_ai_market_news()
        if ai_news:
            date_str = datetime.now().strftime("%B %d, %Y • %H:%M")
            return f"""
📰📰📰 <b>MARKET UPDATE</b> 📰📰📰

📅 {date_str}

━━━━━━━━━━━━━━━━━━━━━━

{ai_news}

━━━━━━━━━━━━━━━━━━━━━━

💡 <i>AI-Generated Market Commentary</i>

#MarketNews #SP500 #AIAnalysis #Trading
"""

    return None


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("S&P 500 News Fetcher Test")
    print("="*60)

    print(f"\nFinnhub API: {'Available' if FINNHUB_AVAILABLE else 'Not configured'}")
    print(f"Groq AI: {'Available' if GROQ_AVAILABLE else 'Not configured'}")

    print("\n" + "="*60)
    print("Fetching Yahoo Finance RSS...")
    print("="*60)

    yahoo_news = fetch_yahoo_finance_news(3)
    for item in yahoo_news:
        print(f"\n📰 {item['title']}")
        print(f"   Source: {item['source']}")

    if FINNHUB_AVAILABLE:
        print("\n" + "="*60)
        print("Fetching Finnhub News...")
        print("="*60)

        finnhub_news = fetch_finnhub_news(3)
        for item in finnhub_news:
            print(f"\n📰 {item['title']}")
            print(f"   Source: {item['source']}")

    print("\n" + "="*60)
    print("Generating Telegram Message...")
    print("="*60)

    telegram_msg = get_news_for_telegram()
    if telegram_msg:
        print("\n[Message Preview]")
        print(telegram_msg[:500] + "...")
    else:
        print("\nNo news available")
