"""
Calculate Prediction Accuracy
Compares predictions with actual market movements
"""

import pandas as pd
import os
from datetime import datetime, timedelta

print("\n" + "="*70)
print("CALCULATING PREDICTION ACCURACY")
print("="*70 + "\n")

# Load predictions
predictions_file = 'predictions_history.csv'
if not os.path.exists(predictions_file):
    print("[ERROR] No predictions file found")
    exit(1)

pred_df = pd.read_csv(predictions_file)
pred_df['data_date'] = pd.to_datetime(pred_df['data_date'])
print(f"[OK] Loaded {len(pred_df)} predictions")

# Load price data
price_file = 'data/raw/price_data.csv'
if not os.path.exists(price_file):
    print("[ERROR] No price data found")
    exit(1)

price_df = pd.read_csv(price_file)
price_df['date'] = pd.to_datetime(price_df['date'])
print(f"[OK] Loaded {len(price_df)} days of price data")

# Calculate actual movements
print("\nCalculating actual market movements...")

results = []
for _, pred in pred_df.iterrows():
    pred_date = pred['data_date']

    # Find the price on prediction date
    current_price_row = price_df[price_df['date'] == pred_date]

    if len(current_price_row) == 0:
        # Try to find closest date
        closest_idx = (price_df['date'] - pred_date).abs().argmin()
        current_price_row = price_df.iloc[[closest_idx]]

    if len(current_price_row) > 0:
        current_price = current_price_row.iloc[0]['close']
        current_idx = price_df[price_df['date'] == current_price_row.iloc[0]['date']].index[0]

        # Get next day price
        if current_idx + 1 < len(price_df):
            next_price = price_df.iloc[current_idx + 1]['close']
            next_date = price_df.iloc[current_idx + 1]['date']

            # Calculate actual movement
            actual_direction = 'UP' if next_price > current_price else 'DOWN'
            actual_return = ((next_price - current_price) / current_price) * 100

            # Check if prediction was correct
            is_correct = (pred['direction'] == actual_direction)

            results.append({
                'prediction_date': pred['prediction_date'],
                'data_date': pred['data_date'],
                'predicted_direction': pred['direction'],
                'confidence': pred['confidence'],
                'actual_direction': actual_direction,
                'actual_return': actual_return,
                'is_correct': is_correct,
                'current_price': current_price,
                'next_price': next_price,
                'next_date': next_date
            })

# Create results DataFrame
results_df = pd.DataFrame(results)

if len(results_df) > 0:
    # Save to file
    results_df.to_csv('predictions_with_accuracy.csv', index=False)

    # Calculate statistics
    accuracy = (results_df['is_correct'].sum() / len(results_df)) * 100
    correct_count = results_df['is_correct'].sum()
    total_count = len(results_df)

    # Accuracy by confidence level
    high_conf = results_df[results_df['confidence'] >= 0.70]
    medium_conf = results_df[(results_df['confidence'] >= 0.60) & (results_df['confidence'] < 0.70)]
    low_conf = results_df[results_df['confidence'] < 0.60]

    print("\n" + "="*70)
    print("ACCURACY RESULTS")
    print("="*70)
    print(f"\nOverall Accuracy: {accuracy:.2f}%")
    print(f"Correct Predictions: {correct_count}/{total_count}")

    print(f"\nAccuracy by Confidence Level:")
    if len(high_conf) > 0:
        high_acc = (high_conf['is_correct'].sum() / len(high_conf)) * 100
        print(f"  High (>70%):   {high_acc:.2f}%  ({high_conf['is_correct'].sum()}/{len(high_conf)} predictions)")

    if len(medium_conf) > 0:
        med_acc = (medium_conf['is_correct'].sum() / len(medium_conf)) * 100
        print(f"  Medium (60-70%): {med_acc:.2f}%  ({medium_conf['is_correct'].sum()}/{len(medium_conf)} predictions)")

    if len(low_conf) > 0:
        low_acc = (low_conf['is_correct'].sum() / len(low_conf)) * 100
        print(f"  Low (<60%):    {low_acc:.2f}%  ({low_conf['is_correct'].sum()}/{len(low_conf)} predictions)")

    # Best and worst predictions
    print(f"\nBest Prediction:")
    best = results_df.loc[results_df['actual_return'].abs().idxmax()]
    print(f"  Date: {best['data_date']}")
    print(f"  Predicted: {best['predicted_direction']} (Confidence: {best['confidence']:.2f}%)")
    print(f"  Actual: {best['actual_direction']} ({best['actual_return']:+.2f}%)")
    print(f"  Result: {'CORRECT' if best['is_correct'] else 'WRONG'}")

    print(f"\n[OK] Saved results to: predictions_with_accuracy.csv")

else:
    print("\n[WARNING] No predictions could be matched with price data")

print("\n" + "="*70 + "\n")
