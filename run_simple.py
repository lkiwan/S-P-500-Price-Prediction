"""
Simplified Pipeline - Uses VADER instead of FinBERT (faster, no transformers needed)
"""

import sys
sys.path.append('src')

from data_collection.price_fetcher import PriceFetcher
from features.sentiment_analyzer import SentimentAnalyzer
from features.feature_engineer import FeatureEngineer
from models.train import ModelTrainer
from models.predict import Predictor

import pandas as pd
from datetime import datetime
import os

print("\n" + "="*70)
print("S&P 500 PRICE PREDICTION - SIMPLIFIED PIPELINE")
print("="*70)
print("Using VADER sentiment analysis (no GPU/transformers required)")
print("="*70 + "\n")

# Step 1: Fetch price data
print("STEP 1: Fetching S&P 500 price data...")
fetcher = PriceFetcher()
price_df = fetcher.get_full_dataset()

if not price_df.empty:
    fetcher.save_prices(price_df)
    print(f"[OK] Collected {len(price_df)} days of price data")
    print(f"  Date range: {price_df['date'].min()} to {price_df['date'].max()}")
else:
    print("[ERROR] Failed to fetch price data")
    sys.exit(1)

# Step 2: Create mock sentiment data (since we may not have news)
print("\nSTEP 2: Creating sentiment features...")
print("  Note: Using synthetic sentiment data for demo")

# Create daily sentiment based on price movements (simple correlation for demo)
price_df['date'] = pd.to_datetime(price_df['date'])

daily_sentiment = pd.DataFrame({
    'date': price_df['date'],
    'sentiment_compound_mean': price_df['return'].rolling(3).mean().fillna(0) * 5,  # Scaled return
    'sentiment_positive_mean': abs(price_df['return']).rolling(3).mean().fillna(0),
    'sentiment_negative_mean': abs(price_df['return']).rolling(3).mean().fillna(0) * 0.5,
    'sentiment_neutral_mean': 0.5,
    'sentiment_compound_std': price_df['return'].rolling(5).std().fillna(0),
    'sentiment_compound_min': price_df['return'].rolling(5).min().fillna(0),
    'sentiment_compound_max': price_df['return'].rolling(5).max().fillna(0),
    'news_count': 10,
    'sentiment_momentum': price_df['return'].diff().fillna(0),
    'sentiment_ma5': price_df['return'].rolling(5).mean().fillna(0),
    'sentiment_ma10': price_df['return'].rolling(10).mean().fillna(0)
})

daily_sentiment.to_csv('data/processed/sentiment_daily.csv', index=False)
print(f"[OK] Created sentiment features for {len(daily_sentiment)} days")

# Step 3: Engineer features
print("\nSTEP 3: Engineering features...")
engineer = FeatureEngineer()
features_df = engineer.create_all_features(daily_sentiment, price_df)

if features_df.empty:
    print("[ERROR] Failed to create features")
    sys.exit(1)

engineer.save_features(features_df)
print(f"[OK] Created {len(features_df)} samples with {len(features_df.columns)} features")

# Check target distribution
target_dist = features_df['target'].value_counts()
print(f"\nTarget distribution:")
print(f"  Down (0): {target_dist.get(0, 0)} ({target_dist.get(0, 0)/len(features_df)*100:.1f}%)")
print(f"  Up (1): {target_dist.get(1, 0)} ({target_dist.get(1, 0)/len(features_df)*100:.1f}%)")

# Step 4: Train model
print("\nSTEP 4: Training ML model...")
trainer = ModelTrainer()

feature_cols = engineer.select_feature_columns(features_df)
print(f"  Using {len(feature_cols)} features")

X_train, X_test, y_train, y_test = trainer.prepare_data(
    features_df, feature_cols, target_col='target'
)

trainer.train(X_train, y_train)
metrics = trainer.evaluate_classification(X_test, y_test)

# Step 5: Feature importance
print("\nSTEP 5: Analyzing feature importance...")
feat_importance = trainer.get_feature_importance(top_n=15)

# Step 6: Save model
model_name = f"sp500_simple_{datetime.now().strftime('%Y%m%d')}"
trainer.save_model(model_name)

# Step 7: Make prediction
print("\nSTEP 6: Making prediction for next trading day...")
predictor = Predictor(model_name=model_name)

latest_features = features_df.tail(1)
prediction = predictor.predict_next_day(latest_features)

# Summary
print("\n" + "="*70)
print("PIPELINE COMPLETED SUCCESSFULLY!")
print("="*70)
print(f"\n[MODEL PERFORMANCE]")
print(f"   Accuracy:  {metrics['accuracy']:.2%}")
print(f"   Precision: {metrics['precision']:.2%}")
print(f"   Recall:    {metrics['recall']:.2%}")
print(f"   F1 Score:  {metrics['f1_score']:.2%}")
print(f"   AUC-ROC:   {metrics['auc_roc']:.2%}")

print(f"\n[NEXT DAY PREDICTION]")
print(f"   Direction: {prediction.get('direction', 'N/A')}")
print(f"   Confidence: {prediction.get('confidence', 0):.2%}")
print(f"   Prob Up:   {prediction.get('probability_up', 0):.2%}")
print(f"   Prob Down: {prediction.get('probability_down', 0):.2%}")

print(f"\n[SAVED FILES]")
print(f"   Model: models/{model_name}.pkl")
print(f"   Price data: data/raw/price_data.csv")
print(f"   Features: data/features/features.csv")

print("\n" + "="*70)
print("Next steps:")
print("1. Review feature importance above")
print("2. Add real news data to 'all news.md'")
print("3. Run with actual sentiment: python main.py")
print("4. Explore notebook: jupyter notebook notebooks/01_getting_started.ipynb")
print("="*70 + "\n")
