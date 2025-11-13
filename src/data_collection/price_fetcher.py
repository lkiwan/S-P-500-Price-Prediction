"""
Price Fetcher Module
Downloads S&P 500 historical price data
"""

import yfinance as yf
import pandas as pd
import yaml
import os
from datetime import datetime, timedelta
from typing import Optional


class PriceFetcher:
    """Fetches S&P 500 price data from Yahoo Finance"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize price fetcher with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.ticker = self.config['data']['ticker']
        self.start_date = self.config['data']['start_date']
        self.end_date = self.config['data']['end_date']
        self.raw_data_path = self.config['paths']['raw_data']

        # Create data directory if it doesn't exist
        os.makedirs(self.raw_data_path, exist_ok=True)

    def fetch_prices(self,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     ticker: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch historical price data for S&P 500

        Args:
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)
            ticker: Stock ticker symbol (optional)

        Returns:
            DataFrame with OHLCV data and calculated fields
        """
        # Use config values if not provided
        ticker = ticker or self.ticker
        start_date = start_date or self.start_date
        end_date = end_date or datetime.now().strftime('%Y-%m-%d')

        print(f"Fetching {ticker} data from {start_date} to {end_date}...")

        try:
            # Download data
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)

            if df.empty:
                print(f"No data found for {ticker}")
                return pd.DataFrame()

            # Reset index to make Date a column
            df = df.reset_index()

            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

            # Rename columns to lowercase
            df.columns = [col.lower() if isinstance(col, str) else str(col).lower() for col in df.columns]

            # Calculate daily returns
            df['return'] = df['close'].pct_change()

            # Calculate log returns
            df['log_return'] = pd.Series(df['close']).apply(lambda x: pd.Series(x).pct_change()).apply(
                lambda x: pd.Series(x).apply(lambda y: 0 if y == 0 else (1 if y > 0 else -1))
            )

            # Simpler calculation
            df['log_return'] = (df['close'] / df['close'].shift(1)).apply(
                lambda x: 0 if pd.isna(x) else (1 if x > 1 else (-1 if x < 1 else 0))
            )

            # Calculate price direction (up=1, down=0)
            df['direction'] = (df['return'] > 0).astype(int)

            # Calculate price change
            df['price_change'] = df['close'] - df['close'].shift(1)

            # Calculate intraday range
            df['intraday_range'] = df['high'] - df['low']

            # Calculate volatility (rolling std of returns)
            df['volatility_5d'] = df['return'].rolling(window=5).std()
            df['volatility_20d'] = df['return'].rolling(window=20).std()

            # Format date
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

            print(f"Successfully fetched {len(df)} days of data")

            return df

        except Exception as e:
            print(f"Error fetching price data: {e}")
            return pd.DataFrame()

    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to price dataframe

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with additional technical indicators
        """
        if df.empty:
            return df

        try:
            # Simple Moving Averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['sma_200'] = df['close'].rolling(window=200).mean()

            # Exponential Moving Averages
            df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()

            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']

            # RSI (Relative Strength Index)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi_14'] = 100 - (100 / (1 + rs))

            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            df['bb_width'] = df['bb_upper'] - df['bb_lower']

            # Volume indicators
            df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma_20']

            # Price momentum
            df['momentum_5'] = df['close'] - df['close'].shift(5)
            df['momentum_10'] = df['close'] - df['close'].shift(10)
            df['momentum_20'] = df['close'] - df['close'].shift(20)

            # Rate of Change (ROC)
            df['roc_5'] = ((df['close'] - df['close'].shift(5)) / df['close'].shift(5)) * 100
            df['roc_10'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100

            print(f"Added technical indicators to {len(df)} rows")

            return df

        except Exception as e:
            print(f"Error adding technical indicators: {e}")
            return df

    def get_full_dataset(self) -> pd.DataFrame:
        """
        Fetch prices and add all technical indicators

        Returns:
            Complete DataFrame with prices and indicators
        """
        df = self.fetch_prices()

        if not df.empty:
            df = self.add_technical_indicators(df)

        return df

    def save_prices(self, df: pd.DataFrame, filename: str = "price_data.csv"):
        """Save price data to CSV file"""
        if df.empty:
            print("No data to save")
            return

        filepath = os.path.join(self.raw_data_path, filename)
        df.to_csv(filepath, index=False)
        print(f"Saved price data to {filepath}")

    def get_latest_price(self) -> dict:
        """
        Get the most recent price information

        Returns:
            Dictionary with latest price info
        """
        try:
            ticker_obj = yf.Ticker(self.ticker)
            info = ticker_obj.info

            return {
                'price': info.get('regularMarketPrice', 0),
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'volume': info.get('regularMarketVolume', 0),
                'date': datetime.now().strftime('%Y-%m-%d')
            }

        except Exception as e:
            print(f"Error getting latest price: {e}")
            return {}


if __name__ == "__main__":
    # Example usage
    fetcher = PriceFetcher()

    # Fetch full dataset
    price_df = fetcher.get_full_dataset()

    if not price_df.empty:
        fetcher.save_prices(price_df)

        print("\nDataset summary:")
        print(f"Date range: {price_df['date'].min()} to {price_df['date'].max()}")
        print(f"Total rows: {len(price_df)}")
        print(f"\nColumns: {list(price_df.columns)}")

        print("\nLatest data:")
        print(price_df.tail())

        # Get latest price
        latest = fetcher.get_latest_price()
        print(f"\nCurrent S&P 500: ${latest.get('price', 'N/A')}")
        print(f"Change: {latest.get('change', 'N/A')} ({latest.get('change_percent', 'N/A')}%)")
