"""
Full Pipeline with REAL News Sentiment
Uses the scraped news articles for genuine sentiment analysis
"""

import sys
sys.path.append('src')

from data_collection.price_fetcher import PriceFetcher
from preprocessing.text_cleaner import TextCleaner
from features.sentiment_analyzer import SentimentAnalyzer
from features.feature_engineer import FeatureEngineer
from models.train import ModelTrainer
from models.predict import Predictor

import pandas as pd
from datetime import datetime

print("\n" + "="*70)
print("S&P 500 PREDICTION - WITH REAL NEWS SENTIMENT")
print("="*70)
print("Using 104 real news articles scraped from Finviz and other sources")
print("="*70 + "\n")

# Step 1: Load real news
print("STEP 1: Loading real news articles...")
try:
    news_df = pd.read_csv('data/raw/news_data.csv')
    print(f"[OK] Loaded {len(news_df)} real news articles")
    print(f"  Sources: {', '.join(news_df['source'].unique())}")
    print(f"  Date range: {news_df['date'].min()} to {news_df['date'].max()}")
except Exception as e:
    print(f"[ERROR] Could not load news: {e}")
    sys.exit(1)

# Step 2: Load price data (already fetched)
print("\nSTEP 2: Loading S&P 500 price data...")
try:
    price_df = pd.read_csv('data/raw/price_data.csv')
    print(f"[OK] Loaded {len(price_df)} days of price data")
except Exception as e:
    print(f"[ERROR] Could not load prices: {e}")
    print("  Run: python run_simple.py first to fetch price data")
    sys.exit(1)

# Step 3: Preprocess news text
print("\nSTEP 3: Preprocessing news text...")
cleaner = TextCleaner()
cleaned_news = cleaner.preprocess_for_sentiment(news_df)
print(f"[OK] Preprocessed {len(cleaned_news)} articles")

# Step 4: Analyze sentiment with VADER
print("\nSTEP 4: Analyzing sentiment with VADER...")
analyzer = SentimentAnalyzer()

# Analyze each article
sentiment_df = analyzer.analyze_dataframe(
    cleaned_news,
    text_column='full_text',
    method='vader'  # Using VADER (transformers not installed)
)

print(f"[OK] Analyzed sentiment for {len(sentiment_df)} articles")

# Show sample sentiments
print("\nSample Sentiment Scores:")
for idx in range(min(5, len(sentiment_df))):
    article = sentiment_df.iloc[idx]
    print(f"  [{article['source']}] {article['title'][:50]}...")
    print(f"    Sentiment: {article['sentiment_compound']:.3f} ({article['sentiment_label']})")

# Step 5: Aggregate daily sentiment
print("\nSTEP 5: Aggregating daily sentiment...")
daily_sentiment = analyzer.aggregate_daily_sentiment(sentiment_df)
print(f"[OK] Created daily sentiment for {len(daily_sentiment)} days")

# Save sentiment data
sentiment_df.to_csv('data/processed/sentiment_articles_real.csv', index=False)
daily_sentiment.to_csv('data/processed/sentiment_daily_real.csv', index=False)
print("  Saved: data/processed/sentiment_articles_real.csv")
print("  Saved: data/processed/sentiment_daily_real.csv")

# Step 6: Engineer features
print("\nSTEP 6: Engineering features with real sentiment...")
engineer = FeatureEngineer()
features_df = engineer.create_all_features(daily_sentiment, price_df)

if features_df.empty:
    print("[ERROR] Failed to create features")
    sys.exit(1)

engineer.save_features(features_df, filename='features_real_news.csv')
print(f"[OK] Created {len(features_df)} samples with {len(features_df.columns)} features")
print("  Saved: data/features/features_real_news.csv")

# Check target distribution
target_dist = features_df['target'].value_counts()
print(f"\nTarget distribution:")
print(f"  Down (0): {target_dist.get(0, 0)} ({target_dist.get(0, 0)/len(features_df)*100:.1f}%)")
print(f"  Up (1): {target_dist.get(1, 0)} ({target_dist.get(1, 0)/len(features_df)*100:.1f}%)")

# Step 7: Train model with real sentiment
print("\nSTEP 7: Training model with REAL news sentiment...")
trainer = ModelTrainer()

feature_cols = engineer.select_feature_columns(features_df)
print(f"  Using {len(feature_cols)} features")

X_train, X_test, y_train, y_test = trainer.prepare_data(
    features_df, feature_cols, target_col='target'
)

trainer.train(X_train, y_train)
metrics = trainer.evaluate_classification(X_test, y_test)

# Step 8: Feature importance
print("\nSTEP 8: Analyzing feature importance...")
feat_importance = trainer.get_feature_importance(top_n=15)

# Step 9: Save model
model_name = f"sp500_real_news_{datetime.now().strftime('%Y%m%d')}"
trainer.save_model(model_name)

# Step 10: Make prediction
print("\nSTEP 9: Making prediction with REAL news sentiment...")
predictor = Predictor(model_name=model_name)

latest_features = features_df.tail(1)
prediction = predictor.predict_next_day(latest_features)

# Compare with synthetic sentiment
print("\n" + "="*70)
print("COMPARISON: Real News vs Synthetic Sentiment")
print("="*70)

try:
    # Load old results
    old_features = pd.read_csv('data/features/features.csv')
    print(f"\nSynthetic Sentiment:")
    print(f"  Samples: {len(old_features)}")
    print(f"  Model: sp500_simple_20251113")
    print(f"  Accuracy: 51.76%")

    print(f"\nReal News Sentiment:")
    print(f"  Samples: {len(features_df)}")
    print(f"  Model: {model_name}")
    print(f"  Accuracy: {metrics['accuracy']:.2%}")

    improvement = (metrics['accuracy'] - 0.5176) * 100
    if improvement > 0:
        print(f"\n  Improvement: +{improvement:.2f} percentage points!")
    else:
        print(f"\n  Change: {improvement:.2f} percentage points")

except:
    pass

# Summary
print("\n" + "="*70)
print("PIPELINE COMPLETED WITH REAL NEWS!")
print("="*70)
print(f"\n[MODEL PERFORMANCE - REAL NEWS]")
print(f"   Accuracy:  {metrics['accuracy']:.2%}")
print(f"   Precision: {metrics['precision']:.2%}")
print(f"   Recall:    {metrics['recall']:.2%}")
print(f"   F1 Score:  {metrics['f1_score']:.2%}")
print(f"   AUC-ROC:   {metrics['auc_roc']:.2%}")

print(f"\n[PREDICTION - WITH REAL NEWS]")
print(f"   Direction: {prediction.get('direction', 'N/A')}")
print(f"   Confidence: {prediction.get('confidence', 0):.2%}")
print(f"   Prob Up:   {prediction.get('probability_up', 0):.2%}")
print(f"   Prob Down: {prediction.get('probability_down', 0):.2%}")

print(f"\n[NEWS STATISTICS]")
print(f"   Total Articles: {len(news_df)}")
print(f"   Avg Sentiment: {sentiment_df['sentiment_compound'].mean():.3f}")
print(f"   Positive Articles: {(sentiment_df['sentiment_label'] == 'positive').sum()}")
print(f"   Negative Articles: {(sentiment_df['sentiment_label'] == 'negative').sum()}")
print(f"   Neutral Articles: {(sentiment_df['sentiment_label'] == 'neutral').sum()}")

print(f"\n[SAVED FILES]")
print(f"   Model: models/{model_name}.pkl")
print(f"   Features: data/features/features_real_news.csv")
print(f"   Sentiment: data/processed/sentiment_articles_real.csv")

print("\n" + "="*70)
print("SUCCESS! Your model now uses REAL news sentiment!")
print("="*70 + "\n")
