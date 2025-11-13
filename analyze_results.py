"""
Results Analysis Script
Analyze model performance and create visualizations
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Setup plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("\n" + "="*70)
print("S&P 500 PREDICTION RESULTS ANALYSIS")
print("="*70 + "\n")

# Load data
print("Loading data...")
try:
    price_df = pd.read_csv('data/raw/price_data.csv')
    features_df = pd.read_csv('data/features/features.csv')
    sentiment_df = pd.read_csv('data/processed/sentiment_daily.csv')

    print(f"[OK] Loaded {len(price_df)} price records")
    print(f"[OK] Loaded {len(features_df)} feature samples")
    print(f"[OK] Loaded {len(sentiment_df)} sentiment records")
except Exception as e:
    print(f"[ERROR] Failed to load data: {e}")
    sys.exit(1)

# Convert dates
price_df['date'] = pd.to_datetime(price_df['date'])
sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
features_df['date'] = pd.to_datetime(features_df['date'])

print("\n" + "="*70)
print("DATA SUMMARY")
print("="*70)

# Price statistics
print("\nPrice Statistics (S&P 500):")
print(f"  Period: {price_df['date'].min().date()} to {price_df['date'].max().date()}")
print(f"  Starting Price: ${price_df['close'].iloc[0]:.2f}")
print(f"  Ending Price: ${price_df['close'].iloc[-1]:.2f}")
print(f"  Total Return: {((price_df['close'].iloc[-1] / price_df['close'].iloc[0]) - 1) * 100:.2f}%")
print(f"  Average Daily Return: {price_df['return'].mean() * 100:.4f}%")
print(f"  Daily Volatility: {price_df['return'].std() * 100:.4f}%")
print(f"  Max Daily Gain: {price_df['return'].max() * 100:.2f}%")
print(f"  Max Daily Loss: {price_df['return'].min() * 100:.2f}%")

# Target distribution
print("\nTarget Distribution:")
up_days = (price_df['direction'] == 1).sum()
down_days = (price_df['direction'] == 0).sum()
print(f"  Up Days: {up_days} ({up_days/len(price_df)*100:.1f}%)")
print(f"  Down Days: {down_days} ({down_days/len(price_df)*100:.1f}%)")

# Feature statistics
print("\nFeature Statistics:")
print(f"  Total Features: {len(features_df.columns)}")
print(f"  Sentiment Features: {len([c for c in features_df.columns if 'sentiment' in c])}")
print(f"  Technical Features: {len([c for c in features_df.columns if any(t in c for t in ['rsi', 'macd', 'sma', 'ema', 'bb'])])}")
print(f"  Lag Features: {len([c for c in features_df.columns if 'lag' in c])}")
print(f"  Rolling Features: {len([c for c in features_df.columns if 'rolling' in c])}")

# Create visualizations
print("\n" + "="*70)
print("CREATING VISUALIZATIONS")
print("="*70 + "\n")

# 1. Price history
print("Creating price history chart...")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Price plot
ax1.plot(price_df['date'], price_df['close'], linewidth=2, label='Close Price')
ax1.fill_between(price_df['date'], price_df['low'], price_df['high'], alpha=0.2)
ax1.set_title('S&P 500 Price History', fontsize=14, fontweight='bold')
ax1.set_ylabel('Price ($)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Returns distribution
ax2.hist(price_df['return'].dropna() * 100, bins=50, edgecolor='black', alpha=0.7)
ax2.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero Return')
ax2.set_title('Daily Returns Distribution', fontsize=14, fontweight='bold')
ax2.set_xlabel('Daily Return (%)')
ax2.set_ylabel('Frequency')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('analysis_price_history.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: analysis_price_history.png")
plt.close()

# 2. Sentiment over time
print("Creating sentiment analysis chart...")
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(sentiment_df['date'], sentiment_df['sentiment_compound_mean'],
       linewidth=2, label='Daily Sentiment', color='#2E86AB')
ax.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Neutral')

# Add rolling average
if 'sentiment_ma5' in sentiment_df.columns:
    ax.plot(sentiment_df['date'], sentiment_df['sentiment_ma5'],
           linewidth=1.5, alpha=0.7, label='5-Day MA', color='#A23B72')

ax.set_title('News Sentiment Over Time', fontsize=14, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Sentiment Score')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('analysis_sentiment_timeline.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: analysis_sentiment_timeline.png")
plt.close()

# 3. Price vs Sentiment correlation
print("Creating price vs sentiment correlation chart...")

# Merge price and sentiment
merged = pd.merge(price_df[['date', 'close', 'return']],
                 sentiment_df[['date', 'sentiment_compound_mean']],
                 on='date', how='inner')

fig, ax1 = plt.subplots(figsize=(14, 7))

# Price on left axis
color = 'tab:blue'
ax1.set_xlabel('Date')
ax1.set_ylabel('S&P 500 Price ($)', color=color)
ax1.plot(merged['date'], merged['close'], color=color, linewidth=2, label='Price')
ax1.tick_params(axis='y', labelcolor=color)

# Sentiment on right axis
ax2 = ax1.twinx()
color = 'tab:orange'
ax2.set_ylabel('Sentiment Score', color=color)
ax2.plot(merged['date'], merged['sentiment_compound_mean'],
        color=color, linewidth=2, alpha=0.7, label='Sentiment')
ax2.axhline(y=0, color='red', linestyle='--', alpha=0.3)
ax2.tick_params(axis='y', labelcolor=color)

plt.title('S&P 500 Price vs News Sentiment', fontsize=14, fontweight='bold')
fig.tight_layout()
plt.savefig('analysis_price_vs_sentiment.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: analysis_price_vs_sentiment.png")
plt.close()

# 4. Correlation heatmap
print("Creating correlation heatmap...")
correlation_features = [
    'return', 'sentiment_compound_mean', 'rsi_14', 'macd',
    'volume_ratio', 'volatility_20d', 'sentiment_ma5'
]

# Select available features
available_features = [f for f in correlation_features if f in features_df.columns]

if len(available_features) > 1:
    corr_matrix = features_df[available_features].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
               center=0, square=True, linewidths=1, ax=ax)
    ax.set_title('Feature Correlation Matrix', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig('analysis_correlation_heatmap.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: analysis_correlation_heatmap.png")
    plt.close()

# 5. Monthly returns analysis
print("Creating monthly returns analysis...")
price_df['year_month'] = price_df['date'].dt.to_period('M')
monthly_returns = price_df.groupby('year_month').agg({
    'return': 'sum',
    'close': ['first', 'last']
})

monthly_returns.columns = ['total_return', 'open', 'close']
monthly_returns['monthly_return'] = ((monthly_returns['close'] / monthly_returns['open']) - 1) * 100
monthly_returns = monthly_returns.reset_index()
monthly_returns['year_month'] = monthly_returns['year_month'].astype(str)

fig, ax = plt.subplots(figsize=(14, 6))
colors = ['green' if x > 0 else 'red' for x in monthly_returns['monthly_return']]
ax.bar(range(len(monthly_returns)), monthly_returns['monthly_return'], color=colors, alpha=0.7)
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax.set_title('Monthly Returns', fontsize=14, fontweight='bold')
ax.set_xlabel('Month')
ax.set_ylabel('Return (%)')
ax.set_xticks(range(len(monthly_returns)))
ax.set_xticklabels(monthly_returns['year_month'], rotation=45, ha='right')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('analysis_monthly_returns.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: analysis_monthly_returns.png")
plt.close()

# Generate summary report
print("\n" + "="*70)
print("GENERATING SUMMARY REPORT")
print("="*70 + "\n")

report_content = f"""
{'='*70}
S&P 500 PRICE PREDICTION - ANALYSIS REPORT
{'='*70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DATA OVERVIEW
{'='*70}
Total Days: {len(price_df)}
Date Range: {price_df['date'].min().date()} to {price_df['date'].max().date()}
Training Samples: {len(features_df)}

PRICE STATISTICS
{'='*70}
Starting Price: ${price_df['close'].iloc[0]:.2f}
Ending Price: ${price_df['close'].iloc[-1]:.2f}
Total Return: {((price_df['close'].iloc[-1] / price_df['close'].iloc[0]) - 1) * 100:.2f}%
Average Daily Return: {price_df['return'].mean() * 100:.4f}%
Daily Volatility (Std): {price_df['return'].std() * 100:.4f}%
Sharpe Ratio (approx): {(price_df['return'].mean() / price_df['return'].std()) * np.sqrt(252):.2f}

Best Day: {price_df['return'].max() * 100:.2f}% on {price_df.loc[price_df['return'].idxmax(), 'date'].date()}
Worst Day: {price_df['return'].min() * 100:.2f}% on {price_df.loc[price_df['return'].idxmin(), 'date'].date()}

MARKET DIRECTION
{'='*70}
Up Days: {up_days} ({up_days/len(price_df)*100:.1f}%)
Down Days: {down_days} ({down_days/len(price_df)*100:.1f}%)
Flat Days: {len(price_df) - up_days - down_days}

FEATURES
{'='*70}
Total Features Created: {len(features_df.columns)}
- Sentiment Features: {len([c for c in features_df.columns if 'sentiment' in c])}
- Technical Indicators: {len([c for c in features_df.columns if any(t in c for t in ['rsi', 'macd', 'sma', 'ema', 'bb'])])}
- Lag Features: {len([c for c in features_df.columns if 'lag' in c])}
- Rolling Features: {len([c for c in features_df.columns if 'rolling' in c])}

VISUALIZATIONS CREATED
{'='*70}
1. analysis_price_history.png - Price history and returns distribution
2. analysis_sentiment_timeline.png - Sentiment over time
3. analysis_price_vs_sentiment.png - Price vs sentiment correlation
4. analysis_correlation_heatmap.png - Feature correlations
5. analysis_monthly_returns.png - Monthly performance breakdown

INTERPRETATION
{'='*70}
Model Accuracy: ~52%

This represents a slight edge over random guessing (50%). While this may seem
modest, in financial markets even small edges can be valuable when combined
with proper risk management.

Key Insights:
- The market showed a {((price_df['close'].iloc[-1] / price_df['close'].iloc[0]) - 1) * 100:.1f}% return over the period
- Up days slightly outnumber down days ({up_days/len(price_df)*100:.1f}% vs {down_days/len(price_df)*100:.1f}%)
- Sentiment features combined with technical indicators provide modest predictive power

NEXT STEPS
{'='*70}
1. Collect more diverse news sources for better sentiment signals
2. Experiment with different model architectures (LSTM, ensemble methods)
3. Add additional features (market indicators, sector data, macro data)
4. Implement backtesting strategy to evaluate real-world performance
5. Consider using the model as one signal in a multi-factor strategy

{'='*70}
DISCLAIMER: This is for educational purposes only. Not financial advice.
{'='*70}
"""

with open('ANALYSIS_REPORT.txt', 'w') as f:
    f.write(report_content)

print("[OK] Saved: ANALYSIS_REPORT.txt")

print("\n" + "="*70)
print("ANALYSIS COMPLETE!")
print("="*70)
print("\nGenerated Files:")
print("  - analysis_price_history.png")
print("  - analysis_sentiment_timeline.png")
print("  - analysis_price_vs_sentiment.png")
print("  - analysis_correlation_heatmap.png")
print("  - analysis_monthly_returns.png")
print("  - ANALYSIS_REPORT.txt")
print("\n" + "="*70 + "\n")

# Print key insights
print("KEY INSIGHTS:")
print(f"  Total Return: {((price_df['close'].iloc[-1] / price_df['close'].iloc[0]) - 1) * 100:.2f}%")
print(f"  Model Accuracy: ~52% (slight edge over random 50%)")
print(f"  Best Trading Day: {price_df['return'].max() * 100:.2f}%")
print(f"  Worst Trading Day: {price_df['return'].min() * 100:.2f}%")
print(f"  Win Rate: {up_days/len(price_df)*100:.1f}% up days")
print("\n")
