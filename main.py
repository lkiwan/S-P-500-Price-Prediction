"""
Main Pipeline Script
Complete end-to-end pipeline for S&P 500 price prediction
"""

import sys
import os
sys.path.append('src')

from data_collection.news_scraper import NewsScraper
from data_collection.price_fetcher import PriceFetcher
from preprocessing.text_cleaner import TextCleaner
from features.sentiment_analyzer import SentimentAnalyzer
from features.feature_engineer import FeatureEngineer
from models.train import ModelTrainer
from models.predict import Predictor
from utils.helpers import (
    plot_sentiment_over_time,
    plot_price_and_sentiment,
    plot_feature_importance,
    create_data_report
)

import pandas as pd
import argparse
from datetime import datetime


def collect_data(days_back: int = 90):
    """Step 1: Collect news and price data"""
    print("\n" + "="*70)
    print("STEP 1: DATA COLLECTION")
    print("="*70)

    # Scrape news
    print("\nCollecting news data...")
    scraper = NewsScraper()
    news_df = scraper.scrape_all(days_back=days_back)

    if not news_df.empty:
        scraper.save_news()

    # Fetch prices
    print("\nFetching price data...")
    fetcher = PriceFetcher()
    price_df = fetcher.get_full_dataset()

    if not price_df.empty:
        fetcher.save_prices()

    return news_df, price_df


def preprocess_data(news_df: pd.DataFrame):
    """Step 2: Preprocess text data"""
    print("\n" + "="*70)
    print("STEP 2: TEXT PREPROCESSING")
    print("="*70)

    cleaner = TextCleaner()
    cleaned_df = cleaner.preprocess_for_sentiment(news_df)

    return cleaned_df


def analyze_sentiment(cleaned_news_df: pd.DataFrame):
    """Step 3: Analyze sentiment"""
    print("\n" + "="*70)
    print("STEP 3: SENTIMENT ANALYSIS")
    print("="*70)

    analyzer = SentimentAnalyzer()

    # Analyze sentiment for each article
    sentiment_df = analyzer.analyze_dataframe(cleaned_news_df, method='finbert')

    # Aggregate daily sentiment
    daily_sentiment = analyzer.aggregate_daily_sentiment(sentiment_df)

    # Save results
    sentiment_df.to_csv('data/processed/sentiment_articles.csv', index=False)
    daily_sentiment.to_csv('data/processed/sentiment_daily.csv', index=False)

    print(f"\nSentiment analysis complete: {len(sentiment_df)} articles analyzed")

    return sentiment_df, daily_sentiment


def engineer_features(daily_sentiment: pd.DataFrame, price_df: pd.DataFrame):
    """Step 4: Engineer features"""
    print("\n" + "="*70)
    print("STEP 4: FEATURE ENGINEERING")
    print("="*70)

    engineer = FeatureEngineer()

    # Create all features
    features_df = engineer.create_all_features(daily_sentiment, price_df)

    # Save features
    engineer.save_features()

    print(f"\nFeature engineering complete: {len(features_df)} samples, {len(features_df.columns)} features")

    return features_df


def train_model(features_df: pd.DataFrame):
    """Step 5: Train ML model"""
    print("\n" + "="*70)
    print("STEP 5: MODEL TRAINING")
    print("="*70)

    trainer = ModelTrainer()

    # Get feature columns
    engineer = FeatureEngineer()
    feature_cols = engineer.select_feature_columns(features_df)

    # Prepare data
    X_train, X_test, y_train, y_test = trainer.prepare_data(
        features_df, feature_cols, target_col='target'
    )

    # Train model
    trainer.train(X_train, y_train)

    # Evaluate
    metrics = trainer.evaluate_classification(X_test, y_test)

    # Feature importance
    feat_importance = trainer.get_feature_importance(top_n=20)

    # Save model
    model_name = f"sp500_model_{datetime.now().strftime('%Y%m%d')}"
    trainer.save_model(model_name)

    return trainer, metrics, feat_importance, model_name


def make_predictions(model_name: str, features_df: pd.DataFrame):
    """Step 6: Make predictions"""
    print("\n" + "="*70)
    print("STEP 6: MAKING PREDICTIONS")
    print("="*70)

    predictor = Predictor(model_name=model_name)

    # Get latest data for prediction
    latest_features = features_df.tail(1)

    # Predict next day
    result = predictor.predict_next_day(latest_features)

    return result


def create_visualizations(sentiment_df: pd.DataFrame,
                         daily_sentiment: pd.DataFrame,
                         price_df: pd.DataFrame,
                         features_df: pd.DataFrame,
                         feat_importance: pd.DataFrame):
    """Create visualizations"""
    print("\n" + "="*70)
    print("CREATING VISUALIZATIONS")
    print("="*70)

    # Merge price and sentiment for plotting
    price_df['date'] = pd.to_datetime(price_df['date'])
    daily_sentiment['date'] = pd.to_datetime(daily_sentiment['date'])
    combined = pd.merge(price_df, daily_sentiment, on='date', how='inner')

    # Plot sentiment over time
    print("Creating sentiment plot...")
    plot_sentiment_over_time(daily_sentiment, save_path='sentiment_over_time.png')

    # Plot price and sentiment
    print("Creating price vs sentiment plot...")
    plot_price_and_sentiment(combined, save_path='price_vs_sentiment.png')

    # Plot feature importance
    print("Creating feature importance plot...")
    plot_feature_importance(feat_importance, save_path='feature_importance.png')

    print("\nVisualizations saved!")


def run_full_pipeline(days_back: int = 90, skip_data_collection: bool = False):
    """Run the complete pipeline"""
    print("\n" + "="*70)
    print("S&P 500 PRICE PREDICTION - FULL PIPELINE")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Step 1: Collect data
        if not skip_data_collection:
            news_df, price_df = collect_data(days_back)
        else:
            print("\nSkipping data collection, loading existing data...")
            news_df = pd.read_csv('data/raw/news_data.csv')
            price_df = pd.read_csv('data/raw/price_data.csv')

        # Step 2: Preprocess
        cleaned_news = preprocess_data(news_df)

        # Step 3: Analyze sentiment
        sentiment_df, daily_sentiment = analyze_sentiment(cleaned_news)

        # Step 4: Engineer features
        features_df = engineer_features(daily_sentiment, price_df)

        # Step 5: Train model
        trainer, metrics, feat_importance, model_name = train_model(features_df)

        # Step 6: Make predictions
        prediction = make_predictions(model_name, features_df)

        # Create visualizations
        create_visualizations(sentiment_df, daily_sentiment, price_df,
                            features_df, feat_importance)

        # Create data report
        create_data_report(news_df, price_df, daily_sentiment, features_df)

        print("\n" + "="*70)
        print("PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nModel Accuracy: {metrics['accuracy']:.2%}")
        print(f"Next Day Prediction: {prediction.get('direction', 'N/A')}")
        print(f"Confidence: {prediction.get('confidence', 0):.2%}")
        print("\nAll results saved to respective directories.")

    except Exception as e:
        print(f"\n❌ Error in pipeline: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='S&P 500 Price Prediction Pipeline')
    parser.add_argument('--days', type=int, default=90,
                       help='Number of days of historical data to collect')
    parser.add_argument('--skip-data', action='store_true',
                       help='Skip data collection and use existing data')

    args = parser.parse_args()

    run_full_pipeline(days_back=args.days, skip_data_collection=args.skip_data)
