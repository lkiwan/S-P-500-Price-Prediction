# Quick Start Guide

Get up and running with S&P 500 price prediction in 5 minutes!

## Step 1: Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

Download required NLTK data:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Step 2: Configure (Optional - 1 minute)

If you want to scrape live news, get a free API key from [newsapi.org](https://newsapi.org) and add it to `config.yaml`:

```yaml
news:
  newsapi_key: "YOUR_API_KEY_HERE"
```

**Note**: You can skip this and use the existing `all news.md` file instead!

## Step 3: Run the Pipeline (2 minutes)

### Option A: Full Pipeline (Recommended)

```bash
python main.py
```

This will:
- ✅ Collect news and price data
- ✅ Analyze sentiment with FinBERT
- ✅ Engineer features
- ✅ Train ML model
- ✅ Make predictions
- ✅ Generate visualizations

### Option B: Step-by-Step

Use the Jupyter notebook for interactive exploration:

```bash
jupyter notebook notebooks/01_getting_started.ipynb
```

## Step 4: View Results

After running the pipeline, you'll find:

**Visualizations**:
- `sentiment_over_time.png` - News sentiment trends
- `price_vs_sentiment.png` - Price and sentiment correlation
- `feature_importance.png` - Most important features

**Data Files**:
- `data/raw/` - Raw news and price data
- `data/processed/` - Processed sentiment data
- `data/features/` - Engineered features

**Model**:
- `models/sp500_model_YYYYMMDD.pkl` - Trained model

**Report**:
- `data_report.txt` - Complete data summary

## Expected Output

```
==============================================================
PIPELINE COMPLETED SUCCESSFULLY!
==============================================================
Model Accuracy: 62.45%
Next Day Prediction: UP
Confidence: 67.3%

All results saved to respective directories.
```

## Understanding the Results

### Model Accuracy
- **>60%**: Excellent (significantly better than random)
- **55-60%**: Good (profitable with proper risk management)
- **50-55%**: Fair (marginal edge)
- **<50%**: Poor (worse than random)

### Prediction Confidence
- **>70%**: High confidence - Strong signal
- **60-70%**: Medium confidence - Moderate signal
- **50-60%**: Low confidence - Weak signal
- **<50%**: Very low confidence - Consider waiting

## Common Commands

```bash
# Collect 180 days of data
python main.py --days 180

# Use existing data (skip collection)
python main.py --skip-data

# Test individual components
python src/data_collection/price_fetcher.py
python src/features/sentiment_analyzer.py

# Start Jupyter notebook
jupyter notebook
```

## Troubleshooting

### FinBERT Not Loading?
The model will automatically download on first use. This may take a few minutes. If it fails, the system will fall back to VADER sentiment analysis.

### Out of Memory?
Reduce batch size in `config.yaml`:
```yaml
sentiment:
  batch_size: 16  # Default is 32
```

### NewsAPI Errors?
- Free tier allows 100 requests/day
- Use `--skip-data` to use existing data
- Or skip NewsAPI and use your own news file

## What's Next?

1. **Explore the notebook**: `notebooks/01_getting_started.ipynb`
2. **Customize config**: Edit `config.yaml` for your preferences
3. **Add more data**: Put your news articles in `all news.md`
4. **Experiment**: Try different models, features, and parameters
5. **Backtest**: Test predictions on historical data

## Key Files

- `main.py` - Full pipeline
- `config.yaml` - All settings
- `README.md` - Complete documentation
- `requirements.txt` - Dependencies
- `notebooks/` - Interactive examples
- `src/` - All source code

## Tips for Success

1. **More News = Better Predictions**: Collect diverse news sources
2. **Regular Updates**: Retrain model weekly/monthly with new data
3. **Risk Management**: Use predictions as ONE signal, not the only one
4. **Backtesting**: Always validate on historical data before live use

## Need Help?

- Check `README.md` for detailed documentation
- Review code comments for implementation details
- Open an issue if you find bugs

---

**Ready to predict the market? Let's go! 🚀📈**
