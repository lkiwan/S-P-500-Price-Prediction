# -*- coding: utf-8 -*-
"""
Groq AI Integration for S&P 500 Telegram Bot
=============================================
Uses Groq's free API with Llama 3 for intelligent message generation.

Get your FREE API key at: https://console.groq.com/keys
"""

import os
import requests
import json
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get API key from environment variable or config file
# Set your key in environment: set GROQ_API_KEY=your_key_here
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Try to load from config file if not in environment
if not GROQ_API_KEY:
    config_file = os.path.join(os.path.dirname(__file__), '.groq_key')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            GROQ_API_KEY = f.read().strip()

# Groq API endpoint
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Available models (all free!)
MODELS = {
    "llama3-70b": "llama-3.3-70b-versatile",      # Best quality
    "llama3-8b": "llama-3.1-8b-instant",          # Fastest
    "mixtral": "mixtral-8x7b-32768",              # Good balance
    "gemma": "gemma2-9b-it",                      # Google's model
}

# Default model
DEFAULT_MODEL = MODELS["llama3-70b"]


# ============================================================================
# GROQ API FUNCTIONS
# ============================================================================

def call_groq_api(prompt, system_prompt=None, model=DEFAULT_MODEL, max_tokens=1000, temperature=0.7):
    """
    Call Groq API to generate text.

    Args:
        prompt: User prompt
        system_prompt: System instructions
        model: Model to use
        max_tokens: Maximum response length
        temperature: Creativity (0-1)

    Returns:
        Generated text or None if error
    """
    if GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        print("[WARNING] Groq API key not set! Get free key at: https://console.groq.com/keys")
        return None

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30, verify=False)

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            print(f"[ERROR] Groq API error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"[ERROR] Groq API call failed: {e}")
        return None


# ============================================================================
# TRADING-SPECIFIC AI FUNCTIONS
# ============================================================================

TRADING_SYSTEM_PROMPT = """You are a professional S&P 500 market analyst for a Telegram trading channel.
Your role is to provide educational, insightful, and engaging content about the stock market.

Rules:
- Keep messages concise (max 200 words)
- Use emojis appropriately for Telegram
- Be professional but engaging
- Include relevant hashtags at the end
- Never give specific financial advice (use disclaimers)
- Focus on education and analysis
- Use HTML formatting: <b>bold</b>, <i>italic</i>, <code>code</code>
"""


def generate_technical_analysis(price, rsi, macd, trend, atr):
    """Generate AI-powered technical analysis"""

    prompt = f"""Generate a technical analysis update for S&P 500 Telegram channel.

Current Data:
- Price: ${price:,.2f}
- RSI (14): {rsi:.1f}
- MACD: {macd:.2f}
- Trend: {trend}
- ATR (Volatility): {atr:.2f}

Create an engaging technical analysis post with:
1. Current market condition assessment
2. Key indicator interpretations
3. What traders should watch for
4. Educational insight about one indicator

Use HTML formatting for Telegram. Add relevant emojis and hashtags."""

    return call_groq_api(prompt, TRADING_SYSTEM_PROMPT, temperature=0.7)


def generate_market_insight():
    """Generate a random market insight/education post"""

    topics = [
        "a lesser-known but powerful trading indicator",
        "a common mistake traders make and how to avoid it",
        "an interesting pattern in market history",
        "the psychology behind market movements",
        "risk management best practices",
        "how institutional traders think differently",
        "the importance of position sizing",
        "reading market sentiment effectively",
        "understanding market cycles",
        "the role of volume in trading decisions"
    ]

    import random
    topic = random.choice(topics)

    prompt = f"""Create an educational Telegram post about {topic}.

Requirements:
- Start with an attention-grabbing emoji and title
- Explain the concept clearly for beginners
- Give a practical example or tip
- End with a key takeaway
- Use HTML formatting (<b>, <i>, <code>)
- Keep it under 200 words
- Add relevant hashtags"""

    return call_groq_api(prompt, TRADING_SYSTEM_PROMPT, temperature=0.8)


def generate_quote_analysis(quote, author):
    """Generate analysis of a famous trading quote"""

    prompt = f"""Analyze this famous trading quote for a Telegram channel:

"{quote}" - {author}

Create a post that:
1. Shows the quote beautifully formatted
2. Explains what it means in practical terms
3. Gives a real-world trading example
4. Provides a modern application of this wisdom

Use HTML formatting, emojis, and hashtags. Keep under 200 words."""

    return call_groq_api(prompt, TRADING_SYSTEM_PROMPT, temperature=0.7)


def generate_market_history_insight(event_name, event_details):
    """Generate insight about a historical market event"""

    prompt = f"""Create an educational post about this historical market event:

Event: {event_name}
Details: {event_details}

Create an engaging Telegram post that:
1. Describes what happened
2. Explains why it happened
3. What lessons traders can learn
4. How it relates to today's market

Use HTML formatting, emojis, and hashtags. Keep under 200 words."""

    return call_groq_api(prompt, TRADING_SYSTEM_PROMPT, temperature=0.7)


def generate_morning_analysis(price, prediction, confidence, key_levels):
    """Generate AI-powered morning market analysis"""

    prompt = f"""Create a morning market analysis for S&P 500 Telegram channel.

Data:
- Current Price: ${price:,.2f}
- AI Prediction: {prediction}
- Model Confidence: {confidence:.1f}%
- Key Resistance: ${key_levels.get('resistance', 0):,.2f}
- Key Support: ${key_levels.get('support', 0):,.2f}

Create an engaging morning briefing that:
1. Welcomes traders to the day
2. Summarizes the market setup
3. Highlights key levels to watch
4. Sets expectations for the session
5. Reminds about risk management

Use HTML formatting, emojis, and hashtags."""

    return call_groq_api(prompt, TRADING_SYSTEM_PROMPT, temperature=0.6)


def generate_trading_tip():
    """Generate a random AI-powered trading tip"""

    prompt = """Generate a unique, valuable trading tip for a Telegram channel.

The tip should be:
1. Practical and actionable
2. Suitable for intermediate traders
3. Related to S&P 500 or index trading
4. Something not commonly discussed

Format:
- Start with a lightbulb emoji and "TRADING TIP"
- Present the tip clearly
- Explain why it works
- Give a practical example
- End with a key takeaway

Use HTML formatting, emojis, and hashtags. Keep under 150 words."""

    return call_groq_api(prompt, TRADING_SYSTEM_PROMPT, temperature=0.9)


def generate_did_you_know():
    """Generate an interesting market fact"""

    prompt = """Generate a fascinating "Did You Know?" fact about the stock market.

Requirements:
- Must be a real, verifiable fact
- Surprising or counter-intuitive
- Related to S&P 500, trading, or market history
- Educational value

Format:
- Start with thinking emoji and "DID YOU KNOW?"
- Present the fact
- Add brief context or explanation
- Why it matters for traders

Use HTML formatting, emojis, and hashtags. Keep under 120 words."""

    return call_groq_api(prompt, TRADING_SYSTEM_PROMPT, temperature=0.8)


def generate_fundamental_insight():
    """Generate fundamental analysis education"""

    topics = [
        "P/E ratio and what it really tells us",
        "earnings reports and how to interpret them",
        "Federal Reserve decisions and market impact",
        "inflation data and stock prices",
        "GDP growth and market correlation",
        "unemployment data as a market indicator",
        "bond yields and their effect on stocks",
        "sector rotation and economic cycles"
    ]

    import random
    topic = random.choice(topics)

    prompt = f"""Create an educational post about {topic} for a Telegram trading channel.

Requirements:
- Explain the concept simply
- Show how it affects S&P 500
- Give a practical example
- Include current relevance
- End with what to watch for

Use HTML formatting, emojis, and hashtags. Keep under 180 words."""

    return call_groq_api(prompt, TRADING_SYSTEM_PROMPT, temperature=0.7)


def generate_signal_analysis(direction, entry, tp, sl, confidence, rr_ratio):
    """Generate AI analysis of a trading signal"""

    prompt = f"""Analyze this S&P 500 trading signal for Telegram:

Signal Details:
- Direction: {direction}
- Entry Price: ${entry:,.2f}
- Take Profit: ${tp:,.2f}
- Stop Loss: ${sl:,.2f}
- Confidence: {confidence:.1f}%
- Risk/Reward Ratio: {rr_ratio:.2f}

Create a post that:
1. Presents the signal clearly with emojis
2. Explains the reasoning (technical context)
3. Highlights the risk/reward
4. Reminds about position sizing
5. Adds a risk disclaimer

Use HTML formatting. Keep professional but engaging."""

    return call_groq_api(prompt, TRADING_SYSTEM_PROMPT, temperature=0.5)


def generate_end_of_day_summary(open_price, close_price, high, low, signal_result, pnl):
    """Generate AI-powered end of day summary"""

    day_change = ((close_price - open_price) / open_price) * 100
    day_emoji = "🟢" if day_change > 0 else "🔴" if day_change < 0 else "⚪"

    prompt = f"""Create an end-of-day market summary for S&P 500 Telegram channel.

Today's Data:
- Open: ${open_price:,.2f}
- Close: ${close_price:,.2f}
- High: ${high:,.2f}
- Low: ${low:,.2f}
- Day Change: {day_change:+.2f}%
- Signal Result: {signal_result}
- P&L: {pnl:+.2f}%

Create a comprehensive but concise summary:
1. How the day went
2. Key market observations
3. Signal performance review
4. What to watch tomorrow
5. Encouraging note to traders

Use HTML formatting, emojis, and hashtags."""

    return call_groq_api(prompt, TRADING_SYSTEM_PROMPT, temperature=0.6)


# ============================================================================
# TEST FUNCTION
# ============================================================================

def test_groq_connection():
    """Test if Groq API is working"""

    print("Testing Groq API connection...")

    result = call_groq_api(
        "Say 'Groq AI is connected!' in a creative way with emojis.",
        max_tokens=50,
        temperature=0.9
    )

    if result:
        print(f"[OK] Groq API working!\n{result}")
        return True
    else:
        print("[FAILED] Could not connect to Groq API")
        return False


if __name__ == "__main__":
    print("="*50)
    print("Groq AI Integration Test")
    print("="*50)

    if GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        print("\n[!] Please set your Groq API key!")
        print("Get free key at: https://console.groq.com/keys")
        print("\nThen either:")
        print("1. Set environment variable: GROQ_API_KEY=your_key")
        print("2. Edit this file and replace YOUR_GROQ_API_KEY_HERE")
    else:
        test_groq_connection()

        print("\n" + "="*50)
        print("Testing AI Message Generation...")
        print("="*50)

        tip = generate_trading_tip()
        if tip:
            print("\n[Trading Tip Generated]")
            print(tip)
