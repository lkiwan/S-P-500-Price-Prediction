"""
Feature Engineering Module
Combines sentiment and technical features for ML model
"""

import pandas as pd
import numpy as np
from typing import List, Optional
import yaml
import os


class FeatureEngineer:
    """Create features from sentiment and price data"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize feature engineer"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.features_config = self.config['features']
        self.features_path = self.config['paths']['features']

        os.makedirs(self.features_path, exist_ok=True)

    def merge_sentiment_and_prices(self,
                                   sentiment_df: pd.DataFrame,
                                   price_df: pd.DataFrame,
                                   date_column: str = 'date') -> pd.DataFrame:
        """
        Merge daily sentiment scores with price data

        Args:
            sentiment_df: DataFrame with daily sentiment scores
            price_df: DataFrame with price data
            date_column: Column name for date

        Returns:
            Merged DataFrame
        """
        # Ensure date columns are datetime
        sentiment_df[date_column] = pd.to_datetime(sentiment_df[date_column])
        price_df[date_column] = pd.to_datetime(price_df[date_column])

        # Merge on date
        merged = pd.merge(
            price_df,
            sentiment_df,
            on=date_column,
            how='left'
        )

        # Fill missing sentiment values with neutral (0)
        sentiment_cols = [col for col in merged.columns if 'sentiment' in col]
        merged[sentiment_cols] = merged[sentiment_cols].fillna(0)

        # Fill news_count with 0
        if 'news_count' in merged.columns:
            merged['news_count'] = merged['news_count'].fillna(0)

        print(f"Merged data: {len(merged)} rows, {len(merged.columns)} columns")

        return merged

    def create_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create lagged features for sentiment and price

        Args:
            df: Input dataframe

        Returns:
            DataFrame with lag features
        """
        df = df.copy()

        # Sentiment lag features
        sentiment_lags = self.features_config['sentiment_lag_days']
        for lag in sentiment_lags:
            if lag > 0:
                df[f'sentiment_lag{lag}'] = df['sentiment_compound_mean'].shift(lag)

        # Price lag features
        price_lags = self.features_config['price_lag_days']
        for lag in price_lags:
            df[f'return_lag{lag}'] = df['return'].shift(lag)
            df[f'close_lag{lag}'] = df['close'].shift(lag)

        return df

    def create_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create rolling window features

        Args:
            df: Input dataframe

        Returns:
            DataFrame with rolling features
        """
        df = df.copy()

        windows = self.features_config['rolling_windows']

        for window in windows:
            # Rolling sentiment statistics
            df[f'sentiment_rolling_mean_{window}'] = df['sentiment_compound_mean'].rolling(window).mean()
            df[f'sentiment_rolling_std_{window}'] = df['sentiment_compound_mean'].rolling(window).std()
            df[f'sentiment_rolling_min_{window}'] = df['sentiment_compound_mean'].rolling(window).min()
            df[f'sentiment_rolling_max_{window}'] = df['sentiment_compound_mean'].rolling(window).max()

            # Rolling price statistics
            df[f'return_rolling_mean_{window}'] = df['return'].rolling(window).mean()
            df[f'return_rolling_std_{window}'] = df['return'].rolling(window).std()

            # Rolling volume
            df[f'volume_rolling_mean_{window}'] = df['volume'].rolling(window).mean()

        return df

    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create interaction features between sentiment and technical indicators

        Args:
            df: Input dataframe

        Returns:
            DataFrame with interaction features
        """
        df = df.copy()

        # Sentiment * Technical indicators
        if 'sentiment_compound_mean' in df.columns and 'rsi_14' in df.columns:
            df['sentiment_rsi'] = df['sentiment_compound_mean'] * df['rsi_14']

        if 'sentiment_compound_mean' in df.columns and 'macd' in df.columns:
            df['sentiment_macd'] = df['sentiment_compound_mean'] * df['macd']

        if 'sentiment_compound_mean' in df.columns and 'volume_ratio' in df.columns:
            df['sentiment_volume'] = df['sentiment_compound_mean'] * df['volume_ratio']

        # Sentiment change * Price change
        if 'sentiment_momentum' in df.columns and 'return' in df.columns:
            df['sentiment_price_momentum'] = df['sentiment_momentum'] * df['return']

        # News count * Sentiment strength
        if 'news_count' in df.columns and 'sentiment_compound_mean' in df.columns:
            df['news_weighted_sentiment'] = df['news_count'] * np.abs(df['sentiment_compound_mean'])

        return df

    def create_target_variable(self, df: pd.DataFrame,
                              task: str = 'classification',
                              horizon: int = 1) -> pd.DataFrame:
        """
        Create target variable for prediction

        Args:
            df: Input dataframe
            task: 'classification' or 'regression'
            horizon: Days ahead to predict (default: 1 = next day)

        Returns:
            DataFrame with target variable
        """
        df = df.copy()

        if task == 'classification':
            # Binary classification: will price go up or down?
            df['target'] = (df['close'].shift(-horizon) > df['close']).astype(int)

            # Multi-class: significant up, slight up, slight down, significant down
            df['target_multiclass'] = pd.cut(
                df['return'].shift(-horizon),
                bins=[-np.inf, -0.01, 0, 0.01, np.inf],
                labels=[0, 1, 2, 3]  # 0=big down, 1=slight down, 2=slight up, 3=big up
            )

        elif task == 'regression':
            # Predict next day's return
            df['target'] = df['return'].shift(-horizon)

            # Predict next day's price
            df['target_price'] = df['close'].shift(-horizon)

        else:
            raise ValueError(f"Unknown task: {task}")

        return df

    def create_all_features(self, sentiment_df: pd.DataFrame,
                          price_df: pd.DataFrame,
                          task: str = 'classification') -> pd.DataFrame:
        """
        Create complete feature set

        Args:
            sentiment_df: Daily sentiment scores
            price_df: Price data with technical indicators
            task: Prediction task type

        Returns:
            Complete feature DataFrame
        """
        print("Creating features...")

        # Merge sentiment and prices
        df = self.merge_sentiment_and_prices(sentiment_df, price_df)

        # Create lag features
        print("  Creating lag features...")
        df = self.create_lag_features(df)

        # Create rolling features
        print("  Creating rolling features...")
        df = self.create_rolling_features(df)

        # Create interaction features
        print("  Creating interaction features...")
        df = self.create_interaction_features(df)

        # Create target variable
        print("  Creating target variable...")
        df = self.create_target_variable(df, task)

        # Remove rows with NaN (due to lagging and rolling)
        initial_rows = len(df)
        df = df.dropna()
        print(f"  Removed {initial_rows - len(df)} rows with missing values")

        print(f"Feature engineering complete: {len(df)} rows, {len(df.columns)} features")

        return df

    def select_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Select relevant feature columns for modeling

        Args:
            df: Complete dataframe

        Returns:
            List of feature column names
        """
        # Exclude columns that shouldn't be features
        exclude = ['date', 'target', 'target_multiclass', 'target_price',
                  'open', 'high', 'low', 'close', 'volume',
                  'direction', 'price_change']

        feature_cols = [col for col in df.columns if col not in exclude]

        return feature_cols

    def get_feature_importance_names(self) -> List[str]:
        """Get descriptive names for feature categories"""
        categories = {
            'sentiment': 'Sentiment scores and aggregations',
            'technical': 'Technical indicators (RSI, MACD, etc.)',
            'lag': 'Lagged features from previous days',
            'rolling': 'Rolling window statistics',
            'interaction': 'Interaction between sentiment and technical',
            'volume': 'Volume-related features',
            'momentum': 'Price and sentiment momentum'
        }
        return categories

    def save_features(self, df: pd.DataFrame, filename: str = "features.csv"):
        """Save feature dataframe"""
        filepath = os.path.join(self.features_path, filename)
        df.to_csv(filepath, index=False)
        print(f"Saved features to {filepath}")

    def load_features(self, filename: str = "features.csv") -> pd.DataFrame:
        """Load feature dataframe"""
        filepath = os.path.join(self.features_path, filename)

        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return pd.DataFrame()

        df = pd.read_csv(filepath)
        print(f"Loaded features from {filepath}: {len(df)} rows")
        return df


if __name__ == "__main__":
    # Example usage
    engineer = FeatureEngineer()

    print("Feature Engineering Module")
    print("\nFeature categories:")
    for category, description in engineer.get_feature_importance_names().items():
        print(f"  {category}: {description}")
