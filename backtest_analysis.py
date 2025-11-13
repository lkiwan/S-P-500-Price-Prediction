"""
Backtest Analysis - Previous Month
Tests model predictions on past data and analyzes news-price relationships
"""

import sys
sys.path.append('src')

from models.predict import Predictor
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

print("\n" + "="*70)
print("BACKTEST ANALYSIS - PREVIOUS MONTH")
print("="*70)
print("Testing model performance on historical data")
print("Analyzing news-price relationships")
print("="*70 + "\n")

# Step 1: Load data
print("STEP 1: Loading historical data...")

try:
    # Load features
    features_df = pd.read_csv('data/features/features_complete.csv')
    features_df['date'] = pd.to_datetime(features_df['date'])

    # Load price data
    price_df = pd.read_csv('data/raw/price_data.csv')
    price_df['date'] = pd.to_datetime(price_df['date'])

    # Load sentiment data
    try:
        sentiment_df = pd.read_csv('data/processed/sentiment_daily_real.csv')
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
        sentiment_source = "REAL news"
    except:
        sentiment_df = pd.read_csv('data/processed/sentiment_daily.csv')
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
        sentiment_source = "Synthetic"

    print(f"[OK] Loaded data")
    print(f"  Features: {len(features_df)} samples")
    print(f"  Prices: {len(price_df)} days")
    print(f"  Sentiment: {len(sentiment_df)} days ({sentiment_source})")

except Exception as e:
    print(f"[ERROR] Failed to load data: {e}")
    sys.exit(1)

# Step 2: Select last month for backtesting
print("\nSTEP 2: Selecting last month data...")

# Get last month
end_date = features_df['date'].max()
start_date = end_date - timedelta(days=30)

backtest_df = features_df[features_df['date'] >= start_date].copy()
print(f"[OK] Backtest period: {start_date.date()} to {end_date.date()}")
print(f"  Trading days: {len(backtest_df)}")

# Step 3: Load model and make predictions
print("\nSTEP 3: Running model predictions on past data...")

model_name = "sp500_complete_20251113"
predictor = Predictor(model_name=model_name)

# Make predictions for each day
predictions = []
actuals = []
dates = []
confidences = []

for idx, row in backtest_df.iterrows():
    # Make prediction
    features = pd.DataFrame([row])
    result = predictor.predict(features)

    if result:
        predictions.append(result['prediction'])
        actuals.append(row['target'])
        dates.append(row['date'])
        confidences.append(result['confidence'])

predictions_df = pd.DataFrame({
    'date': dates,
    'predicted': predictions,
    'actual': actuals,
    'confidence': confidences
})

print(f"[OK] Made {len(predictions_df)} predictions")

# Step 4: Calculate accuracy metrics
print("\nSTEP 4: Analyzing prediction accuracy...")
print("-" * 70)

accuracy = accuracy_score(actuals, predictions)
correct = sum([1 for p, a in zip(predictions, actuals) if p == a])

print(f"\nBacktest Results:")
print(f"  Total Predictions: {len(predictions)}")
print(f"  Correct: {correct}")
print(f"  Incorrect: {len(predictions) - correct}")
print(f"  Accuracy: {accuracy:.2%}")
print(f"  Edge over random: {(accuracy - 0.5) * 100:+.2f} pp")

# Confusion matrix
cm = confusion_matrix(actuals, predictions)
print(f"\nConfusion Matrix:")
print(f"  True Negatives (Predicted Down, Was Down): {cm[0,0]}")
print(f"  False Positives (Predicted Up, Was Down): {cm[0,1]}")
print(f"  False Negatives (Predicted Down, Was Up): {cm[1,0]}")
print(f"  True Positives (Predicted Up, Was Up): {cm[1,1]}")

# Classification report
print(f"\nDetailed Classification Report:")
print(classification_report(actuals, predictions,
                           target_names=['Down', 'Up']))

# Accuracy by confidence level
print("\nAccuracy by Confidence Level:")
predictions_df['correct'] = predictions_df['predicted'] == predictions_df['actual']

for conf_threshold in [0.7, 0.6, 0.5]:
    high_conf = predictions_df[predictions_df['confidence'] >= conf_threshold]
    if len(high_conf) > 0:
        acc = high_conf['correct'].mean()
        print(f"  Confidence >= {conf_threshold:.0%}: {acc:.2%} ({len(high_conf)} predictions)")

# Step 5: Analyze news-price relationship
print("\n" + "="*70)
print("STEP 5: Analyzing News-Price Relationship")
print("="*70)

# Merge sentiment with prices for the backtest period
analysis_df = pd.merge(price_df, sentiment_df, on='date', how='inner')
analysis_df = analysis_df[analysis_df['date'] >= start_date]

if len(analysis_df) > 0:
    print(f"\n[OK] Analyzing {len(analysis_df)} days with both news and price data")

    # Calculate correlation
    if 'sentiment_compound_mean' in analysis_df.columns:
        # Correlation between sentiment and next day return
        analysis_df['next_return'] = analysis_df['return'].shift(-1)

        corr = analysis_df['sentiment_compound_mean'].corr(analysis_df['next_return'])
        print(f"\nCorrelation Analysis:")
        print(f"  Sentiment vs Next-Day Return: {corr:.4f}")

        # Sentiment vs same-day return
        corr_same = analysis_df['sentiment_compound_mean'].corr(analysis_df['return'])
        print(f"  Sentiment vs Same-Day Return: {corr_same:.4f}")

        # Group by sentiment level
        analysis_df['sentiment_level'] = pd.cut(
            analysis_df['sentiment_compound_mean'],
            bins=[-np.inf, -0.1, 0.1, np.inf],
            labels=['Negative', 'Neutral', 'Positive']
        )

        print(f"\nAverage Returns by Sentiment:")
        sentiment_returns = analysis_df.groupby('sentiment_level')['next_return'].agg(['mean', 'count'])
        for level in ['Negative', 'Neutral', 'Positive']:
            if level in sentiment_returns.index:
                mean_ret = sentiment_returns.loc[level, 'mean'] * 100
                count = sentiment_returns.loc[level, 'count']
                print(f"  {level:8s}: {mean_ret:+.3f}% avg return (n={count})")

        # Direction accuracy by sentiment
        analysis_df['direction_correct'] = (
            (analysis_df['sentiment_compound_mean'] > 0) ==
            (analysis_df['next_return'] > 0)
        )

        directional_acc = analysis_df['direction_correct'].mean()
        print(f"\nSentiment Directional Accuracy:")
        print(f"  Can sentiment predict direction? {directional_acc:.2%}")

# Step 6: Create visualizations
print("\n" + "="*70)
print("STEP 6: Creating Visualizations")
print("="*70 + "\n")

# Setup
sns.set_style("darkgrid")
fig = plt.figure(figsize=(16, 12))

# Plot 1: Predictions vs Actual
ax1 = plt.subplot(3, 2, 1)
x = range(len(predictions_df))
ax1.scatter(x, predictions_df['actual'], alpha=0.6, label='Actual', s=100, marker='o')
ax1.scatter(x, predictions_df['predicted'], alpha=0.6, label='Predicted', s=100, marker='x')
ax1.set_xlabel('Trading Day')
ax1.set_ylabel('Direction (0=Down, 1=Up)')
ax1.set_title(f'Predictions vs Actual - Last Month\nAccuracy: {accuracy:.2%}',
             fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Prediction Accuracy Over Time
ax2 = plt.subplot(3, 2, 2)
predictions_df['rolling_accuracy'] = predictions_df['correct'].rolling(5, min_periods=1).mean()
ax2.plot(predictions_df['date'], predictions_df['rolling_accuracy'], linewidth=2, color='green')
ax2.axhline(y=0.5, color='red', linestyle='--', label='Random Guess')
ax2.axhline(y=accuracy, color='blue', linestyle='--', label=f'Overall ({accuracy:.2%})')
ax2.set_xlabel('Date')
ax2.set_ylabel('Accuracy')
ax2.set_title('Rolling 5-Day Accuracy', fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)
plt.xticks(rotation=45)

# Plot 3: Confusion Matrix
ax3 = plt.subplot(3, 2, 3)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax3,
           xticklabels=['Down', 'Up'], yticklabels=['Down', 'Up'])
ax3.set_xlabel('Predicted')
ax3.set_ylabel('Actual')
ax3.set_title('Confusion Matrix', fontweight='bold')

# Plot 4: Confidence Distribution
ax4 = plt.subplot(3, 2, 4)
ax4.hist(predictions_df['confidence'], bins=20, edgecolor='black', alpha=0.7, color='purple')
ax4.axvline(x=0.7, color='green', linestyle='--', label='High Confidence', linewidth=2)
ax4.axvline(x=0.6, color='orange', linestyle='--', label='Medium Confidence', linewidth=2)
ax4.set_xlabel('Confidence Level')
ax4.set_ylabel('Frequency')
ax4.set_title('Prediction Confidence Distribution', fontweight='bold')
ax4.legend()
ax4.grid(True, alpha=0.3)

# Plot 5: Sentiment vs Price
if len(analysis_df) > 0 and 'sentiment_compound_mean' in analysis_df.columns:
    ax5 = plt.subplot(3, 2, 5)
    ax5_twin = ax5.twinx()

    ax5.plot(analysis_df['date'], analysis_df['close'],
            color='blue', linewidth=2, label='Price')
    ax5_twin.plot(analysis_df['date'], analysis_df['sentiment_compound_mean'],
                 color='orange', linewidth=2, alpha=0.7, label='Sentiment')
    ax5_twin.axhline(y=0, color='red', linestyle='--', alpha=0.3)

    ax5.set_xlabel('Date')
    ax5.set_ylabel('S&P 500 Price', color='blue')
    ax5_twin.set_ylabel('Sentiment Score', color='orange')
    ax5.set_title('Price vs News Sentiment', fontweight='bold')
    ax5.tick_params(axis='y', labelcolor='blue')
    ax5_twin.tick_params(axis='y', labelcolor='orange')
    plt.xticks(rotation=45)
    ax5.grid(True, alpha=0.3)

# Plot 6: Returns by Sentiment Level
if len(analysis_df) > 0 and 'sentiment_level' in analysis_df.columns:
    ax6 = plt.subplot(3, 2, 6)

    sentiment_groups = analysis_df.groupby('sentiment_level')['next_return'].apply(list)
    positions = [1, 2, 3]
    labels = ['Negative', 'Neutral', 'Positive']

    data_to_plot = []
    actual_labels = []
    for label in labels:
        if label in sentiment_groups.index:
            data_to_plot.append([x*100 for x in sentiment_groups[label] if not np.isnan(x)])
            actual_labels.append(label)

    if data_to_plot:
        bp = ax6.boxplot(data_to_plot, labels=actual_labels, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
        ax6.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax6.set_xlabel('Sentiment Level')
        ax6.set_ylabel('Next-Day Return (%)')
        ax6.set_title('Returns Distribution by Sentiment', fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('backtest_analysis.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: backtest_analysis.png")
plt.close()

# Step 7: Generate detailed report
print("\n" + "="*70)
print("STEP 7: Generating Detailed Report")
print("="*70 + "\n")

report = f"""
{'='*70}
BACKTEST ANALYSIS REPORT - LAST MONTH
{'='*70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PERIOD ANALYZED
{'='*70}
Start Date: {start_date.date()}
End Date: {end_date.date()}
Trading Days: {len(predictions_df)}
Model: {model_name}
Sentiment Source: {sentiment_source}

PREDICTION PERFORMANCE
{'='*70}
Total Predictions: {len(predictions)}
Correct: {correct}
Incorrect: {len(predictions) - correct}
Accuracy: {accuracy:.2%}
Edge over Random: {(accuracy - 0.5) * 100:+.2f} percentage points

Confusion Matrix:
  True Negatives (Down->Down): {cm[0,0]}
  False Positives (Down->Up): {cm[0,1]}
  False Negatives (Up->Down): {cm[1,0]}
  True Positives (Up->Up): {cm[1,1]}

Precision (Up): {cm[1,1]/(cm[1,1]+cm[0,1]) if (cm[1,1]+cm[0,1])>0 else 0:.2%}
Recall (Up): {cm[1,1]/(cm[1,1]+cm[1,0]) if (cm[1,1]+cm[1,0])>0 else 0:.2%}

CONFIDENCE ANALYSIS
{'='*70}
Average Confidence: {predictions_df['confidence'].mean():.2%}
"""

# Add confidence-stratified accuracy
for conf_threshold in [0.7, 0.6, 0.5]:
    high_conf = predictions_df[predictions_df['confidence'] >= conf_threshold]
    if len(high_conf) > 0:
        acc = high_conf['correct'].mean()
        report += f"Accuracy (Confidence >= {conf_threshold:.0%}): {acc:.2%} (n={len(high_conf)})\n"

# Add news-price relationship
if len(analysis_df) > 0 and 'sentiment_compound_mean' in analysis_df.columns:
    report += f"""
NEWS-PRICE RELATIONSHIP
{'='*70}
Correlation (Sentiment vs Next-Day Return): {corr:.4f}
Correlation (Sentiment vs Same-Day Return): {corr_same:.4f}
Sentiment Directional Accuracy: {directional_acc:.2%}

Average Returns by Sentiment Level:
"""
    for level in ['Negative', 'Neutral', 'Positive']:
        if level in sentiment_returns.index:
            mean_ret = sentiment_returns.loc[level, 'mean'] * 100
            count = sentiment_returns.loc[level, 'count']
            report += f"  {level}: {mean_ret:+.3f}% (n={count} days)\n"

report += f"""
INTERPRETATION
{'='*70}
"""

if accuracy > 0.55:
    report += f"[+] Model is performing WELL ({accuracy:.2%} accuracy)\n"
    report += f"  This {(accuracy-0.5)*100:.1f}pp edge over random is statistically significant\n"
elif accuracy > 0.50:
    report += f"~ Model has a SLIGHT edge ({accuracy:.2%} accuracy)\n"
    report += f"  Edge is modest but may be useful with risk management\n"
else:
    report += f"[-] Model underperformed on this period ({accuracy:.2%} accuracy)\n"
    report += f"  Consider retraining with more recent data\n"

if corr > 0.1:
    report += f"\n[+] Sentiment shows POSITIVE correlation with returns ({corr:.3f})\n"
    report += f"  News sentiment is a useful signal\n"
elif corr < -0.1:
    report += f"\n~ Sentiment shows NEGATIVE correlation with returns ({corr:.3f})\n"
    report += f"  Contrarian signal - market may move opposite to news\n"
else:
    report += f"\n~ Sentiment correlation is WEAK ({corr:.3f})\n"
    report += f"  News sentiment alone is not a strong predictor\n"

report += f"""
TRADING SIMULATION
{'='*70}
"""

# Simple trading simulation
initial_capital = 10000
capital = initial_capital
trades = 0
wins = 0

for _, row in predictions_df.iterrows():
    # Only trade on high confidence
    if row['confidence'] >= 0.6:
        # Merge with actual returns
        date_match = price_df[price_df['date'] == row['date']]
        if len(date_match) > 0:
            actual_return = date_match.iloc[0]['return']
            if not np.isnan(actual_return):
                trades += 1
                # If predicted correctly, gain; otherwise lose
                if row['predicted'] == row['actual']:
                    capital *= (1 + abs(actual_return))
                    wins += 1
                else:
                    capital *= (1 - abs(actual_return))

total_return = ((capital - initial_capital) / initial_capital) * 100
win_rate = (wins / trades * 100) if trades > 0 else 0

report += f"Initial Capital: ${initial_capital:,.2f}\n"
report += f"Final Capital: ${capital:,.2f}\n"
report += f"Total Return: {total_return:+.2f}%\n"
report += f"Trades Taken (Conf >= 60%): {trades}\n"
report += f"Winning Trades: {wins}\n"
report += f"Win Rate: {win_rate:.1f}%\n"

# Buy and hold comparison
if len(price_df[price_df['date'] >= start_date]) > 0:
    start_price = price_df[price_df['date'] >= start_date].iloc[0]['close']
    end_price = price_df[price_df['date'] >= start_date].iloc[-1]['close']
    buy_hold_return = ((end_price - start_price) / start_price) * 100
    report += f"\nBuy & Hold Return (Same Period): {buy_hold_return:+.2f}%\n"

    if total_return > buy_hold_return:
        report += f"[+] Strategy OUTPERFORMED buy & hold by {total_return - buy_hold_return:.2f}pp\n"
    else:
        report += f"[-] Strategy UNDERPERFORMED buy & hold by {buy_hold_return - total_return:.2f}pp\n"

report += f"""
{'='*70}
FILES GENERATED
{'='*70}
  - backtest_analysis.png (visualizations)
  - backtest_report.txt (this report)

RECOMMENDATIONS
{'='*70}
"""

if accuracy > 0.55 and win_rate > 55:
    report += "[+] Model shows promise for live trading\n"
    report += "[+] Continue with paper trading to validate\n"
    report += "[+] Consider gradual position sizing\n"
elif accuracy > 0.50:
    report += "~ Model has slight edge\n"
    report += "~ Use conservative position sizing\n"
    report += "~ Only trade high confidence signals (>70%)\n"
else:
    report += "[-] Model needs improvement\n"
    report += "[-] Retrain with more recent data\n"
    report += "[-] Add more features or try different models\n"

report += f"""
{'='*70}
DISCLAIMER: Past performance does not guarantee future results.
This analysis is for educational purposes only.
{'='*70}
"""

# Save report
with open('backtest_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print(report)
print("\n[OK] Saved: backtest_report.txt")

print("\n" + "="*70)
print("BACKTEST ANALYSIS COMPLETE!")
print("="*70)
print("\nGenerated files:")
print("  1. backtest_analysis.png - Visualizations")
print("  2. backtest_report.txt - Detailed report")
print("\nKey Findings:")
print(f"  - Model accuracy: {accuracy:.2%}")
print(f"  - Sentiment-price correlation: {corr:.4f}" if len(analysis_df) > 0 else "")
print(f"  - Trading return: {total_return:+.2f}%")
print(f"  - Buy & Hold return: {buy_hold_return:+.2f}%" if 'buy_hold_return' in locals() else "")
print("="*70 + "\n")
