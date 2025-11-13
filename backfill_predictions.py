"""
Backfill Prediction History
Populates predictions_history.csv with historical predictions from backtest period
"""

import sys
sys.path.append('src')

import pandas as pd
import os
from datetime import datetime
from models.predict import Predictor

print("\n" + "="*70)
print("BACKFILLING PREDICTION HISTORY")
print("="*70)
print("This will add historical predictions to your dashboard")
print("="*70 + "\n")

# Load features
features_file = 'data/features/features_complete.csv'
if not os.path.exists(features_file):
    print("[ERROR] Features file not found!")
    print("  Please run: python run_complete_pipeline.py")
    sys.exit(1)

print("Loading features...")
features_df = pd.read_csv(features_file)
features_df['date'] = pd.to_datetime(features_df['date'])
print(f"[OK] Loaded {len(features_df)} samples")

# Get last 60 days (approximately 2 months of trading days)
print("\nSelecting last 60 trading days...")
recent_features = features_df.tail(60).copy()
print(f"[OK] Selected {len(recent_features)} days")
print(f"  Date range: {recent_features['date'].min()} to {recent_features['date'].max()}")

# Load model
model_name = "sp500_complete_20251113"
model_path = f"models/{model_name}.pkl"

if not os.path.exists(model_path):
    print(f"\n[ERROR] Model not found: {model_path}")
    print("  Please run: python run_complete_pipeline.py")
    sys.exit(1)

print(f"\nLoading model: {model_name}...")
try:
    predictor = Predictor(model_name=model_name)
    print("[OK] Model loaded")
except Exception as e:
    print(f"[ERROR] Failed to load model: {e}")
    sys.exit(1)

# Generate predictions for each day
print(f"\nGenerating predictions for {len(recent_features)} days...")
print("-" * 70)

predictions_list = []
for idx, row in recent_features.iterrows():
    try:
        # Create single row DataFrame for prediction
        single_row = pd.DataFrame([row])

        # Make prediction
        result = predictor.predict(single_row)

        if result:
            prediction_record = {
                'prediction_date': row['date'].strftime('%Y-%m-%d %H:%M:%S'),
                'data_date': row['date'].strftime('%Y-%m-%d'),
                'direction': result['direction'],
                'confidence': result['confidence'],
                'prob_up': result['probability_up'],
                'prob_down': result['probability_down']
            }
            predictions_list.append(prediction_record)

            # Show progress every 10 predictions
            if len(predictions_list) % 10 == 0:
                print(f"  Generated {len(predictions_list)} predictions...")

    except Exception as e:
        print(f"  [Warning] Failed for {row['date']}: {e}")
        continue

print(f"\n[OK] Generated {len(predictions_list)} predictions")

# Create DataFrame
predictions_df = pd.DataFrame(predictions_list)

# Check if predictions_history.csv exists
predictions_file = "predictions_history.csv"
if os.path.exists(predictions_file):
    print(f"\n[INFO] Existing predictions file found")
    existing_df = pd.read_csv(predictions_file)
    print(f"  Current predictions: {len(existing_df)}")

    # Automatically append - avoid duplicates by checking dates
    print("\n[AUTO] Appending new predictions (skipping duplicates)...")
    existing_dates = set(existing_df['data_date'].values)
    new_predictions = predictions_df[~predictions_df['data_date'].isin(existing_dates)]

    if len(new_predictions) > 0:
        combined_df = pd.concat([existing_df, new_predictions], ignore_index=True)
        # Sort by date
        combined_df['data_date_sort'] = pd.to_datetime(combined_df['data_date'])
        combined_df = combined_df.sort_values('data_date_sort').drop('data_date_sort', axis=1)
        combined_df.to_csv(predictions_file, index=False)
        print(f"[OK] Appended {len(new_predictions)} new predictions")
        print(f"  Total predictions now: {len(combined_df)}")
        predictions_df = combined_df
    else:
        print("[INFO] No new predictions to add (all dates already exist)")
        predictions_df = existing_df

else:
    # Create new file
    predictions_df.to_csv(predictions_file, index=False)
    print(f"\n[OK] Created new predictions file with {len(predictions_df)} predictions")

# Show summary statistics
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

# Group by month
predictions_df['data_date'] = pd.to_datetime(predictions_df['data_date'])
predictions_df['month'] = predictions_df['data_date'].dt.to_period('M')

monthly_stats = predictions_df.groupby('month').agg({
    'direction': lambda x: f"{(x=='UP').sum()}/{len(x)} UP",
    'confidence': lambda x: f"{x.mean()*100:.1f}%"
}).reset_index()

monthly_stats['month'] = monthly_stats['month'].astype(str)

print("\nMonthly Breakdown:")
print("-" * 70)
for _, row in monthly_stats.iterrows():
    print(f"  {row['month']:12s}  Predictions: {row['direction']:12s}  Avg Confidence: {row['confidence']}")

print("\n" + "="*70)
print("BACKFILL COMPLETE!")
print("="*70)
print("\nYour dashboard now has historical data!")
print("\nNext steps:")
print("  1. Refresh your browser (F5)")
print("  2. You should now see multiple months in the chart")
print("  3. Dashboard will show trends over time")
print("\n" + "="*70 + "\n")
