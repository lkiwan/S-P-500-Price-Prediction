# -*- coding: utf-8 -*-
"""
S&P 500 Professional Image Generator
=====================================
Creates professional images for Telegram posts:
- Technical analysis charts
- Quote cards with Unsplash backgrounds
- News banners
- Market statistics graphics

Uses: matplotlib, Pillow, Unsplash API
"""

import os
import io
import requests
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
FONTS_DIR = os.path.join(BASE_DIR, 'fonts')

# Create directories if they don't exist
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

# Unsplash API (Free: 50 requests/hour)
# Get your free API key at: https://unsplash.com/developers
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")

# Try to load from config file
if not UNSPLASH_ACCESS_KEY:
    config_file = os.path.join(BASE_DIR, '.unsplash_key')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            UNSPLASH_ACCESS_KEY = f.read().strip()

UNSPLASH_AVAILABLE = bool(UNSPLASH_ACCESS_KEY)

# Color schemes
COLORS = {
    'bullish': '#00C853',      # Green
    'bearish': '#FF1744',      # Red
    'neutral': '#FFC107',      # Yellow
    'primary': '#1E88E5',      # Blue
    'secondary': '#7C4DFF',    # Purple
    'dark': '#1a1a2e',         # Dark blue
    'darker': '#16213e',       # Darker blue
    'accent': '#0f3460',       # Accent blue
    'gold': '#FFD700',         # Gold
    'white': '#FFFFFF',
    'light_gray': '#E0E0E0',
}

# Chart style
plt.style.use('dark_background')
plt.rcParams['figure.facecolor'] = COLORS['dark']
plt.rcParams['axes.facecolor'] = COLORS['darker']
plt.rcParams['axes.edgecolor'] = COLORS['light_gray']
plt.rcParams['axes.labelcolor'] = COLORS['white']
plt.rcParams['text.color'] = COLORS['white']
plt.rcParams['xtick.color'] = COLORS['light_gray']
plt.rcParams['ytick.color'] = COLORS['light_gray']
plt.rcParams['grid.color'] = '#333333'
plt.rcParams['font.size'] = 10


# ============================================================================
# UNSPLASH API
# ============================================================================

def get_unsplash_image(query="stock market trading", width=1200, height=630):
    """
    Fetch a professional image from Unsplash.
    Returns image bytes or None.
    """
    if not UNSPLASH_AVAILABLE:
        return None

    try:
        # Search for image
        url = "https://api.unsplash.com/photos/random"
        params = {
            "query": query,
            "orientation": "landscape",
            "client_id": UNSPLASH_ACCESS_KEY
        }

        response = requests.get(url, params=params, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            image_url = data['urls']['regular']

            # Download image
            img_response = requests.get(image_url, timeout=15, verify=False)
            if img_response.status_code == 200:
                # Resize image
                img = Image.open(io.BytesIO(img_response.content))
                img = img.convert('RGB')
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                return img
    except Exception as e:
        print(f"Unsplash error: {e}")

    return None


def get_cached_or_fetch_image(query, cache_name, width=1200, height=630):
    """Get image from cache or fetch from Unsplash."""
    cache_path = os.path.join(IMAGES_DIR, f"cache_{cache_name}.jpg")

    # Try to fetch new image
    img = get_unsplash_image(query, width, height)
    if img:
        img.save(cache_path, 'JPEG', quality=90)
        return img

    # Use cached image if exists
    if os.path.exists(cache_path):
        return Image.open(cache_path)

    # Create gradient fallback
    return create_gradient_background(width, height)


# ============================================================================
# BACKGROUND GENERATORS
# ============================================================================

def create_gradient_background(width=1200, height=630, colors=None):
    """Create a professional gradient background."""
    if colors is None:
        colors = [(26, 26, 46), (22, 33, 62), (15, 52, 96)]  # Dark blue gradient

    img = Image.new('RGB', (width, height))
    pixels = img.load()

    for y in range(height):
        # Calculate position in gradient
        pos = y / height

        if pos < 0.5:
            # Blend between first two colors
            t = pos * 2
            r = int(colors[0][0] * (1-t) + colors[1][0] * t)
            g = int(colors[0][1] * (1-t) + colors[1][1] * t)
            b = int(colors[0][2] * (1-t) + colors[1][2] * t)
        else:
            # Blend between second and third colors
            t = (pos - 0.5) * 2
            r = int(colors[1][0] * (1-t) + colors[2][0] * t)
            g = int(colors[1][1] * (1-t) + colors[2][1] * t)
            b = int(colors[1][2] * (1-t) + colors[2][2] * t)

        for x in range(width):
            pixels[x, y] = (r, g, b)

    return img


def create_market_background(width=1200, height=630, bullish=True):
    """Create market-themed background with gradient."""
    if bullish:
        colors = [(10, 40, 30), (20, 60, 40), (0, 100, 53)]  # Green gradient
    else:
        colors = [(50, 20, 20), (80, 30, 30), (120, 20, 30)]  # Red gradient

    return create_gradient_background(width, height, colors)


# ============================================================================
# TECHNICAL ANALYSIS CHART
# ============================================================================

def create_technical_chart(df, save_path=None):
    """
    Create a professional technical analysis chart with price and indicators.

    Args:
        df: DataFrame with Date, Open, High, Low, Close, Volume columns
        save_path: Optional path to save the image

    Returns:
        BytesIO object with the chart image
    """
    if df is None or df.empty:
        return None

    # Ensure proper column names
    df = df.copy()
    df.columns = [c.capitalize() if c.lower() in ['open', 'high', 'low', 'close', 'volume', 'date'] else c for c in df.columns]

    if 'Date' not in df.columns:
        if 'date' in df.columns:
            df.rename(columns={'date': 'Date'}, inplace=True)
        else:
            return None

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').tail(60)  # Last 60 days

    # Calculate indicators
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_12'] = df['Close'].ewm(span=12).mean()
    df['EMA_26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()

    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Create figure with subplots
    fig = plt.figure(figsize=(14, 10), facecolor=COLORS['dark'])

    # Grid spec for layout
    gs = fig.add_gridspec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.1)

    # Price chart
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(COLORS['darker'])

    # Candlestick-like bars
    for i in range(len(df)):
        row = df.iloc[i]
        color = COLORS['bullish'] if row['Close'] >= row['Open'] else COLORS['bearish']
        ax1.plot([row['Date'], row['Date']], [row['Low'], row['High']], color=color, linewidth=1)
        ax1.plot([row['Date'], row['Date']], [row['Open'], row['Close']], color=color, linewidth=4)

    # Moving averages
    ax1.plot(df['Date'], df['SMA_20'], color='#FFD700', linewidth=1.5, label='SMA 20', alpha=0.8)
    ax1.plot(df['Date'], df['SMA_50'], color='#FF6B6B', linewidth=1.5, label='SMA 50', alpha=0.8)

    ax1.set_ylabel('Price ($)', fontsize=11, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticklabels([])

    # Title
    current_price = df['Close'].iloc[-1]
    price_change = ((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100
    trend = "BULLISH" if df['Close'].iloc[-1] > df['SMA_20'].iloc[-1] else "BEARISH"
    trend_color = COLORS['bullish'] if trend == "BULLISH" else COLORS['bearish']

    ax1.set_title(f"S&P 500 Technical Analysis | ${current_price:,.2f} ({price_change:+.2f}%) | {trend}",
                  fontsize=14, fontweight='bold', color=COLORS['white'], pad=15)

    # Volume chart
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.set_facecolor(COLORS['darker'])

    colors = [COLORS['bullish'] if df['Close'].iloc[i] >= df['Open'].iloc[i] else COLORS['bearish']
              for i in range(len(df))]
    ax2.bar(df['Date'], df['Volume'], color=colors, alpha=0.7, width=0.8)
    ax2.set_ylabel('Volume', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticklabels([])

    # MACD
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax3.set_facecolor(COLORS['darker'])
    ax3.plot(df['Date'], df['MACD'], color=COLORS['primary'], linewidth=1.5, label='MACD')
    ax3.plot(df['Date'], df['Signal'], color='#FF6B6B', linewidth=1.5, label='Signal')
    ax3.bar(df['Date'], df['MACD'] - df['Signal'], color=[COLORS['bullish'] if v > 0 else COLORS['bearish']
            for v in (df['MACD'] - df['Signal'])], alpha=0.5, width=0.8)
    ax3.axhline(y=0, color=COLORS['light_gray'], linestyle='--', linewidth=0.5)
    ax3.set_ylabel('MACD', fontsize=10)
    ax3.legend(loc='upper left', fontsize=8)
    ax3.grid(True, alpha=0.3)
    ax3.set_xticklabels([])

    # RSI
    ax4 = fig.add_subplot(gs[3], sharex=ax1)
    ax4.set_facecolor(COLORS['darker'])
    ax4.plot(df['Date'], df['RSI'], color=COLORS['secondary'], linewidth=1.5)
    ax4.axhline(y=70, color=COLORS['bearish'], linestyle='--', linewidth=1, alpha=0.7)
    ax4.axhline(y=30, color=COLORS['bullish'], linestyle='--', linewidth=1, alpha=0.7)
    ax4.axhline(y=50, color=COLORS['light_gray'], linestyle='--', linewidth=0.5, alpha=0.5)
    ax4.fill_between(df['Date'], 30, df['RSI'].clip(upper=30), color=COLORS['bullish'], alpha=0.3)
    ax4.fill_between(df['Date'], 70, df['RSI'].clip(lower=70), color=COLORS['bearish'], alpha=0.3)
    ax4.set_ylabel('RSI', fontsize=10)
    ax4.set_ylim(0, 100)
    ax4.grid(True, alpha=0.3)

    # Format x-axis
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax4.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.xticks(rotation=45)

    # Add watermark
    fig.text(0.99, 0.01, '@lkiwanSP500', fontsize=10, color=COLORS['light_gray'],
             ha='right', va='bottom', alpha=0.7)

    # Add date
    fig.text(0.01, 0.01, datetime.now().strftime('%Y-%m-%d %H:%M ET'),
             fontsize=9, color=COLORS['light_gray'], ha='left', va='bottom', alpha=0.7)

    plt.tight_layout()

    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=COLORS['dark'], edgecolor='none')
    buf.seek(0)
    plt.close(fig)

    if save_path:
        with open(save_path, 'wb') as f:
            f.write(buf.getvalue())
        buf.seek(0)

    return buf


# ============================================================================
# QUOTE CARD GENERATOR
# ============================================================================

def create_quote_card(quote, author, save_path=None):
    """
    Create a professional quote card with background image.

    Args:
        quote: The quote text
        author: The author name
        save_path: Optional path to save the image

    Returns:
        BytesIO object with the quote card image
    """
    width, height = 1200, 630

    # Try to get Unsplash background
    bg = get_cached_or_fetch_image(
        "stock market dark abstract finance",
        "quote_bg",
        width, height
    )

    # Apply dark overlay for text readability
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 180))
    bg = bg.convert('RGBA')
    bg = Image.alpha_composite(bg, overlay)
    bg = bg.convert('RGB')

    # Apply slight blur
    bg = bg.filter(ImageFilter.GaussianBlur(radius=2))

    draw = ImageDraw.Draw(bg)

    # Try to load fonts (with fallbacks)
    try:
        # Try system fonts
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

        quote_font = None
        author_font = None

        for fp in font_paths:
            if os.path.exists(fp):
                quote_font = ImageFont.truetype(fp, 36)
                author_font = ImageFont.truetype(fp, 28)
                break

        if quote_font is None:
            quote_font = ImageFont.load_default()
            author_font = ImageFont.load_default()

    except Exception:
        quote_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Add decorative elements
    # Top gold line
    draw.rectangle([(100, 80), (width-100, 85)], fill=COLORS['gold'])

    # Quote icon
    draw.text((width//2 - 30, 100), '"', font=quote_font, fill=COLORS['gold'])

    # Wrap quote text
    max_width = width - 200
    words = quote.split()
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=quote_font)
        if bbox[2] - bbox[0] > max_width:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(test_line)
                current_line = []

    if current_line:
        lines.append(' '.join(current_line))

    # Calculate text position (centered)
    line_height = 50
    total_height = len(lines) * line_height
    start_y = (height - total_height) // 2 - 30

    # Draw quote lines
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=quote_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = start_y + i * line_height

        # Shadow
        draw.text((x+2, y+2), line, font=quote_font, fill=(0, 0, 0, 128))
        # Text
        draw.text((x, y), line, font=quote_font, fill=COLORS['white'])

    # Author
    author_text = f"— {author}"
    bbox = draw.textbbox((0, 0), author_text, font=author_font)
    author_width = bbox[2] - bbox[0]
    author_x = (width - author_width) // 2
    author_y = start_y + len(lines) * line_height + 40

    draw.text((author_x+2, author_y+2), author_text, font=author_font, fill=(0, 0, 0, 128))
    draw.text((author_x, author_y), author_text, font=author_font, fill=COLORS['gold'])

    # Bottom gold line
    draw.rectangle([(100, height-80), (width-100, height-75)], fill=COLORS['gold'])

    # Channel watermark
    try:
        watermark_font = ImageFont.truetype(font_paths[0], 18) if font_paths else ImageFont.load_default()
    except:
        watermark_font = ImageFont.load_default()

    draw.text((width-150, height-40), "@lkiwanSP500", font=watermark_font, fill=COLORS['light_gray'])

    # Save to bytes
    buf = io.BytesIO()
    bg.save(buf, format='PNG', quality=95)
    buf.seek(0)

    if save_path:
        bg.save(save_path, 'PNG', quality=95)

    return buf


# ============================================================================
# NEWS BANNER GENERATOR
# ============================================================================

def create_news_banner(headline=None, save_path=None):
    """
    Create a professional news banner image.

    Args:
        headline: Optional headline text
        save_path: Optional path to save the image

    Returns:
        BytesIO object with the banner image
    """
    width, height = 1200, 630

    # Get news-themed background
    bg = get_cached_or_fetch_image(
        "newspaper business finance stock market",
        "news_bg",
        width, height
    )

    # Dark overlay
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 160))
    bg = bg.convert('RGBA')
    bg = Image.alpha_composite(bg, overlay)
    bg = bg.convert('RGB')

    draw = ImageDraw.Draw(bg)

    # Load fonts
    try:
        font_paths = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]

        title_font = None
        for fp in font_paths:
            if os.path.exists(fp):
                title_font = ImageFont.truetype(fp, 60)
                subtitle_font = ImageFont.truetype(fp, 30)
                break

        if title_font is None:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Breaking news banner
    draw.rectangle([(0, 50), (width, 130)], fill='#B71C1C')
    draw.text((50, 65), "MARKET NEWS", font=title_font, fill=COLORS['white'])

    # S&P 500 label
    draw.rectangle([(width-250, 60), (width-30, 120)], fill=COLORS['gold'])
    draw.text((width-230, 70), "S&P 500", font=subtitle_font, fill=COLORS['dark'])

    # Date and time
    date_str = datetime.now().strftime("%B %d, %Y | %H:%M ET")
    draw.text((50, 150), date_str, font=subtitle_font, fill=COLORS['light_gray'])

    # Headline if provided
    if headline:
        # Wrap headline
        max_width = width - 100
        words = headline.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=subtitle_font)
            if bbox[2] - bbox[0] > max_width:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        y = 250
        for line in lines[:3]:  # Max 3 lines
            draw.text((50, y), line, font=subtitle_font, fill=COLORS['white'])
            y += 45

    # Decorative elements
    draw.rectangle([(0, height-60), (width, height)], fill=COLORS['dark'])
    draw.text((50, height-45), "@lkiwanSP500 | Daily Market Updates", font=subtitle_font, fill=COLORS['light_gray'])

    # Save to bytes
    buf = io.BytesIO()
    bg.save(buf, format='PNG', quality=95)
    buf.seek(0)

    if save_path:
        bg.save(save_path, 'PNG', quality=95)

    return buf


# ============================================================================
# MARKET STATS GRAPHIC
# ============================================================================

def create_stats_graphic(stats_data, save_path=None):
    """
    Create a professional market statistics graphic.

    Args:
        stats_data: Dict with keys like 'price', 'day_change', 'week_change', 'month_change'
        save_path: Optional path to save the image

    Returns:
        BytesIO object with the graphic
    """
    width, height = 1200, 630

    fig, ax = plt.subplots(figsize=(12, 6.3), facecolor=COLORS['dark'])
    ax.set_facecolor(COLORS['darker'])

    # Remove axes
    ax.axis('off')

    # Title
    price = stats_data.get('price', 0)
    day_change = stats_data.get('day_change', 0)
    trend_color = COLORS['bullish'] if day_change >= 0 else COLORS['bearish']

    fig.text(0.5, 0.92, 'S&P 500 MARKET STATISTICS', fontsize=28, fontweight='bold',
             ha='center', color=COLORS['white'])

    fig.text(0.5, 0.82, f'${price:,.2f}', fontsize=48, fontweight='bold',
             ha='center', color=COLORS['white'])

    fig.text(0.5, 0.72, f'{day_change:+.2f}% Today', fontsize=24,
             ha='center', color=trend_color)

    # Performance bars
    metrics = [
        ('Week', stats_data.get('week_change', 0)),
        ('Month', stats_data.get('month_change', 0)),
        ('YTD', stats_data.get('ytd_change', 0)),
    ]

    bar_width = 0.2
    positions = [0.25, 0.5, 0.75]

    for i, (label, value) in enumerate(metrics):
        color = COLORS['bullish'] if value >= 0 else COLORS['bearish']

        # Bar background
        ax2 = fig.add_axes([positions[i]-0.08, 0.25, 0.16, 0.35])
        ax2.set_facecolor(COLORS['accent'])
        ax2.axis('off')

        # Label
        fig.text(positions[i], 0.18, label, fontsize=18, ha='center', color=COLORS['light_gray'])

        # Value
        fig.text(positions[i], 0.45, f'{value:+.2f}%', fontsize=24, fontweight='bold',
                ha='center', color=color)

        # Arrow
        arrow = '↑' if value >= 0 else '↓'
        fig.text(positions[i], 0.35, arrow, fontsize=36, ha='center', color=color)

    # Footer
    fig.text(0.5, 0.05, f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M ET')} | @lkiwanSP500",
             fontsize=12, ha='center', color=COLORS['light_gray'])

    # Decorative line
    line = plt.Line2D([0.1, 0.9], [0.65, 0.65], color=COLORS['gold'], linewidth=2)
    fig.add_artist(line)

    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=COLORS['dark'], edgecolor='none')
    buf.seek(0)
    plt.close(fig)

    if save_path:
        with open(save_path, 'wb') as f:
            f.write(buf.getvalue())
        buf.seek(0)

    return buf


# ============================================================================
# TRADING TIP CARD
# ============================================================================

def create_tip_card(tip_text, tip_number=None, save_path=None):
    """
    Create a professional trading tip card.

    Args:
        tip_text: The tip text
        tip_number: Optional tip number
        save_path: Optional path to save the image

    Returns:
        BytesIO object with the tip card image
    """
    width, height = 1200, 630

    # Gradient background
    bg = create_gradient_background(width, height,
        colors=[(20, 30, 48), (36, 59, 85), (52, 89, 122)])

    draw = ImageDraw.Draw(bg)

    # Load fonts
    try:
        font_paths = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]

        for fp in font_paths:
            if os.path.exists(fp):
                title_font = ImageFont.truetype(fp, 42)
                tip_font = ImageFont.truetype(fp, 32)
                small_font = ImageFont.truetype(fp, 20)
                break
        else:
            title_font = ImageFont.load_default()
            tip_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    except:
        title_font = ImageFont.load_default()
        tip_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Decorative top bar
    draw.rectangle([(0, 0), (width, 8)], fill=COLORS['gold'])

    # Light bulb emoji area
    draw.ellipse([(width//2-50, 40), (width//2+50, 140)], fill=COLORS['gold'])
    draw.text((width//2-25, 60), "💡", font=title_font, fill=COLORS['dark'])

    # Title
    title = f"TRADING TIP #{tip_number}" if tip_number else "TRADING TIP"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]
    draw.text(((width-title_width)//2, 160), title, font=title_font, fill=COLORS['gold'])

    # Wrap tip text
    max_width = width - 150
    words = tip_text.split()
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=tip_font)
        if bbox[2] - bbox[0] > max_width:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    # Draw tip text
    y = 250
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=tip_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), line, font=tip_font, fill=COLORS['white'])
        y += 50

    # Bottom decorative bar
    draw.rectangle([(0, height-50), (width, height)], fill=COLORS['accent'])
    draw.text((50, height-40), "@lkiwanSP500", font=small_font, fill=COLORS['light_gray'])
    draw.text((width-200, height-40), "#TradingTips", font=small_font, fill=COLORS['gold'])

    # Save to bytes
    buf = io.BytesIO()
    bg.save(buf, format='PNG', quality=95)
    buf.seek(0)

    if save_path:
        bg.save(save_path, 'PNG', quality=95)

    return buf


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("S&P 500 Image Generator Test")
    print("=" * 60)

    print(f"\nUnsplash API: {'Available' if UNSPLASH_AVAILABLE else 'Not configured'}")
    print(f"Images directory: {IMAGES_DIR}")

    # Test gradient background
    print("\n1. Creating gradient background...")
    bg = create_gradient_background()
    bg.save(os.path.join(IMAGES_DIR, "test_gradient.png"))
    print("   Saved: test_gradient.png")

    # Test quote card
    print("\n2. Creating quote card...")
    quote_buf = create_quote_card(
        "Be fearful when others are greedy and greedy when others are fearful.",
        "Warren Buffett",
        os.path.join(IMAGES_DIR, "test_quote.png")
    )
    print("   Saved: test_quote.png")

    # Test news banner
    print("\n3. Creating news banner...")
    news_buf = create_news_banner(
        "S&P 500 Reaches New All-Time High Amid Strong Earnings",
        os.path.join(IMAGES_DIR, "test_news.png")
    )
    print("   Saved: test_news.png")

    # Test stats graphic
    print("\n4. Creating stats graphic...")
    stats_buf = create_stats_graphic({
        'price': 5890.23,
        'day_change': 0.45,
        'week_change': 1.23,
        'month_change': 2.87,
        'ytd_change': 8.45
    }, os.path.join(IMAGES_DIR, "test_stats.png"))
    print("   Saved: test_stats.png")

    # Test tip card
    print("\n5. Creating tip card...")
    tip_buf = create_tip_card(
        "Never risk more than 2% of your portfolio on a single trade. This simple rule can save you from devastating losses.",
        tip_number=42,
        save_path=os.path.join(IMAGES_DIR, "test_tip.png")
    )
    print("   Saved: test_tip.png")

    # Test technical chart
    print("\n6. Creating technical chart...")
    try:
        price_file = os.path.join(BASE_DIR, 'data', 'raw', 'price_data.csv')
        if os.path.exists(price_file):
            df = pd.read_csv(price_file)
            chart_buf = create_technical_chart(df, os.path.join(IMAGES_DIR, "test_chart.png"))
            print("   Saved: test_chart.png")
        else:
            print("   Skipped: price_data.csv not found")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "=" * 60)
    print("All test images saved to:", IMAGES_DIR)
    print("=" * 60)
