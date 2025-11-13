# 🚀 S&P 500 AI Prediction Dashboard

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-orange.svg)](https://xgboost.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive, production-ready machine learning system for predicting S&P 500 market movements with an interactive web dashboard featuring advanced analytics, backtesting, and Monte Carlo simulations.

---

## ✨ Features

### 🤖 Machine Learning
- **XGBoost Classifier** with 91 technical and sentiment features
- **Multiple Model Variants**: Simple, Economic Data, News Sentiment, Complete
- **Real-time Predictions** with confidence scores
- **Model Ensemble System** for improved accuracy
- **Automated Retraining** capabilities

### 📊 Interactive Dashboard
- **Professional UI** with glassmorphism design
- **Dark/Light Theme** toggle
- **Real-time Data** with auto-refresh (customizable intervals)
- **Interactive Candlestick Chart** with ApexCharts
- **Live Market Status** with countdown timers
- **PDF Export** for comprehensive reports

### 📈 Advanced Analytics
- **Backtesting Simulator** with multiple strategies:
  - Simple (Fixed Position Size)
  - Confidence-Based Position Sizing
  - Kelly Criterion Optimization
  - Martingale Strategy
- **Monte Carlo Simulation** with 1000+ paths
- **Scenario Analysis** (Bull/Base/Bear cases)
- **Risk Metrics**: Sharpe Ratio, Max Drawdown, VaR, CVaR
- **Performance Metrics**: Win Rate, Profit Factor, Equity Curve

### 🧠 AI Explanation
- **Feature Importance** visualization
- **Prediction Explanations** showing top contributing factors
- **Bullish/Bearish** indicator for each feature

### 📅 Economic Calendar
- **Dynamic Event Generation** based on realistic schedules
- **FOMC Meetings, CPI Reports, Jobs Data**, GDP, Retail Sales
- **Impact Classification** (High/Medium/Low)
- **Automatic Date Calculation** with business day adjustments

### 📉 Technical Indicators
- Price History with SMA 20/50
- Bollinger Bands
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Volume Analysis

---

## 🏗️ Architecture

```
S&P-500-Price-Prediction/
├── app.py                          # Flask application
├── Dockerfile                      # Docker container configuration
├── docker-compose.yml             # Docker Compose orchestration
├── requirements.txt               # Python dependencies
├── requirements_production.txt    # Production dependencies
│
├── src/
│   ├── data_collection/          # Data fetching modules
│   │   ├── price_fetcher.py      # S&P 500 price data
│   │   ├── news_scraper.py       # News article scraping
│   │   └── economic_data.py      # Economic indicators
│   │
│   ├── preprocessing/            # Data preprocessing
│   │   └── text_cleaner.py      # Text cleaning utilities
│   │
│   ├── features/                # Feature engineering
│   │   ├── feature_engineer.py  # Technical indicators
│   │   └── sentiment_analyzer.py # NLP sentiment analysis
│   │
│   ├── models/                  # ML models
│   │   ├── train.py            # Model training
│   │   ├── predict.py          # Prediction logic
│   │   ├── backtester.py       # Backtesting engine
│   │   └── monte_carlo.py      # Monte Carlo simulator
│   │
│   └── utils/                  # Utility functions
│       └── helpers.py
│
├── templates/                  # HTML templates
│   ├── dashboard.html         # Main dashboard
│   └── report.html            # Project report
│
├── static/                    # Static assets
│   ├── css/
│   │   └── style.css         # Custom styles
│   ├── js/
│   │   └── dashboard.js      # Dashboard logic
│   └── images/               # Charts and visuals
│
├── data/                     # Data storage
│   ├── raw/                 # Raw data
│   ├── processed/           # Processed data
│   └── features/            # Feature datasets
│
└── models/                  # Trained models
    └── sp500_complete_*.pkl
```

---

## 🚀 Quick Start

### Option 1: Local Installation

#### Prerequisites
- Python 3.11 or higher
- pip package manager
- 4GB+ RAM recommended

#### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/lkiwan/S-P-500-Price-Prediction.git
cd S-P-500-Price-Prediction
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements_dashboard.txt
```

3. **Run the dashboard**
```bash
python app.py
```

4. **Access the dashboard**
Open your browser and navigate to: `http://localhost:5000`

### Option 2: Docker Deployment (Recommended for Production)

#### Prerequisites
- Docker 20.10+ and Docker Compose
- 2GB+ free disk space

#### Deployment Steps

1. **Clone the repository**
```bash
git clone https://github.com/lkiwan/S-P-500-Price-Prediction.git
cd S-P-500-Price-Prediction
```

2. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

3. **Check container status**
```bash
docker-compose ps
docker-compose logs -f
```

4. **Access the dashboard**
Navigate to: `http://localhost:5000`

5. **Stop the containers**
```bash
docker-compose down
```

---

## 📚 Usage Guide

### Dashboard Navigation

#### Main Sections

1. **Prediction Panel** (Top)
   - Latest prediction with confidence score
   - UP/DOWN direction indicator
   - Market status with live countdown
   - "Get Prediction" and "Export PDF" buttons

2. **Interactive Candlestick Chart**
   - Last 90/60/30 days of price data
   - Interactive zoom and pan
   - OHLC tooltips
   - Period selector buttons

3. **Analytics Grid**
   - Performance metrics (accuracy, Sharpe ratio)
   - Feature importance chart
   - Trading simulation results
   - Rolling accuracy statistics

4. **Market Intelligence**
   - Economic indicators (Fed Rate, CPI, VIX)
   - Technical indicators chart
   - Recent news sentiment analysis
   - Upcoming economic calendar

5. **Advanced Analytics**
   - Confusion matrix
   - Risk metrics (max drawdown, streaks)
   - Best/worst predictions
   - AI explanation module

### Key Features Usage

#### 🔄 Auto-Refresh
- Click the sync icon in the navbar
- Toggle between "Auto" (60s refresh) and "Off"
- Preference is saved in browser localStorage

#### 🌓 Dark/Light Theme
- Click the moon/sun icon in navbar
- Theme persists across sessions
- Smooth transitions between themes

#### 📄 PDF Export
- Click "Export PDF" button
- Generates comprehensive report with:
  - Latest prediction details
  - Accuracy statistics by confidence level
  - Recent predictions table
  - Model information

#### 📊 Interactive Charts
- **Hover** to see detailed tooltips
- **Zoom** by dragging on chart
- **Pan** by holding Shift + drag
- **Reset** using toolbar buttons

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file for production:

```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///data/predictions.db
LOG_LEVEL=INFO
```

### Model Configuration

Edit `config.yaml` to customize:

```yaml
model:
  name: "sp500_complete"
  features: 91
  lookback_days: 60

training:
  test_size: 0.2
  random_state: 42
  n_estimators: 200
  max_depth: 7

prediction:
  confidence_threshold: 0.60
  auto_retrain_days: 30
```

---

## 🧪 API Documentation

### Prediction Endpoints

#### Get Latest Prediction
```
GET /api/latest_prediction
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "date": "2024-11-14",
    "direction": "UP",
    "confidence": 0.73,
    "prob_up": 0.73,
    "prob_down": 0.27
  }
}
```

#### Run New Prediction
```
POST /api/run_prediction
```

**Response:**
```json
{
  "success": true,
  "message": "Prediction completed successfully"
}
```

### Analytics Endpoints

#### Backtest Strategies
```
GET /api/backtest_strategies
```

**Response:**
```json
{
  "success": true,
  "strategies": {
    "Simple (50%)": {
      "total_return_pct": 15.3,
      "sharpe_ratio": 1.42,
      "max_drawdown_pct": -8.5,
      "win_rate_pct": 58.2
    }
  }
}
```

#### Monte Carlo Simulation
```
GET /api/monte_carlo?days=30&simulations=1000
```

**Response:**
```json
{
  "success": true,
  "current_price": 4500.00,
  "prob_profit_pct": 54.2,
  "expected_return_pct": 2.3,
  "var_95_pct": -5.8
}
```

#### Feature Importance
```
GET /api/feature_importance
```

**Response:**
```json
{
  "success": true,
  "features": [
    {
      "name": "RSI_14",
      "importance": 0.124
    }
  ]
}
```

For complete API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## 📊 Model Performance

### Current Accuracy Metrics

| Metric | Value |
|--------|-------|
| Overall Accuracy | 58.5% |
| High Confidence (>70%) | 67.2% |
| Sharpe Ratio | 1.38 |
| Max Drawdown | -12.4% |
| Win Rate | 58.5% |
| Profit Factor | 1.42 |

### Feature Importance (Top 10)

1. RSI_14 (12.4%)
2. MACD_Signal (10.8%)
3. Bollinger_Upper_Distance (9.3%)
4. SMA_20_50_Cross (8.7%)
5. Volume_Ratio (7.5%)
6. Sentiment_Score (6.9%)
7. VIX_Close (6.2%)
8. Fed_Rate_Change (5.8%)
9. MACD_Histogram (5.4%)
10. Price_vs_SMA50 (5.1%)

---

## 🛡️ Security

### Implemented Security Measures

- **HTTPS** ready (configure reverse proxy)
- **CORS** protection
- **SQL Injection** prevention (parameterized queries)
- **XSS** protection in templates
- **CSRF** tokens for forms
- **Rate Limiting** on API endpoints
- **Input Validation** on all user inputs

### Recommended Production Setup

1. **Use HTTPS** with SSL certificates
2. **Set strong SECRET_KEY** in environment variables
3. **Enable Flask-Talisman** for security headers
4. **Configure rate limiting** per endpoint
5. **Regular security audits**
6. **Keep dependencies updated**

---

## 📈 Performance Optimization

### Current Optimizations

- **Caching** of prediction results
- **Lazy loading** of large datasets
- **Pagination** for historical data
- **Minified** CSS and JavaScript
- **Compressed** static assets
- **Database indexing** on date columns

### Recommended Enhancements

- Redis caching for API responses
- CDN for static assets
- Database connection pooling
- Asynchronous task queue (Celery)
- Load balancing for multiple instances

---

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/
```

### Run with Coverage
```bash
pytest --cov=src tests/
```

### Load Testing
```bash
locust -f tests/locustfile.py
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

**IMPORTANT:** This system is for educational and research purposes only.

- Past performance does not guarantee future results
- Trading involves substantial risk of loss
- Always conduct your own research
- Consult with a licensed financial advisor
- Not financial advice

---

## 📧 Contact & Support

- **GitHub**: [github.com/lkiwan/S-P-500-Price-Prediction](https://github.com/lkiwan/S-P-500-Price-Prediction)
- **Issues**: [Report a bug](https://github.com/lkiwan/S-P-500-Price-Prediction/issues)
- **Discussions**: [Join the conversation](https://github.com/lkiwan/S-P-500-Price-Prediction/discussions)

---

## 🙏 Acknowledgments

- XGBoost team for the excellent ML framework
- Flask community for the web framework
- Chart.js and ApexCharts for visualization libraries
- Yahoo Finance for market data
- All contributors and supporters

---

**Made with ❤️ by Omar**
