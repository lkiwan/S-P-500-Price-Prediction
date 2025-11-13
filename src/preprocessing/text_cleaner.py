"""
Text Cleaner Module
Cleans and preprocesses news text for sentiment analysis
"""

import re
import pandas as pd
import nltk
from typing import List, Optional
import yaml
import os

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class TextCleaner:
    """Clean and preprocess text data for NLP analysis"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize text cleaner"""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except:
            self.config = {}

        self.stop_words = set(stopwords.words('english'))

        # Financial terms to preserve (don't remove as stopwords)
        self.preserve_terms = {
            'up', 'down', 'above', 'below', 'over', 'under',
            'high', 'low', 'bull', 'bear', 'gain', 'loss'
        }

    def clean_text(self, text: str, deep_clean: bool = False) -> str:
        """
        Clean a single text string

        Args:
            text: Input text
            deep_clean: If True, removes stopwords and applies aggressive cleaning

        Returns:
            Cleaned text
        """
        if not isinstance(text, str) or not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)

        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)

        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)

        # Remove special characters but keep basic punctuation
        if deep_clean:
            text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
        else:
            # Keep more punctuation for sentiment analysis
            text = re.sub(r'[^a-zA-Z0-9\s.,!?;:\-\'\"()%$]', '', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove stopwords if deep cleaning
        if deep_clean:
            tokens = word_tokenize(text)
            tokens = [
                word for word in tokens
                if word not in self.stop_words or word in self.preserve_terms
            ]
            text = ' '.join(tokens)

        return text

    def clean_dataframe(self, df: pd.DataFrame,
                       text_columns: List[str] = None,
                       deep_clean: bool = False) -> pd.DataFrame:
        """
        Clean text columns in a dataframe

        Args:
            df: Input dataframe
            text_columns: List of column names to clean
            deep_clean: If True, applies aggressive cleaning

        Returns:
            DataFrame with cleaned text columns
        """
        if df.empty:
            return df

        df = df.copy()

        # Default text columns if not specified
        if text_columns is None:
            text_columns = ['title', 'description', 'content']

        # Clean each text column
        for col in text_columns:
            if col in df.columns:
                print(f"Cleaning column: {col}")
                df[f'{col}_clean'] = df[col].apply(
                    lambda x: self.clean_text(x, deep_clean)
                )

        # Combine title and description for full text
        if 'title_clean' in df.columns and 'description_clean' in df.columns:
            df['full_text'] = df.apply(
                lambda row: f"{row['title_clean']}. {row['description_clean']}".strip(),
                axis=1
            )
        elif 'title_clean' in df.columns:
            df['full_text'] = df['title_clean']

        # Remove rows with empty text
        if 'full_text' in df.columns:
            df = df[df['full_text'].str.len() > 0]

        return df

    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract important keywords from text

        Args:
            text: Input text
            top_n: Number of top keywords to return

        Returns:
            List of keywords
        """
        if not isinstance(text, str) or not text:
            return []

        # Tokenize and clean
        tokens = word_tokenize(text.lower())

        # Remove stopwords except preserved financial terms
        tokens = [
            word for word in tokens
            if (word not in self.stop_words or word in self.preserve_terms)
            and len(word) > 2
            and word.isalpha()
        ]

        # Count frequency
        from collections import Counter
        word_freq = Counter(tokens)

        # Return top N keywords
        return [word for word, count in word_freq.most_common(top_n)]

    def detect_market_mentions(self, text: str) -> dict:
        """
        Detect specific market-related mentions in text

        Args:
            text: Input text

        Returns:
            Dictionary with detection flags
        """
        if not isinstance(text, str):
            text = ""

        text_lower = text.lower()

        mentions = {
            'sp500': any(term in text_lower for term in ['s&p 500', 's&p500', 'sp500', 'sp 500']),
            'fed': any(term in text_lower for term in ['federal reserve', 'fed', 'fomc', 'powell']),
            'inflation': 'inflation' in text_lower or 'cpi' in text_lower,
            'earnings': 'earnings' in text_lower or 'revenue' in text_lower,
            'tech': any(term in text_lower for term in ['technology', 'tech stock', 'apple', 'microsoft', 'google']),
            'banking': any(term in text_lower for term in ['bank', 'banking', 'financial sector']),
            'recession': 'recession' in text_lower or 'economic downturn' in text_lower,
            'bull_market': 'bull market' in text_lower or 'bullish' in text_lower,
            'bear_market': 'bear market' in text_lower or 'bearish' in text_lower,
        }

        return mentions

    def preprocess_for_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess news dataframe specifically for sentiment analysis

        Args:
            df: Input news dataframe

        Returns:
            Preprocessed dataframe ready for sentiment analysis
        """
        print("Preprocessing news for sentiment analysis...")

        # Clean text (not too aggressive for sentiment)
        df = self.clean_dataframe(df, deep_clean=False)

        # Extract keywords
        if 'full_text' in df.columns:
            df['keywords'] = df['full_text'].apply(
                lambda x: ', '.join(self.extract_keywords(x, top_n=5))
            )

        # Detect market mentions
        if 'full_text' in df.columns:
            mentions_df = df['full_text'].apply(self.detect_market_mentions).apply(pd.Series)
            df = pd.concat([df, mentions_df], axis=1)

        # Calculate text length
        if 'full_text' in df.columns:
            df['text_length'] = df['full_text'].str.len()
            df['word_count'] = df['full_text'].str.split().str.len()

        print(f"Preprocessing complete. {len(df)} articles ready for analysis.")

        return df


if __name__ == "__main__":
    # Example usage
    cleaner = TextCleaner()

    # Test with sample text
    sample_text = """
    The S&P 500 SURGED 2.5% today as investors cheered strong earnings reports!
    Tech stocks led the rally, with AAPL gaining 3%. Visit https://example.com for more.
    """

    print("Original text:")
    print(sample_text)

    print("\nCleaned text:")
    cleaned = cleaner.clean_text(sample_text)
    print(cleaned)

    print("\nKeywords:")
    keywords = cleaner.extract_keywords(sample_text)
    print(keywords)

    print("\nMarket mentions:")
    mentions = cleaner.detect_market_mentions(sample_text)
    print(mentions)
