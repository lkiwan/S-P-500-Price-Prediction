"""
Generate missing predictions for Nov 12-13, 2025
"""

import sys
sys.path.append('src')

import pandas as pd
import joblib
from datetime import datetime
import os

print("\n" + "="*70)
print("GENERATING MISSING PREDICTIONS")
print("="*70)

# Load features
features_df = pd.read_csv('data/features/features_complete.csv')
features_df['date'] = pd.to_datetime(features_df['date'])

# Filter for Nov 12 and 13
missing_dates = ['2025-11-12', '2025-11-13']

# Load model
model_name = "sp500_complete_20251113"
try:
    model = joblib.load(f"models/{model_name}.pkl")
    scaler = joblib.load(f"models/{model_name}_scaler.pkl")
    feature_names = joblib.load(f"models/{model_name}_features.pkl")
    print(f"\n[OK] Loaded model: {model_name}")
except FileNotFoundError:
    print(f"\n[ERROR] Model not found: {model_name}")
    sys.exit(1)

# Load existing predictions
if os.path.exists('predictions_history.csv'):
    predictions_df = pd.read_csv('predictions_history.csv')
else:
    predictions_df = pd.DataFrame()

print(f"\n[OK] Current predictions: {len(predictions_df)} records")
print(f"[OK] Last prediction date: {predictions_df['data_date'].iloc[-1] if len(predictions_df) > 0 else 'None'}")

# Generate predictions for missing dates
new_predictions = []

for date_str in missing_dates:
    date_features = features_df[features_df['date'] == date_str]

    if len(date_features) == 0:
        print(f"\n[ERROR] No features found for {date_str}")
        continue

    # Make prediction
    X = date_features[feature_names].values
    X_scaled = scaler.transform(X)

    prediction = model.predict(X_scaled)[0]
    probabilities = model.predict_proba(X_scaled)[0]

    direction = "UP" if prediction == 1 else "DOWN"
    confidence = max(probabilities)
    prob_down = probabilities[0]
    prob_up = probabilities[1]

    # Create prediction record
    new_record = {
        'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_date': date_str,
        'direction': direction,
        'confidence': confidence,
        'prob_up': prob_up,
        'prob_down': prob_down
    }

    new_predictions.append(new_record)

    print(f"\n[OK] Generated prediction for {date_str}:")
    print(f"  Direction: {direction}")
    print(f"  Confidence: {confidence:.2%}")
    print(f"  Prob UP: {prob_up:.2%}, Prob DOWN: {prob_down:.2%}")

# Append new predictions
if new_predictions:
    new_df = pd.DataFrame(new_predictions)
    predictions_df = pd.concat([predictions_df, new_df], ignore_index=True)
    predictions_df.to_csv('predictions_history.csv', index=False)

    print(f"\n" + "="*70)
    print(f"[SUCCESS] Added {len(new_predictions)} new predictions")
    print(f"[OK] Total predictions: {len(predictions_df)}")
    print("="*70 + "\n")
else:
    print(f"\n[ERROR] No new predictions generated")
