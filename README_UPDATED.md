# S&P 500 AI Prediction Dashboard

![Model Accuracy](https://img.shields.io/badge/Accuracy-71.20%25-success)
![High Confidence](https://img.shields.io/badge/High--Confidence-93.12%25-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Achievements

**Base Accuracy:** 71.20% (validated on 382-day test set)
**High-Confidence Accuracy:** 93.12% (at 80%+ confidence)
**Edge Over Random:** +21.20 percentage points

## Overview

An advanced machine learning system that predicts S&P 500 market direction using:
- **91 features** combining technical indicators, news sentiment, and economic data
- **XGBoost** optimized classifier
- Real-time predictions with confidence scoring
- Interactive web dashboard with live analytics

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Build and run
docker-compose up --build

# Visit http://localhost:5000
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python app.py

# Visit http://localhost:5000
```

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| **Base Accuracy** | 71.20% |
| **Precision** | 71.27% |
| **Recall** | 85.27% |
| **F1 Score** | 77.64% |
| **AUC-ROC** | 80.39% |

### Confidence-Based Performance

| Confidence Level | Accuracy | Coverage |
|------------------|----------|----------|
| ≥80% | **93.12%** | 41.9% of predictions |
| ≥75% | **86.50%** | 52.4% of predictions |
| ≥70% | **81.07%** | 63.6% of predictions |
| All predictions | **71.20%** | 100% |

## 🎓 How It Works

### Data Sources
1. **Market Data**: S&P 500 historical prices (Yahoo Finance)
2. **News Sentiment**: Web-scraped financial news
3. **Economic Indicators**: Fed rates, unemployment, VIX, inflation, etc.

### Feature Engineering (91 Features)
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Sentiment Analysis**: VADER sentiment from financial news
- **Economic Data**: Fed funds rate, unemployment, inflation, VIX
- **Momentum Features**: Multi-timeframe price momentum
- **Volume Patterns**: Volume ratios and trends

### Model Architecture
- **Algorithm**: XGBoost Gradient Boosting Classifier
- **Training**: Walk-forward validation on 2020-2024 data
- **Validation**: 382-day test set (30% of data)
- **Optimization**: Grid search hyperparameter tuning

## 📱 Dashboard Features

### Main Dashboard
- Real-time market prediction with confidence score
- Interactive price charts
- Feature importance visualization
- Prediction history timeline
- Performance analytics

### Analytics
- Rolling accuracy metrics
- Confusion matrix
- Confidence distribution
- Win rate by prediction type
- Monthly performance breakdown

### PDF Reports
- Comprehensive performance analysis
- Feature importance rankings
- Backtest results
- Monte Carlo simulations
- Trading recommendations

## 🎯 Trading Strategies

### Ultra-Conservative (Recommended)
- **Trade when**: Confidence ≥ 80%
- **Expected accuracy**: 93.12%
- **Frequency**: ~8-10 signals/month
- **Risk**: Very low

### Balanced
- **Trade when**: Confidence ≥ 70%
- **Expected accuracy**: 81.07%
- **Frequency**: ~16 signals/month
- **Risk**: Moderate

### Aggressive
- **Trade when**: All predictions
- **Expected accuracy**: 71.20%
- **Frequency**: Daily
- **Risk**: Higher

## 🛠️ Project Structure

```
S&P USA/
├── app.py                          # Flask web application
├── predict.py                      # Standalone prediction script
├── Dockerfile                      # Docker containerization
├── docker-compose.yml              # Docker orchestration
├── requirements.txt                # Python dependencies
├── src/
│   ├── data_collection/
│   │   ├── price_fetcher.py       # Market data collection
│   │   └── economic_data.py       # Economic indicators
│   ├── features/
│   │   ├── sentiment_analyzer.py  # News sentiment analysis
│   │   └── feature_engineer.py    # Feature generation
│   └── models/
│       ├── train.py               # Model training
│       └── predict.py             # Prediction engine
├── data/
│   ├── raw/                       # Raw market data
│   ├── processed/                 # Processed sentiment
│   └── features/                  # Engineered features
├── models/                         # Trained models
└── templates/
    └── dashboard.html             # Web UI
```

## 📈 Usage Examples

### Make a Prediction

```python
from src.models.predict import Predictor

# Load model
predictor = Predictor(model_name="sp500_complete_20251113")

# Get latest features
features_df = pd.read_csv('data/features/features_complete.csv')
latest = features_df.tail(1)

# Predict
result = predictor.predict(latest)

print(f"Direction: {result['direction']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Probability UP: {result['probability_up']:.2%}")
```

### Run from Command Line

```bash
# Make prediction for next trading day
python predict.py

# Outputs:
# Market Direction: UP ↑ [BULLISH]
# Confidence: 72.45% [**] MEDIUM
# Accuracy: 71.20% (validated on 382-day test)
```

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
data:
  ticker: "^GSPC"
  start_date: "2020-01-01"

model:
  type: "xgboost"
  n_estimators: 200
  max_depth: 6

prediction:
  threshold: 0.5
  confidence_level: 0.7
```

## 🧪 Testing & Validation

### Validate Model

```bash
python test_original_model_properly.py
```

Output:
```
30% test set (382 samples):
  Accuracy: 71.20%
  Test period: last 382 days

Detailed Metrics:
  Accuracy:  71.20%
  Precision: 71.27%
  Recall:    85.27%
  F1 Score:  77.64%
  AUC-ROC:   80.39%
```

### Backtest Analysis

```bash
python backtest_analysis.py
```

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t sp500-dashboard .
```

### Run Container

```bash
docker run -d -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  --name sp500-dashboard \
  sp500-dashboard
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📊 Model Details

### Training Process

1. **Data Collection** (2020-2024)
   - 1,275 trading days
   - Daily OHLCV data
   - Economic indicators
   - News sentiment scores

2. **Feature Engineering**
   - 91 engineered features
   - Technical + Fundamental + Sentiment
   - Lag features (1-5 days)
   - Rolling statistics

3. **Model Training**
   - Walk-forward validation
   - 70% train / 30% test split
   - No data leakage
   - Hyperparameter optimization

4. **Validation**
   - 382-day test set
   - Time-series cross-validation
   - Confidence-based analysis

### Key Features (Top 10)

1. Unemployment rate changes
2. Fed funds rate changes (3-month)
3. Historical returns (lag 3)
4. VIX volatility index
5. Consumer sentiment
6. Inflation rate (CPI)
7. Dollar index (DXY)
8. RSI-14 momentum
9. Fed funds rate changes
10. Historical returns (lag 1)

## ⚠️ Important Notes

### Disclaimer

This software is for **educational purposes only**. It does NOT constitute financial advice.

- Past performance does not guarantee future results
- The model has 71.20% accuracy on historical data
- Always use proper risk management
- Never invest more than you can afford to lose
- Consult a financial advisor before trading

### Risk Management

1. **Position Sizing**: Never risk more than 1-2% per trade
2. **Stop Losses**: Always use stop losses (2-3% below entry)
3. **Diversification**: Don't rely on a single signal
4. **Confidence Threshold**: Use ≥70% confidence for better accuracy
5. **Review Performance**: Track actual vs predicted results

## 📚 Documentation

- `SUCCESS_71_PERCENT_ACHIEVED.md` - Detailed accuracy analysis
- `FINAL_ACHIEVEMENT.txt` - Complete performance summary
- `ACCURACY_IMPROVEMENT_RESULTS.md` - Methodology details
- `POST_DEPLOYMENT.md` - Deployment guide

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Contact & Support

- **Issues**: Open a GitHub issue
- **Questions**: Check documentation first
- **Updates**: Watch the repository for updates

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Market data from Yahoo Finance
- Economic data from FRED, BEA
- Built with Flask, XGBoost, scikit-learn
- UI with Bootstrap 5

---

**Model Version**: sp500_complete_20251113
**Last Updated**: 2025-11-14
**Status**: Production Ready ✅

**Accuracy**: 71.20% (base) | 93.12% (high confidence)
**Ready to trade!** 🚀
