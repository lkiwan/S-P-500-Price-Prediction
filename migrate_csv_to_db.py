"""
Migrate existing CSV data to PostgreSQL database
Run this ONCE to import historical predictions and accuracy data
"""

import sys
sys.path.append('src')

import pandas as pd
import os
from datetime import datetime
from utils.database import PredictionDatabase

print("\n" + "="*80)
print("MIGRATING CSV DATA TO POSTGRESQL DATABASE")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# Initialize database
try:
    db = PredictionDatabase()

    if not db.use_postgres:
        print("\n[WARNING] Not connected to PostgreSQL!")
        print("This script should run on Render where DATABASE_URL is set.")
        print("Exiting...")
        sys.exit(1)

    print(f"\n[OK] Connected to PostgreSQL database")

except Exception as e:
    print(f"\n[ERROR] Database connection failed: {e}")
    sys.exit(1)

# ============================================================================
# STEP 1: Migrate Predictions History
# ============================================================================
print("\n[STEP 1/2] Migrating predictions history...")
print("-" * 80)

predictions_file = 'predictions_history.csv'

if os.path.exists(predictions_file):
    try:
        df = pd.read_csv(predictions_file)
        print(f"  Found {len(df)} predictions in CSV file")

        # Check what's already in database
        existing_df = db.get_predictions()
        existing_count = len(existing_df)
        print(f"  Database currently has {existing_count} predictions")

        migrated = 0
        skipped = 0

        for _, row in df.iterrows():
            prediction_data = {
                'prediction_date': row['prediction_date'],
                'data_date': str(row['data_date']),
                'direction': row['direction'],
                'confidence': float(row['confidence']),
                'prob_up': float(row['prob_up']),
                'prob_down': float(row['prob_down'])
            }

            # Try to save
            if db.save_prediction(prediction_data):
                migrated += 1
            else:
                skipped += 1

            if (migrated + skipped) % 50 == 0:
                print(f"  Progress: {migrated + skipped}/{len(df)}...")

        print(f"\n[OK] Migration complete:")
        print(f"  Migrated: {migrated} predictions")
        print(f"  Skipped: {skipped} (duplicates or errors)")

    except Exception as e:
        print(f"\n[ERROR] Failed to migrate predictions: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"  [SKIP] No predictions_history.csv file found")

# ============================================================================
# STEP 2: Migrate Accuracy Data
# ============================================================================
print("\n[STEP 2/2] Migrating accuracy data...")
print("-" * 80)

accuracy_file = 'predictions_with_accuracy.csv'

if os.path.exists(accuracy_file):
    try:
        df = pd.read_csv(accuracy_file)
        print(f"  Found {len(df)} accuracy records in CSV file")

        # Check what's already in database
        existing_df = db.get_accuracy_data()
        existing_count = len(existing_df)
        print(f"  Database currently has {existing_count} accuracy records")

        migrated = 0
        skipped = 0

        for _, row in df.iterrows():
            accuracy_data = {
                'prediction_date': row['prediction_date'],
                'data_date': str(row['data_date']),
                'predicted_direction': row['predicted_direction'],
                'confidence': float(row['confidence']),
                'actual_direction': row['actual_direction'],
                'actual_return': float(row['actual_return']),
                'is_correct': bool(row['is_correct']),
                'current_price': float(row['current_price']),
                'next_price': float(row['next_price']),
                'next_date': str(row['next_date'])
            }

            # Try to save
            if db.save_accuracy(accuracy_data):
                migrated += 1
            else:
                skipped += 1

            if (migrated + skipped) % 50 == 0:
                print(f"  Progress: {migrated + skipped}/{len(df)}...")

        print(f"\n[OK] Migration complete:")
        print(f"  Migrated: {migrated} accuracy records")
        print(f"  Skipped: {skipped} (duplicates or errors)")

    except Exception as e:
        print(f"\n[ERROR] Failed to migrate accuracy data: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"  [SKIP] No predictions_with_accuracy.csv file found")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("MIGRATION SUMMARY")
print("="*80)

# Get final counts
predictions_df = db.get_predictions()
accuracy_df = db.get_accuracy_data()

print(f"\nDatabase now contains:")
print(f"  Predictions: {len(predictions_df)}")
print(f"  Accuracy records: {len(accuracy_df)}")

if len(accuracy_df) > 0:
    correct = accuracy_df['is_correct'].sum()
    total = len(accuracy_df)
    accuracy = (correct / total) * 100
    print(f"\n  Overall accuracy: {accuracy:.2f}% ({correct}/{total})")

print("\n" + "="*80)
print("MIGRATION COMPLETE")
print("="*80)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80 + "\n")

print("\nNext steps:")
print("1. Refresh your dashboard: https://s-p-500-price-prediction.onrender.com")
print("2. All data should now be visible!")
print("3. Daily cron job will continue adding new predictions automatically")
