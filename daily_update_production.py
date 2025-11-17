"""
Production Daily Update Script for S&P 500 Prediction System (Render Deployment)

This version uses PostgreSQL database for persistent storage instead of CSV files.
Falls back to CSV for local development.

Runs daily via Render Cron Job at 5 PM EST (after market close)
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import joblib
import os
from models.predict import Predictor
from utils.database import PredictionDatabase

print("\n" + "="*80)
print("S&P 500 AUTOMATED DAILY UPDATE (PRODUCTION)")
print("="*80)
print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Environment: {'PostgreSQL' if os.getenv('DATABASE_URL') else 'CSV (Local)'}")
print("="*80)

# Initialize database
try:
    db = PredictionDatabase()
    print("[OK] Database initialized")
except Exception as e:
    print(f"[ERROR] Database initialization failed: {e}")
    sys.exit(1)

# ============================================================================
# STEP 1: Fetch Latest Prices
# ============================================================================
print("\n[STEP 1/4] Fetching latest S&P 500 data...")
print("-" * 80)

try:
    sp500 = yf.Ticker('^GSPC')
    latest_data = sp500.history(period='5d')

    # Convert timezone-aware to timezone-naive
    latest_data.index = latest_data.index.tz_localize(None)

    latest_date = latest_data.index[-1]
    latest_close = latest_data['Close'].iloc[-1]

    print(f"[OK] Fetched latest data")
    print(f"  Date: {latest_date.strftime('%Y-%m-%d')}")
    print(f"  Close: ${latest_close:,.2f}")

    # Update price data file (still using CSV for price data - it's refreshed daily anyway)
    price_file = 'data/raw/price_data.csv'
    if os.path.exists(price_file):
        existing_data = pd.read_csv(price_file, index_col='date', parse_dates=True)

        # Combine and remove duplicates
        combined = pd.concat([existing_data, latest_data[['Open', 'High', 'Low', 'Close', 'Volume']]])
        combined = combined[~combined.index.duplicated(keep='last')]
        combined = combined.sort_index()

        # Calculate returns
        combined['returns'] = combined['Close'].pct_change()
        combined['direction'] = (combined['returns'] > 0).astype(int)
        combined['target'] = combined['direction'].shift(-1)

        # Save
        combined.reset_index().rename(columns={'index': 'date'}).to_csv(price_file, index=False)

        new_records = len(combined) - len(existing_data)
        print(f"[OK] Updated price data: {new_records} new records")
    else:
        print("[ERROR] Price data file not found - skipping update")

except Exception as e:
    print(f"[ERROR] Error fetching prices: {e}")
    sys.exit(1)

# ============================================================================
# STEP 2: Update Previous Predictions with Actual Results
# ============================================================================
print("\n[STEP 2/4] Updating prediction accuracy...")
print("-" * 80)

try:
    # Get predictions from database
    predictions_df = db.get_predictions()

    if len(predictions_df) > 0:
        predictions_df['data_date'] = pd.to_datetime(predictions_df['data_date'])

        # Load price data
        price_df = pd.read_csv('data/raw/price_data.csv')
        price_df['date'] = pd.to_datetime(price_df['date'])

        # Get existing accuracy data
        accuracy_df = db.get_accuracy_data()

        if len(accuracy_df) > 0:
            accuracy_df['data_date'] = pd.to_datetime(accuracy_df['data_date'])
            last_processed_date = accuracy_df['data_date'].max()
        else:
            last_processed_date = pd.Timestamp('2000-01-01')

        # Find predictions that need accuracy calculated
        new_predictions = predictions_df[predictions_df['data_date'] > last_processed_date]

        new_records_count = 0

        for _, pred_row in new_predictions.iterrows():
            data_date = pred_row['data_date']

            # Get current and next day prices
            current_price_row = price_df[price_df['date'] == data_date]
            next_day_price_row = price_df[price_df['date'] > data_date].head(1)

            if len(current_price_row) == 0 or len(next_day_price_row) == 0:
                # Not enough data yet (prediction is for today or future)
                continue

            # Handle both 'close' and 'Close' columns
            close_col = 'Close' if 'Close' in price_df.columns else 'close'

            current_price = current_price_row[close_col].values[0]
            next_price = next_day_price_row[close_col].values[0]
            next_date = next_day_price_row['date'].values[0]

            # Calculate actual return
            actual_return = ((next_price - current_price) / current_price) * 100
            actual_direction = 'UP' if actual_return > 0 else 'DOWN'
            is_correct = (pred_row['direction'] == actual_direction)

            accuracy_data = {
                'prediction_date': pred_row['prediction_date'],
                'data_date': str(data_date.date()),
                'predicted_direction': pred_row['direction'],
                'confidence': pred_row['confidence'],
                'actual_direction': actual_direction,
                'actual_return': actual_return,
                'is_correct': is_correct,
                'current_price': current_price,
                'next_price': next_price,
                'next_date': str(pd.to_datetime(next_date).date())
            }

            # Save to database
            if db.save_accuracy(accuracy_data):
                new_records_count += 1

        if new_records_count > 0:
            # Recalculate stats
            accuracy_df = db.get_accuracy_data()
            correct_count = accuracy_df['is_correct'].sum() if len(accuracy_df) > 0 else 0
            accuracy_pct = (correct_count / new_records_count) * 100 if new_records_count > 0 else 0

            print(f"[OK] Updated {new_records_count} predictions with actual results")
            print(f"  Correct: {correct_count}/{new_records_count} ({accuracy_pct:.1f}%)")
        else:
            print("[OK] No new predictions to update (waiting for next day data)")
    else:
        print("[OK] No predictions yet - skipping accuracy update")

except Exception as e:
    print(f"[ERROR] Error updating accuracy: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# STEP 3: Generate New Prediction
# ============================================================================
print("\n[STEP 3/4] Generating new prediction...")
print("-" * 80)

try:
    # Check if model exists
    model_name = "sp500_complete_20251113"
    model_path = f"models/{model_name}.pkl"

    if not os.path.exists(model_path):
        print(f"[ERROR] Model not found: {model_path}")
        print("  Skipping prediction generation")
    else:
        # Load model
        predictor = Predictor(model_name=model_name)

        # Load latest features
        if os.path.exists('data/features/features_complete.csv'):
            features_df = pd.read_csv('data/features/features_complete.csv')
            data_source = "Complete"
        elif os.path.exists('data/features/features.csv'):
            features_df = pd.read_csv('data/features/features.csv')
            data_source = "Standard"
        else:
            print("[ERROR] No feature data found")
            print("  Please run: python run_complete_pipeline.py")
            sys.exit(1)

        latest = features_df.tail(1)
        latest_date = latest['date'].values[0]

        # Check if prediction already exists
        if db.prediction_exists_today(latest_date):
            print("[OK] Prediction already exists for today - skipping")
        else:
            # Make prediction
            result = predictor.predict(latest)

            if result:
                # Save prediction to database
                prediction_data = {
                    'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'data_date': latest_date,
                    'direction': result['direction'],
                    'confidence': result['confidence'],
                    'prob_up': result['probability_up'],
                    'prob_down': result['probability_down']
                }

                if db.save_prediction(prediction_data):
                    print(f"[OK] New prediction generated and saved")
                    print(f"  Data date: {latest_date}")
                    print(f"  Direction: {result['direction']}")
                    print(f"  Confidence: {result['confidence']:.2%}")
                else:
                    print("[ERROR] Failed to save prediction")
            else:
                print("[ERROR] Prediction failed")

except Exception as e:
    print(f"[ERROR] Error generating prediction: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# STEP 4: Summary Report
# ============================================================================
print("\n[STEP 4/4] Summary Report")
print("-" * 80)

try:
    # Overall accuracy
    accuracy_df = db.get_accuracy_data()

    if len(accuracy_df) > 0:
        total = len(accuracy_df)
        correct = accuracy_df['is_correct'].sum()
        accuracy = (correct / total) * 100

        print(f"\n[OVERALL PERFORMANCE]")
        print(f"  Total predictions: {total}")
        print(f"  Correct: {correct}")
        print(f"  Accuracy: {accuracy:.2f}%")

        # Recent performance (last 30 days)
        accuracy_df['prediction_date'] = pd.to_datetime(accuracy_df['prediction_date'], format='mixed')
        recent = accuracy_df[accuracy_df['prediction_date'] >= datetime.now() - timedelta(days=30)]

        if len(recent) > 0:
            recent_correct = recent['is_correct'].sum()
            recent_accuracy = (recent_correct / len(recent)) * 100

            print(f"\n[LAST 30 DAYS]")
            print(f"  Predictions: {len(recent)}")
            print(f"  Correct: {recent_correct}")
            print(f"  Accuracy: {recent_accuracy:.2f}%")

    # Latest prediction
    predictions_df = db.get_predictions(limit=1)

    if len(predictions_df) > 0:
        latest_pred = predictions_df.iloc[0]

        print(f"\n[LATEST PREDICTION]")
        print(f"  Date: {latest_pred['prediction_date']}")
        print(f"  Direction: {latest_pred['direction']}")
        print(f"  Confidence: {latest_pred['confidence']:.2%}")

except Exception as e:
    print(f"[ERROR] Error generating summary: {e}")

print("\n" + "="*80)
print("DAILY UPDATE COMPLETE")
print("="*80)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80 + "\n")
