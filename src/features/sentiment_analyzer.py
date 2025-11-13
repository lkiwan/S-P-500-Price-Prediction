"""
Sentiment Analyzer Module
Analyzes sentiment of financial news using FinBERT and other models
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import yaml
import warnings
warnings.filterwarnings('ignore')

try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not installed. Install with: pip install transformers torch")

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("Warning: vaderSentiment not installed. Install with: pip install vaderSentiment")


class SentimentAnalyzer:
    """Analyze sentiment of financial news using multiple models"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize sentiment analyzer"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.sentiment_config = self.config['sentiment']
        self.model_name = self.sentiment_config['model']
        self.use_cuda = self.sentiment_config['use_cuda'] and torch.cuda.is_available() if TRANSFORMERS_AVAILABLE else False

        # Initialize FinBERT model
        self.finbert_model = None
        self.finbert_tokenizer = None
        if TRANSFORMERS_AVAILABLE:
            self._load_finbert()

        # Initialize VADER
        self.vader_analyzer = None
        if VADER_AVAILABLE:
            self.vader_analyzer = SentimentIntensityAnalyzer()

    def _load_finbert(self):
        """Load FinBERT model and tokenizer"""
        try:
            print(f"Loading FinBERT model: {self.model_name}")
            self.finbert_tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.finbert_model = AutoModelForSequenceClassification.from_pretrained(self.model_name)

            if self.use_cuda:
                self.finbert_model = self.finbert_model.cuda()
                print("Using CUDA for inference")
            else:
                print("Using CPU for inference")

            self.finbert_model.eval()
            print("FinBERT model loaded successfully")

        except Exception as e:
            print(f"Error loading FinBERT model: {e}")
            print("Will fall back to VADER sentiment analysis")
            self.finbert_model = None
            self.finbert_tokenizer = None

    def analyze_finbert(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using FinBERT

        Args:
            text: Input text

        Returns:
            Dictionary with sentiment scores
        """
        if not self.finbert_model or not self.finbert_tokenizer:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'compound': 0.0}

        try:
            # Tokenize
            inputs = self.finbert_tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=self.sentiment_config['max_length'],
                padding=True
            )

            if self.use_cuda:
                inputs = {k: v.cuda() for k, v in inputs.items()}

            # Get predictions
            with torch.no_grad():
                outputs = self.finbert_model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # FinBERT outputs: [positive, negative, neutral]
            probs = predictions[0].cpu().numpy()

            # Calculate compound score (-1 to 1)
            compound = probs[0] - probs[1]  # positive - negative

            return {
                'positive': float(probs[0]),
                'negative': float(probs[1]),
                'neutral': float(probs[2]),
                'compound': float(compound)
            }

        except Exception as e:
            print(f"Error in FinBERT analysis: {e}")
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'compound': 0.0}

    def analyze_vader(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using VADER

        Args:
            text: Input text

        Returns:
            Dictionary with sentiment scores
        """
        if not self.vader_analyzer:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'compound': 0.0}

        try:
            scores = self.vader_analyzer.polarity_scores(text)
            return {
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'compound': scores['compound']
            }

        except Exception as e:
            print(f"Error in VADER analysis: {e}")
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'compound': 0.0}

    def analyze_text(self, text: str, method: str = 'finbert') -> Dict[str, float]:
        """
        Analyze sentiment of a single text

        Args:
            text: Input text
            method: 'finbert', 'vader', or 'ensemble'

        Returns:
            Dictionary with sentiment scores
        """
        if not isinstance(text, str) or not text:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'compound': 0.0}

        if method == 'finbert':
            return self.analyze_finbert(text)
        elif method == 'vader':
            return self.analyze_vader(text)
        elif method == 'ensemble':
            # Combine FinBERT and VADER
            finbert_scores = self.analyze_finbert(text)
            vader_scores = self.analyze_vader(text)

            # Average the scores
            ensemble_scores = {
                'positive': (finbert_scores['positive'] + vader_scores['positive']) / 2,
                'negative': (finbert_scores['negative'] + vader_scores['negative']) / 2,
                'neutral': (finbert_scores['neutral'] + vader_scores['neutral']) / 2,
                'compound': (finbert_scores['compound'] + vader_scores['compound']) / 2
            }
            return ensemble_scores
        else:
            raise ValueError(f"Unknown method: {method}")

    def analyze_batch(self, texts: List[str], method: str = 'finbert',
                     batch_size: int = None) -> pd.DataFrame:
        """
        Analyze sentiment for multiple texts

        Args:
            texts: List of input texts
            method: Sentiment analysis method
            batch_size: Batch size for processing

        Returns:
            DataFrame with sentiment scores
        """
        if not texts:
            return pd.DataFrame()

        batch_size = batch_size or self.sentiment_config['batch_size']
        results = []

        print(f"Analyzing sentiment for {len(texts)} texts using {method}...")

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            for text in batch:
                scores = self.analyze_text(text, method)
                results.append(scores)

            if (i + batch_size) % 100 == 0:
                print(f"  Processed {min(i + batch_size, len(texts))}/{len(texts)} texts")

        print("Sentiment analysis complete")

        return pd.DataFrame(results)

    def analyze_dataframe(self, df: pd.DataFrame,
                         text_column: str = 'full_text',
                         method: str = 'finbert') -> pd.DataFrame:
        """
        Analyze sentiment for a dataframe with news articles

        Args:
            df: Input dataframe
            text_column: Column containing text to analyze
            method: Sentiment analysis method

        Returns:
            DataFrame with added sentiment columns
        """
        if df.empty or text_column not in df.columns:
            print(f"Error: DataFrame is empty or missing column '{text_column}'")
            return df

        df = df.copy()

        # Analyze sentiment
        sentiment_df = self.analyze_batch(df[text_column].tolist(), method)

        # Add sentiment columns
        df['sentiment_positive'] = sentiment_df['positive']
        df['sentiment_negative'] = sentiment_df['negative']
        df['sentiment_neutral'] = sentiment_df['neutral']
        df['sentiment_compound'] = sentiment_df['compound']

        # Add sentiment label
        df['sentiment_label'] = df['sentiment_compound'].apply(
            lambda x: 'positive' if x > 0.05 else ('negative' if x < -0.05 else 'neutral')
        )

        return df

    def aggregate_daily_sentiment(self, df: pd.DataFrame,
                                  date_column: str = 'date') -> pd.DataFrame:
        """
        Aggregate sentiment scores by date

        Args:
            df: DataFrame with sentiment scores
            date_column: Column containing dates

        Returns:
            DataFrame with daily aggregated sentiment
        """
        if df.empty or date_column not in df.columns:
            return pd.DataFrame()

        # Ensure date column is datetime
        df[date_column] = pd.to_datetime(df[date_column])

        # Aggregate by date
        daily_sentiment = df.groupby(date_column).agg({
            'sentiment_positive': 'mean',
            'sentiment_negative': 'mean',
            'sentiment_neutral': 'mean',
            'sentiment_compound': ['mean', 'std', 'min', 'max', 'count']
        }).reset_index()

        # Flatten column names
        daily_sentiment.columns = [
            'date',
            'sentiment_positive_mean',
            'sentiment_negative_mean',
            'sentiment_neutral_mean',
            'sentiment_compound_mean',
            'sentiment_compound_std',
            'sentiment_compound_min',
            'sentiment_compound_max',
            'news_count'
        ]

        # Calculate sentiment momentum (change from previous day)
        daily_sentiment['sentiment_momentum'] = daily_sentiment['sentiment_compound_mean'].diff()

        # Calculate rolling averages
        daily_sentiment['sentiment_ma5'] = daily_sentiment['sentiment_compound_mean'].rolling(5).mean()
        daily_sentiment['sentiment_ma10'] = daily_sentiment['sentiment_compound_mean'].rolling(10).mean()

        return daily_sentiment


if __name__ == "__main__":
    # Example usage
    analyzer = SentimentAnalyzer()

    # Test with sample texts
    sample_texts = [
        "S&P 500 surges to record high as tech stocks rally strongly!",
        "Market crashes amid recession fears and rising inflation concerns.",
        "The Federal Reserve maintains interest rates at current levels.",
    ]

    print("Testing sentiment analysis:\n")

    for text in sample_texts:
        print(f"Text: {text}")

        if analyzer.finbert_model:
            finbert_scores = analyzer.analyze_finbert(text)
            print(f"  FinBERT: {finbert_scores['compound']:.3f} ({finbert_scores})")

        if analyzer.vader_analyzer:
            vader_scores = analyzer.analyze_vader(text)
            print(f"  VADER:   {vader_scores['compound']:.3f}")

        print()
