"""
Update predictions_with_accuracy.csv to include Nov 12-13
"""

import pandas as pd

print("\n" + "="*70)
print("UPDATING PREDICTIONS WITH ACCURACY")
print("="*70)

# Load predictions history
predictions_df = pd.read_csv('predictions_history.csv')
predictions_df['data_date'] = pd.to_datetime(predictions_df['data_date'])

# Load price data
price_df = pd.read_csv('data/raw/price_data.csv')
price_df['date'] = pd.to_datetime(price_df['date'])

# Load existing accuracy file
accuracy_df = pd.read_csv('predictions_with_accuracy.csv')
accuracy_df['data_date'] = pd.to_datetime(accuracy_df['data_date'])

print(f"\n[1/3] Loaded data:")
print(f"  Predictions: {len(predictions_df)} records (last: {predictions_df['data_date'].max()})")
print(f"  Accuracy file: {len(accuracy_df)} records (last: {accuracy_df['data_date'].max()})")

# Find predictions not in accuracy file
new_predictions = predictions_df[predictions_df['data_date'] > accuracy_df['data_date'].max()]

print(f"\n[2/3] Found {len(new_predictions)} new predictions to add")

new_records = []

for _, pred_row in new_predictions.iterrows():
    data_date = pred_row['data_date']

    # Get current and next price
    current_price_row = price_df[price_df['date'] == data_date]
    next_day_price_row = price_df[price_df['date'] > data_date].head(1)

    if len(current_price_row) == 0 or len(next_day_price_row) == 0:
        print(f"  Skipping {data_date} - missing price data")
        continue

    close_col = 'Close' if 'Close' in price_df.columns else 'close'

    current_price = current_price_row[close_col].values[0]
    next_price = next_day_price_row[close_col].values[0]
    next_date = next_day_price_row['date'].values[0]

    actual_return = ((next_price - current_price) / current_price) * 100
    actual_direction = 'UP' if actual_return > 0 else 'DOWN'
    is_correct = (pred_row['direction'] == actual_direction)

    new_record = {
        'prediction_date': pred_row['prediction_date'],
        'data_date': data_date,
        'predicted_direction': pred_row['direction'],
        'confidence': pred_row['confidence'],
        'actual_direction': actual_direction,
        'actual_return': actual_return,
        'is_correct': is_correct,
        'current_price': current_price,
        'next_price': next_price,
        'next_date': pd.to_datetime(next_date)
    }

    new_records.append(new_record)

    print(f"  Added {data_date}: Predicted={pred_row['direction']}, Actual={actual_direction}, Correct={is_correct}")

if new_records:
    new_df = pd.DataFrame(new_records)
    accuracy_df = pd.concat([accuracy_df, new_df], ignore_index=True)
    accuracy_df.to_csv('predictions_with_accuracy.csv', index=False)

    print(f"\n[3/3] Updated accuracy file:")
    print(f"  Total records: {len(accuracy_df)}")
    print(f"  Last date: {accuracy_df['data_date'].max()}")
    print("\n" + "="*70)
    print("[SUCCESS] Accuracy file updated")
    print("="*70 + "\n")
else:
    print(f"\n[3/3] No new records to add")
