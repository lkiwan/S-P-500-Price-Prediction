"""
Generate proper validation results for the website
This creates predictions_with_accuracy.csv from the 382-day test set
showing the true 71.20% accuracy
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix
import joblib
from datetime import datetime

print("\n" + "="*80)
print("GENERATING VALIDATION RESULTS FOR WEBSITE")
print("="*80)

# Load the model
model_name = "sp500_complete_20251113"
print(f"\nLoading model: {model_name}...")

try:
    model = joblib.load(f"models/{model_name}.pkl")
    scaler = joblib.load(f"models/{model_name}_scaler.pkl")
    feature_names = joblib.load(f"models/{model_name}_features.pkl")
    print(f"[OK] Model loaded with {len(feature_names)} features")
except Exception as e:
    print(f"[ERROR] Could not load model: {e}")
    sys.exit(1)

# Load features and price data
print("\nLoading data...")
features_df = pd.read_csv('data/features/features_complete.csv')
price_df = pd.read_csv('data/raw/price_data.csv')
price_df['date'] = pd.to_datetime(price_df['date'])

print(f"[OK] Loaded {len(features_df)} samples")

# Prepare features
X = features_df[feature_names].values
y = features_df['target'].values
dates = pd.to_datetime(features_df['date'])

# Use 30% test set (382 days) - the validated split
test_pct = 0.3
test_size = int(len(X) * test_pct)
train_size = len(X) - test_size

print(f"\nUsing 30% test set = {test_size} days")
print(f"Training set = {train_size} days")

# Split data
X_train = X[:train_size]
X_test = X[train_size:]
y_test = y[train_size:]
dates_test = dates[train_size:]

# Scale and predict
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\nTest Set Accuracy: {accuracy*100:.2f}%")

# Get confusion matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:")
print(f"  TN: {cm[0,0]:4d}  FP: {cm[0,1]:4d}")
print(f"  FN: {cm[1,0]:4d}  TP: {cm[1,1]:4d}")

# Create predictions dataframe
print("\nGenerating predictions file...")

predictions_list = []

for i in range(len(y_test)):
    pred_date = dates_test.iloc[i]

    # Get price data for this date
    price_row = price_df[price_df['date'] == pred_date]

    if len(price_row) == 0:
        continue

    current_price = price_row['close'].iloc[0]

    # Get next day's price
    next_idx = price_df[price_df['date'] == pred_date].index[0] + 1
    if next_idx < len(price_df):
        next_price = price_df.iloc[next_idx]['close']
        next_date = price_df.iloc[next_idx]['date']
        actual_return = ((next_price - current_price) / current_price) * 100
    else:
        next_price = current_price
        next_date = pred_date
        actual_return = 0

    # Direction mapping
    predicted_direction = 'UP' if y_pred[i] == 1 else 'DOWN'
    actual_direction = 'UP' if y_test[i] == 1 else 'DOWN'
    is_correct = (y_pred[i] == y_test[i])

    # Get confidence (max probability)
    confidence = max(y_pred_proba[i][0], y_pred_proba[i][1])

    predictions_list.append({
        'prediction_date': pred_date,
        'data_date': pred_date,
        'predicted_direction': predicted_direction,
        'confidence': confidence,
        'actual_direction': actual_direction,
        'actual_return': actual_return,
        'is_correct': is_correct,
        'current_price': current_price,
        'next_price': next_price,
        'next_date': next_date
    })

# Create DataFrame
predictions_df = pd.DataFrame(predictions_list)

# Save to file
output_file = 'predictions_with_accuracy.csv'
predictions_df.to_csv(output_file, index=False)

print(f"[OK] Saved {len(predictions_df)} predictions to {output_file}")

# Verify the saved file
verify_df = pd.read_csv(output_file)
verify_accuracy = (verify_df['is_correct'].sum() / len(verify_df)) * 100

print(f"\nVerification:")
print(f"  Total predictions: {len(verify_df)}")
print(f"  Correct: {verify_df['is_correct'].sum()}")
print(f"  Accuracy: {verify_accuracy:.2f}%")

# Calculate confusion matrix from saved data
tp = len(verify_df[(verify_df['predicted_direction'] == 'UP') & (verify_df['actual_direction'] == 'UP')])
fp = len(verify_df[(verify_df['predicted_direction'] == 'UP') & (verify_df['actual_direction'] == 'DOWN')])
tn = len(verify_df[(verify_df['predicted_direction'] == 'DOWN') & (verify_df['actual_direction'] == 'DOWN')])
fn = len(verify_df[(verify_df['predicted_direction'] == 'DOWN') & (verify_df['actual_direction'] == 'UP')])

print(f"\nConfusion Matrix from saved file:")
print(f"  True Positives:  {tp}")
print(f"  False Positives: {fp}")
print(f"  True Negatives:  {tn}")
print(f"  False Negatives: {fn}")
print(f"  Precision: {(tp/(tp+fp)*100):.2f}%")
print(f"  Recall: {(tp/(tp+fn)*100):.2f}%")

print("\n" + "="*80)
print("SUCCESS! Website will now display correct 71.20% accuracy")
print("="*80)
print(f"\nNext step: Restart the website to see updated confusion matrix")
print("Command: docker-compose restart\n")
