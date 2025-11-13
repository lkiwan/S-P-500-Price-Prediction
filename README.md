# S&P 500 Price Prediction Using News Sentiment Analysis

A complete machine learning pipeline that predicts S&P 500 price movements using financial news sentiment analysis and technical indicators.

## Overview

This project combines:
- **News Sentiment Analysis**: Using FinBERT (financial domain BERT) to analyze market sentiment from news articles
- **Technical Indicators**: RSI, MACD, Moving Averages, Bollinger Bands, etc.
- **Machine Learning**: XGBoost, LightGBM, and Random Forest models
- **Feature Engineering**: Lag features, rolling statistics, and interaction terms

**Goal**: Predict next-day S&P 500 market direction (UP/DOWN) with high accuracy.

## Project Structure

```
S&P_USA/
├── data/
│   ├── raw/              # Raw news and price data
│   ├── processed/        # Cleaned and processed data
│   └── features/         # Engineered features
├── src/
│   ├── data_collection/
│   │   ├── news_scraper.py      # Scrape news from multiple sources
│   │   └── price_fetcher.py     # Download S&P 500 price data
│   ├── preprocessing/
│   │   └── text_cleaner.py      # Clean and preprocess news text
│   ├── features/
│   │   ├── sentiment_analyzer.py    # FinBERT sentiment analysis
│   │   └── feature_engineer.py      # Create ML features
│   ├── models/
│   │   ├── train.py             # Train ML models
│   │   └── predict.py           # Make predictions
│   └── utils/
│       └── helpers.py           # Visualization and utilities
├── models/               # Saved trained models
├── notebooks/           # Jupyter notebooks for exploration
├── main.py             # Main pipeline script
├── config.yaml         # Configuration file
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download this project**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Download NLTK data** (required for text processing):
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

4. **Configure NewsAPI** (optional, for live news scraping):
   - Get a free API key from [newsapi.org](https://newsapi.org)
   - Edit `config.yaml` and add your key:
   ```yaml
   news:
     newsapi_key: "YOUR_API_KEY_HERE"
   ```

## Quick Start

### Run Complete Pipeline

```bash
python main.py
```

This will:
1. Collect news and price data
2. Preprocess and clean text
3. Analyze sentiment with FinBERT
4. Engineer features
5. Train ML model
6. Make predictions
7. Generate visualizations

### Run with Custom Settings

```bash
# Collect 180 days of historical data
python main.py --days 180

# Use existing data (skip data collection)
python main.py --skip-data
```

## Usage Examples

### 1. Collect Data

```python
from src.data_collection.news_scraper import NewsScraper
from src.data_collection.price_fetcher import PriceFetcher

# Scrape news
scraper = NewsScraper()
news_df = scraper.scrape_all(days_back=90)
scraper.save_news(news_df)

# Fetch S&P 500 prices
fetcher = PriceFetcher()
price_df = fetcher.get_full_dataset()
fetcher.save_prices(price_df)
```

### 2. Analyze Sentiment

```python
from src.features.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Analyze single text
text = "S&P 500 surges to record high as tech stocks rally!"
sentiment = analyzer.analyze_text(text, method='finbert')
print(f"Sentiment: {sentiment['compound']:.3f}")

# Analyze dataframe of news
sentiment_df = analyzer.analyze_dataframe(news_df)
daily_sentiment = analyzer.aggregate_daily_sentiment(sentiment_df)
```

### 3. Train Model

```python
from src.models.train import ModelTrainer
from src.features.feature_engineer import FeatureEngineer

# Engineer features
engineer = FeatureEngineer()
features_df = engineer.create_all_features(daily_sentiment, price_df)

# Train model
trainer = ModelTrainer()
feature_cols = engineer.select_feature_columns(features_df)
X_train, X_test, y_train, y_test = trainer.prepare_data(features_df, feature_cols)

trainer.train(X_train, y_train)
metrics = trainer.evaluate_classification(X_test, y_test)

# Save model
trainer.save_model("my_model")
```

### 4. Make Predictions

```python
from src.models.predict import Predictor

# Load trained model
predictor = Predictor(model_name="my_model")

# Predict next day
latest_features = features_df.tail(1)
prediction = predictor.predict_next_day(latest_features)

print(f"Prediction: {prediction['direction']}")
print(f"Confidence: {prediction['confidence']:.2%}")
```

## Configuration

Edit `config.yaml` to customize:

- **Data settings**: Date ranges, train/test split
- **News sources**: Which sources to scrape
- **Sentiment model**: FinBERT, VADER, or ensemble
- **Technical indicators**: Which indicators to include
- **Model parameters**: XGBoost, LightGBM, or Random Forest settings
- **Feature engineering**: Lag periods, rolling windows

## Features

### Sentiment Features
- Daily sentiment scores (positive, negative, neutral, compound)
- Sentiment momentum and trends
- Rolling averages of sentiment
- News volume and weighted sentiment

### Technical Features
- Price indicators: SMA, EMA, RSI, MACD
- Volatility: Bollinger Bands, ATR
- Volume indicators
- Price momentum

### Engineered Features
- Lag features (previous days' data)
- Rolling statistics
- Interaction terms between sentiment and technical indicators

## Model Performance

Expected performance metrics:
- **Accuracy**: 55-65% (significantly better than random 50%)
- **Precision**: 55-70%
- **Recall**: 50-65%
- **AUC-ROC**: 0.60-0.70

Note: Financial market prediction is inherently difficult. These results represent strong performance compared to random guessing.

## Data Sources

1. **News**:
   - NewsAPI (with free API key)
   - Finviz
   - Your own news file (all news.md)

2. **Price Data**:
   - Yahoo Finance (via yfinance library)
   - S&P 500 Index (^GSPC)

## Key Technologies

- **NLP**: Transformers (FinBERT), NLTK, VADER
- **ML**: XGBoost, LightGBM, Scikit-learn
- **Data**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn, Plotly

## Tips for Better Results

1. **More Data**: Collect more news articles for better sentiment signals
2. **Better Sources**: Use premium news sources (Bloomberg, Reuters)
3. **Feature Selection**: Remove weak features, add domain-specific features
4. **Ensemble Models**: Combine multiple models for robust predictions
5. **Regular Updates**: Retrain model regularly with new data
6. **Risk Management**: Use predictions as one signal among many

## Limitations

- Past performance doesn't guarantee future results
- News sentiment is just one factor affecting markets
- Model accuracy varies with market conditions
- Requires regular retraining to maintain performance

## Troubleshooting

### FinBERT Model Issues

If FinBERT fails to load:
```bash
# The model will automatically download on first use
# If you have network issues, it will fall back to VADER
```

### NewsAPI Errors

If NewsAPI returns errors:
- Check your API key in config.yaml
- Free tier has limited requests (100/day)
- Use `--skip-data` to use existing data

### Memory Issues

If running out of memory:
- Reduce batch size in config.yaml
- Process data in smaller chunks
- Use a machine with more RAM

## Future Enhancements

- [ ] Add more news sources (Twitter, Reddit)
- [ ] Implement LSTM/GRU for time series
- [ ] Add real-time prediction API
- [ ] Create web dashboard for visualization
- [ ] Add other market indicators (VIX, bonds, commodities)
- [ ] Multi-step ahead predictions
- [ ] Portfolio backtesting

## Contributing

Contributions are welcome! Areas for improvement:
- Additional data sources
- Better feature engineering
- Alternative ML models
- Improved visualizations
- Code optimization

## License

This project is for educational purposes. Use at your own risk. Not financial advice.

## Disclaimer

**⚠️ IMPORTANT**: This project is for educational and research purposes only. Do not use it for actual trading without thorough testing and risk management. Financial markets are complex and unpredictable. Past performance does not guarantee future results.

## Contact

For questions or feedback, please open an issue in the repository.

---

**Built with ❤️ for financial ML enthusiasts**

Happy Trading! 📈
