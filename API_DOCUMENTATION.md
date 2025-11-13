# 📡 S&P 500 AI Prediction API Documentation

Complete API reference for the S&P 500 prediction system.

---

## Base URL

```
http://localhost:5000/api
```

For production: `https://your-domain.com/api`

---

## Authentication

Currently, the API does not require authentication. For production deployment, consider implementing:
- API Keys
- OAuth 2.0
- JWT tokens

---

## Endpoints

### 1. Predictions

#### Get Latest Prediction
Returns the most recent prediction made by the model.

**Endpoint:** `GET /api/latest_prediction`

**Response:**
```json
{
  "success": true,
  "prediction": {
    "prediction_date": "2024-11-14T10:30:00",
    "data_date": "2024-11-13",
    "direction": "UP",
    "confidence": 0.7342,
    "prob_up": 0.7342,
    "prob_down": 0.2658
  }
}
```

#### Get Prediction History
Returns historical predictions with pagination.

**Endpoint:** `GET /api/prediction_history`

**Response:**
```json
{
  "success": true,
  "predictions": [
    {
      "date": "2024-11-13",
      "direction": "UP",
      "confidence": 0.68
    }
  ],
  "stats": {
    "total": 150,
    "accuracy": 58.5
  }
}
```

#### Run New Prediction
Triggers a new prediction calculation.

**Endpoint:** `POST /api/run_prediction`

**Request Body:** None required

**Response:**
```json
{
  "success": true,
  "message": "Prediction completed successfully",
  "prediction": {
    "direction": "UP",
    "confidence": 0.72
  }
}
```

---

### 2. Performance Metrics

#### Get Overall Performance
Returns accuracy and performance statistics.

**Endpoint:** `GET /api/performance_metrics`

**Response:**
```json
{
  "success": true,
  "accuracy": 58.5,
  "correct_predictions": 88,
  "total_predictions": 150,
  "sharpe_ratio": 1.38,
  "max_drawdown": -12.4,
  "by_confidence": {
    "high": {"accuracy": 67.2, "count": 45},
    "medium": {"accuracy": 58.1, "count": 60},
    "low": {"accuracy": 42.2, "count": 45}
  }
}
```

#### Get Predictions with Accuracy
Returns predictions matched with actual outcomes.

**Endpoint:** `GET /api/predictions_with_accuracy`

**Response:**
```json
{
  "success": true,
  "predictions": [
    {
      "date": "2024-11-13",
      "predicted": "UP",
      "actual": "UP",
      "correct": true,
      "return": 1.23,
      "confidence": 0.72
    }
  ]
}
```

---

### 3. Analytics & Features

#### Get Feature Importance
Returns the top features influencing predictions.

**Endpoint:** `GET /api/feature_importance`

**Response:**
```json
{
  "success": true,
  "features": [
    {
      "name": "RSI_14",
      "importance": 0.124,
      "rank": 1
    },
    {
      "name": "MACD_Signal",
      "importance": 0.108,
      "rank": 2
    }
  ]
}
```

#### Get AI Explanation
Returns feature contributions for the latest prediction.

**Endpoint:** `GET /api/ai_explanation`

**Response:**
```json
{
  "success": true,
  "prediction": "UP",
  "features": [
    {
      "feature": "RSI 14",
      "contribution": 0.0523,
      "importance": 0.124,
      "value": 65.3,
      "direction": "bullish"
    }
  ]
}
```

---

### 4. Backtesting

#### Run Strategy Backtest
Tests multiple trading strategies against historical data.

**Endpoint:** `GET /api/backtest_strategies`

**Response:**
```json
{
  "success": true,
  "initial_capital": 10000,
  "strategies": {
    "Simple (50%)": {
      "total_return_pct": 15.3,
      "final_capital": 11530,
      "sharpe_ratio": 1.42,
      "max_drawdown_pct": -8.5,
      "win_rate_pct": 58.2,
      "profit_factor": 1.65,
      "total_trades": 145,
      "winning_trades": 84,
      "losing_trades": 61,
      "avg_win_pct": 2.1,
      "avg_loss_pct": -1.8,
      "equity_curve": [
        {"date": "2024-01-01", "capital": 10000, "return": 0},
        {"date": "2024-01-02", "capital": 10150, "return": 0.015}
      ]
    },
    "Confidence-Based": { ... },
    "Kelly Criterion": { ... }
  }
}
```

#### Get Trading Simulation
Returns simulated trading performance.

**Endpoint:** `GET /api/trading_simulation`

**Response:**
```json
{
  "success": true,
  "initial_capital": 10000,
  "final_capital": 11234,
  "total_return": 12.34,
  "sharpe_ratio": 1.45,
  "win_rate": 58.5,
  "trades": 150,
  "equity_curve": [ ... ]
}
```

---

### 5. Monte Carlo Simulation

#### Run Monte Carlo Simulation
Simulates future price paths using historical volatility.

**Endpoint:** `GET /api/monte_carlo?days=30&simulations=1000`

**Parameters:**
- `days` (optional): Number of days to simulate (default: 30)
- `simulations` (optional): Number of simulation paths (default: 1000)

**Response:**
```json
{
  "success": true,
  "current_price": 4500.00,
  "days": 30,
  "num_simulations": 1000,
  "final_price_stats": {
    "mean": 4565.23,
    "median": 4558.12,
    "std": 145.67,
    "min": 4123.45,
    "max": 4987.65
  },
  "percentiles": {
    "5th": 4320.15,
    "25th": 4456.78,
    "50th": 4558.12,
    "75th": 4678.90,
    "95th": 4812.34
  },
  "prob_profit_pct": 54.2,
  "expected_return_pct": 2.3,
  "var_95_pct": -5.8,
  "cvar_95_pct": -8.2,
  "daily_stats": [
    {
      "day": 0,
      "date": "2024-11-14",
      "mean": 4500.00,
      "median": 4500.00,
      "5th_percentile": 4500.00,
      "95th_percentile": 4500.00
    },
    {
      "day": 1,
      "date": "2024-11-15",
      "mean": 4505.23,
      "median": 4503.12,
      "5th_percentile": 4445.00,
      "95th_percentile": 4565.00
    }
  ],
  "sample_paths": [ ... ]
}
```

#### Run Scenario Analysis
Tests bull, base, and bear case scenarios.

**Endpoint:** `GET /api/monte_carlo_scenarios`

**Response:**
```json
{
  "success": true,
  "scenarios": {
    "Bull Case": {
      "current_price": 4500.00,
      "final_price_stats": { ... },
      "prob_profit_pct": 68.5,
      "expected_return_pct": 5.2
    },
    "Base Case": { ... },
    "Bear Case": { ... }
  }
}
```

---

### 6. Market Data

#### Get Market Status
Returns current market status and hours.

**Endpoint:** `GET /api/market_status`

**Response:**
```json
{
  "success": true,
  "status": "open",
  "current_price": 4567.89,
  "change": 23.45,
  "change_pct": 0.52,
  "volume": 3456789000,
  "timestamp": "2024-11-14T14:30:00",
  "next_event": "Market Close",
  "next_event_time": "16:00 ET"
}
```

#### Get Candlestick Data
Returns OHLC data for charts.

**Endpoint:** `GET /api/candlestick_data?days=90`

**Parameters:**
- `days` (optional): Number of days (default: 90)

**Response:**
```json
{
  "success": true,
  "candlestick": [
    {
      "x": "2024-11-14",
      "y": [4510.00, 4567.89, 4502.34, 4556.78]
    }
  ],
  "volume": [
    {
      "x": "2024-11-14",
      "y": 3456789000
    }
  ],
  "days": 90
}
```

---

### 7. Economic & Technical Data

#### Get Economic Indicators
Returns latest economic data (Fed Rate, CPI, unemployment, etc.).

**Endpoint:** `GET /api/economic_indicators`

**Response:**
```json
{
  "success": true,
  "indicators": {
    "fed_rate": {"value": 5.25, "change": 0.25, "date": "2024-11-01"},
    "unemployment": {"value": 3.8, "change": -0.1, "date": "2024-11-01"},
    "cpi": {"value": 3.2, "change": -0.1, "date": "2024-11-01"},
    "vix": {"value": 15.3, "change": 1.2, "date": "2024-11-14"}
  }
}
```

#### Get Technical Indicators
Returns 60 days of technical analysis data.

**Endpoint:** `GET /api/technical_indicators`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-11-14",
      "price": 4567.89,
      "sma_20": 4534.56,
      "sma_50": 4512.34,
      "bb_upper": 4598.23,
      "bb_lower": 4470.89,
      "rsi": 65.3,
      "macd": 12.45,
      "signal": 10.23
    }
  ]
}
```

#### Get Economic Calendar
Returns upcoming economic events.

**Endpoint:** `GET /api/economic_calendar`

**Response:**
```json
{
  "success": true,
  "events": [
    {
      "title": "FOMC Meeting",
      "date": "Dec 18, 2024",
      "time": "2:00 PM ET",
      "impact": "High",
      "description": "Federal Reserve interest rate decision",
      "impact_class": "danger"
    }
  ]
}
```

---

### 8. Sentiment & News

#### Get Sentiment Data
Returns daily sentiment scores.

**Endpoint:** `GET /api/sentiment_data`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-11-14",
      "sentiment": 0.23,
      "article_count": 45
    }
  ]
}
```

#### Get Recent News
Returns last 10 days of news sentiment.

**Endpoint:** `GET /api/recent_news`

**Response:**
```json
{
  "success": true,
  "news": [
    {
      "date": "2024-11-14",
      "sentiment": 0.23,
      "category": "Positive",
      "article_count": 45
    }
  ]
}
```

---

### 9. Risk Metrics

#### Get Confusion Matrix
Returns classification performance matrix.

**Endpoint:** `GET /api/confusion_matrix`

**Response:**
```json
{
  "success": true,
  "matrix": {
    "true_positive": 52,
    "false_positive": 32,
    "true_negative": 48,
    "false_negative": 18
  },
  "metrics": {
    "accuracy": 66.67,
    "precision": 61.90,
    "recall": 74.29,
    "f1_score": 67.53
  }
}
```

#### Get Risk Metrics
Returns portfolio risk statistics.

**Endpoint:** `GET /api/risk_metrics`

**Response:**
```json
{
  "success": true,
  "max_drawdown": -12.4,
  "sharpe_ratio": 1.38,
  "current_streak": {
    "type": "winning",
    "count": 3
  },
  "longest_winning_streak": 7,
  "longest_losing_streak": 4,
  "avg_win": 2.1,
  "avg_loss": -1.8
}
```

#### Get Best/Worst Predictions
Returns top performing and worst performing predictions.

**Endpoint:** `GET /api/best_worst_predictions`

**Response:**
```json
{
  "success": true,
  "best": [
    {
      "date": "2024-10-15",
      "predicted": "UP",
      "actual": "UP",
      "confidence": 0.82,
      "actual_return": 2.45,
      "is_correct": true
    }
  ],
  "worst": [
    {
      "date": "2024-09-20",
      "predicted": "UP",
      "actual": "DOWN",
      "confidence": 0.75,
      "actual_return": -2.13,
      "is_correct": false
    }
  ]
}
```

---

### 10. Rolling Metrics

#### Get Rolling Accuracy
Returns accuracy over different time windows.

**Endpoint:** `GET /api/rolling_accuracy`

**Response:**
```json
{
  "success": true,
  "rolling_7d": {
    "current": 71.4,
    "average": 62.3
  },
  "rolling_30d": {
    "current": 63.3,
    "average": 58.9
  },
  "rolling_90d": {
    "current": 58.9,
    "average": 57.2
  }
}
```

---

### 11. Export

#### Export PDF Report
Generates and downloads a comprehensive PDF report.

**Endpoint:** `GET /api/export_pdf`

**Response:** Binary PDF file (application/pdf)

**Filename:** `SP500_Prediction_Report_YYYYMMDD_HHMMSS.pdf`

---

## Error Responses

All endpoints return errors in the following format:

```json
{
  "success": false,
  "error": "Error message description",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Model not loaded |

---

## Rate Limiting

Production API implements rate limiting:

- **Free tier**: 100 requests/hour
- **Authenticated**: 1000 requests/hour

Headers returned:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Webhooks (Coming Soon)

Subscribe to prediction events:

```json
POST /api/webhooks/subscribe
{
  "url": "https://your-domain.com/webhook",
  "events": ["prediction.created", "accuracy.updated"]
}
```

---

## SDK & Libraries

### Python
```python
import requests

response = requests.get('http://localhost:5000/api/latest_prediction')
prediction = response.json()
print(f"Direction: {prediction['prediction']['direction']}")
```

### JavaScript
```javascript
fetch('http://localhost:5000/api/latest_prediction')
  .then(response => response.json())
  .then(data => console.log(data.prediction.direction));
```

---

## Support

For API support:
- **GitHub Issues**: [Report problems](https://github.com/lkiwan/S-P-500-Price-Prediction/issues)
- **Documentation**: [Full docs](https://github.com/lkiwan/S-P-500-Price-Prediction)

---

**Last Updated:** November 14, 2024
