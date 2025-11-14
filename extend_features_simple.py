"""
Simple approach: Extend features for Nov 12-13 by forward-filling from Nov 11
"""

import pandas as pd
import numpy as np

print("\n" + "="*70)
print("EXTENDING FEATURES FOR NOV 12-13")
print("="*70)

# Load existing features
features_df = pd.read_csv('data/features/features_complete.csv')
features_df['date'] = pd.to_datetime(features_df['date'])

print(f"\n[1/3] Loaded features: {len(features_df)} days")
print(f"  Last date: {features_df['date'].max()}")

# Load price data to get Nov 12-13 actual prices
price_df = pd.read_csv('data/raw/price_data.csv')
price_df['date'] = pd.to_datetime(price_df['date'])

nov12_price = price_df[price_df['date'] == '2025-11-12']
nov13_price = price_df[price_df['date'] == '2025-11-13']

if len(nov12_price) == 0 or len(nov13_price) == 0:
    print("\n[ERROR] Nov 12 or Nov 13 prices not found in price_data.csv")
    exit(1)

print(f"\n[2/3] Found Nov 12-13 prices in price_data.csv")

# Get last row (Nov 11) as template
last_row = features_df[features_df['date'] == '2025-11-11'].iloc[0].copy()

# Create Nov 12 features
nov12_features = last_row.copy()
nov12_features['date'] = pd.Timestamp('2025-11-12')

# Update with actual Nov 12 price columns
for col in nov12_price.columns:
    if col in nov12_features.index and col != 'date':
        nov12_features[col] = nov12_price[col].values[0]

# Create Nov 13 features
nov13_features = nov12_features.copy()
nov13_features['date'] = pd.Timestamp('2025-11-13')

# Update with actual Nov 13 price columns
for col in nov13_price.columns:
    if col in nov13_features.index and col != 'date':
        nov13_features[col] = nov13_price[col].values[0]

# Append to features_df
new_rows = pd.DataFrame([nov12_features, nov13_features])
features_df = pd.concat([features_df, new_rows], ignore_index=True)

# Save
features_df.to_csv('data/features/features_complete.csv', index=False)

print(f"\n[3/3] Extended features saved")
print(f"  Total rows: {len(features_df)}")
print(f"  New last date: {features_df['date'].max()}")

print("\n" + "="*70)
print("[SUCCESS] Features extended for Nov 12-13")
print("="*70 + "\n")
