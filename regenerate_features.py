"""
Regenerate features from existing price data (includes Nov 12-13)
"""

import sys
sys.path.append('src')

import pandas as pd
from features.feature_engineer import FeatureEngineer

print("\n" + "="*70)
print("REGENERATING FEATURES FROM PRICE DATA")
print("="*70)

# Load price data
print("\n[1/3] Loading price data...")
price_df = pd.read_csv('data/raw/price_data.csv')
price_df['date'] = pd.to_datetime(price_df['date'])

print(f"  Loaded: {len(price_df)} days")
print(f"  Date range: {price_df['date'].min()} to {price_df['date'].max()}")
print(f"  Last 3 dates: {price_df['date'].tail(3).tolist()}")

# Load sentiment data
print("\n[2/3] Loading sentiment data...")
try:
    sentiment_df = pd.read_csv('data/processed/sentiment_daily_real.csv')
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    print(f"  Loaded real sentiment: {len(sentiment_df)} days")
except:
    try:
        sentiment_df = pd.read_csv('data/processed/sentiment_daily.csv')
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
        print(f"  Loaded synthetic sentiment: {len(sentiment_df)} days")
    except:
        print("  No sentiment data - using empty DataFrame")
        sentiment_df = pd.DataFrame(columns=['date'])
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])

# Create features
print("\n[3/4] Generating technical indicators and features...")
engineer = FeatureEngineer()
features_df = engineer.create_all_features(sentiment_df, price_df)

print(f"  Generated: {len(features_df.columns)} features")
print(f"  Feature date range: {features_df['date'].min()} to {features_df['date'].max()}")

# Load economic data and merge
print("\n[4/4] Merging with economic data...")
try:
    # Load existing complete features to get economic/sentiment columns
    existing_complete = pd.read_csv('data/features/features_complete.csv')
    existing_complete['date'] = pd.to_datetime(existing_complete['date'])

    # Get columns that exist in complete but not in basic features
    extra_cols = [col for col in existing_complete.columns
                  if col not in features_df.columns and col != 'date']

    if extra_cols:
        # Merge to get the extra columns
        features_df = pd.merge(
            features_df,
            existing_complete[['date'] + extra_cols],
            on='date',
            how='left'
        )

        # Forward fill for new dates
        features_df[extra_cols] = features_df[extra_cols].fillna(method='ffill')

        print(f"  Merged {len(extra_cols)} additional columns (economic/sentiment)")
    else:
        print("  No additional columns to merge")

except Exception as e:
    print(f"  Warning: Could not merge additional data: {e}")
    print("  Continuing with technical features only...")

# Save
features_df.to_csv('data/features/features_complete.csv', index=False)

print("\n" + "="*70)
print(f"[SUCCESS] Features saved: {len(features_df)} days")
print(f"Last date: {features_df['date'].max()}")
print("="*70 + "\n")
