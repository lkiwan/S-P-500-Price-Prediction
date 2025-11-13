"""
Economic Data Fetcher
Fetches macroeconomic indicators from FRED and other sources
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import yaml
import os
from typing import Optional, List, Dict


class EconomicDataFetcher:
    """Fetch economic indicators from multiple sources"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize economic data fetcher"""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except:
            self.config = {}

        # API keys (optional - will use free access if not provided)
        self.fred_api_key = self.config.get('economic_data', {}).get('fred_api_key', None)

        self.raw_data_path = self.config.get('paths', {}).get('raw_data', 'data/raw')
        os.makedirs(self.raw_data_path, exist_ok=True)

    def fetch_fred_data(self, series_id: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Fetch data from FRED API

        Args:
            series_id: FRED series ID (e.g., 'DFF' for Federal Funds Rate)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with date and value columns
        """
        if not self.fred_api_key:
            print(f"  Warning: No FRED API key. Using alternative source for {series_id}")
            return pd.DataFrame()

        try:
            url = f"https://api.stlouisfed.org/fred/series/observations"

            params = {
                'series_id': series_id,
                'api_key': self.fred_api_key,
                'file_type': 'json',
                'observation_start': start_date or '2020-01-01',
                'observation_end': end_date or datetime.now().strftime('%Y-%m-%d')
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if 'observations' in data:
                df = pd.DataFrame(data['observations'])
                df = df[['date', 'value']]
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df = df.dropna()
                df.columns = ['date', series_id]

                return df
            else:
                return pd.DataFrame()

        except Exception as e:
            print(f"  Error fetching {series_id} from FRED: {e}")
            return pd.DataFrame()

    def fetch_all_fred_indicators(self, start_date: str = "2020-01-01") -> pd.DataFrame:
        """
        Fetch key economic indicators from FRED

        Args:
            start_date: Start date for data collection

        Returns:
            DataFrame with all economic indicators
        """
        print("Fetching economic indicators from FRED...")

        # Key economic indicators
        indicators = {
            'DFF': 'Federal Funds Rate',
            'UNRATE': 'Unemployment Rate',
            'CPIAUCSL': 'Consumer Price Index',
            'GDP': 'Gross Domestic Product',
            'VIXCLS': 'VIX Volatility Index',
            'DGS10': '10-Year Treasury Yield',
            'DGS2': '2-Year Treasury Yield',
            'T10Y2Y': '10Y-2Y Treasury Spread',
            'DEXUSEU': 'Dollar/Euro Exchange Rate',
            'DCOILWTICO': 'Crude Oil WTI Price',
            'UMCSENT': 'Consumer Sentiment Index',
            'INDPRO': 'Industrial Production Index',
            'PAYEMS': 'Total Nonfarm Payrolls',
        }

        all_data = None

        for series_id, name in indicators.items():
            print(f"  Fetching {name} ({series_id})...")
            df = self.fetch_fred_data(series_id, start_date)

            if not df.empty:
                if all_data is None:
                    all_data = df
                else:
                    all_data = pd.merge(all_data, df, on='date', how='outer')

        if all_data is not None:
            all_data = all_data.sort_values('date')
            print(f"\n  Fetched {len(all_data)} days of economic data")
            return all_data
        else:
            return pd.DataFrame()

    def create_synthetic_economic_data(self, price_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create synthetic economic indicators for demo (when APIs not available)

        Args:
            price_df: Price dataframe with dates

        Returns:
            DataFrame with synthetic economic indicators
        """
        print("Creating synthetic economic indicators (no API key)...")

        df = pd.DataFrame()
        df['date'] = price_df['date']

        # Create realistic synthetic indicators
        n = len(df)

        # Federal Funds Rate (trending down in 2020, up in 2022-2023)
        base_rate = np.linspace(1.5, 5.5, n)
        df['fed_funds_rate'] = base_rate + np.random.normal(0, 0.1, n)

        # Unemployment Rate (spike in 2020, then decline)
        unemployment = np.concatenate([
            np.linspace(3.5, 14.0, n//10),  # COVID spike
            np.linspace(14.0, 3.5, n - n//10)  # Recovery
        ])
        df['unemployment_rate'] = unemployment[:n] + np.random.normal(0, 0.2, n)

        # Inflation (CPI) - rising trend
        inflation = np.linspace(2.0, 4.5, n)
        df['cpi'] = 250 + np.cumsum(inflation / 12) + np.random.normal(0, 0.5, n)

        # VIX Volatility Index
        df['vix'] = 20 + np.random.gamma(2, 5, n)

        # 10-Year Treasury Yield
        df['treasury_10y'] = 1.5 + np.linspace(0, 3, n) + np.random.normal(0, 0.2, n)

        # 2-Year Treasury Yield
        df['treasury_2y'] = 0.5 + np.linspace(0, 4, n) + np.random.normal(0, 0.2, n)

        # Yield Curve (10Y - 2Y)
        df['yield_curve'] = df['treasury_10y'] - df['treasury_2y']

        # Dollar Index
        df['dollar_index'] = 95 + np.random.normal(0, 5, n).cumsum() * 0.1

        # Oil Price
        df['oil_price'] = 60 + np.random.normal(0, 10, n).cumsum() * 0.5

        # Consumer Sentiment
        df['consumer_sentiment'] = 90 + np.random.normal(0, 10, n)

        print(f"  Created {len(df.columns)-1} synthetic economic indicators")

        return df

    def calculate_economic_features(self, econ_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived features from economic indicators

        Args:
            econ_df: DataFrame with economic indicators

        Returns:
            DataFrame with additional calculated features
        """
        df = econ_df.copy()

        # Rate of change features
        if 'fed_funds_rate' in df.columns:
            df['fed_rate_change'] = df['fed_funds_rate'].diff()
            df['fed_rate_change_3m'] = df['fed_funds_rate'].diff(60)  # 3-month change

        if 'unemployment_rate' in df.columns:
            df['unemployment_change'] = df['unemployment_rate'].diff()

        if 'cpi' in df.columns:
            df['inflation_rate'] = df['cpi'].pct_change(12) * 100  # YoY inflation

        if 'vix' in df.columns:
            df['vix_ma20'] = df['vix'].rolling(20).mean()
            df['vix_spike'] = (df['vix'] > df['vix_ma20'] * 1.5).astype(int)

        # Yield curve inversion (recession indicator)
        if 'yield_curve' in df.columns:
            df['yield_curve_inverted'] = (df['yield_curve'] < 0).astype(int)

        # Economic momentum
        if 'consumer_sentiment' in df.columns:
            df['consumer_sentiment_momentum'] = df['consumer_sentiment'].diff()

        return df

    def merge_with_prices(self, economic_df: pd.DataFrame, price_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge economic indicators with price data

        Args:
            economic_df: Economic indicators dataframe
            price_df: Price dataframe

        Returns:
            Merged dataframe
        """
        # Ensure date columns are datetime
        economic_df['date'] = pd.to_datetime(economic_df['date'])
        price_df['date'] = pd.to_datetime(price_df['date'])

        # Merge (forward fill economic data to match daily price data)
        merged = pd.merge(price_df, economic_df, on='date', how='left')

        # Forward fill economic indicators (they update less frequently)
        econ_cols = [col for col in economic_df.columns if col != 'date']
        merged[econ_cols] = merged[econ_cols].ffill()

        # Backward fill for initial NaN values
        merged[econ_cols] = merged[econ_cols].bfill()

        return merged

    def get_full_dataset(self, price_df: pd.DataFrame, use_fred: bool = True) -> pd.DataFrame:
        """
        Get complete dataset with economic indicators

        Args:
            price_df: Price dataframe
            use_fred: Whether to try fetching from FRED API

        Returns:
            Complete dataframe with prices and economic indicators
        """
        if use_fred and self.fred_api_key:
            # Try to fetch real data from FRED
            start_date = price_df['date'].min()
            econ_df = self.fetch_all_fred_indicators(start_date)

            if not econ_df.empty:
                econ_df = self.calculate_economic_features(econ_df)
                merged = self.merge_with_prices(econ_df, price_df)
                return merged

        # Fall back to synthetic data
        econ_df = self.create_synthetic_economic_data(price_df)
        econ_df = self.calculate_economic_features(econ_df)
        merged = self.merge_with_prices(econ_df, price_df)

        return merged

    def save_economic_data(self, df: pd.DataFrame, filename: str = "economic_data.csv"):
        """Save economic data to CSV"""
        filepath = os.path.join(self.raw_data_path, filename)

        # Save only economic columns (not price data)
        econ_cols = ['date'] + [col for col in df.columns
                                if col not in ['open', 'high', 'low', 'close', 'volume',
                                             'adj close', 'return', 'direction']]

        df[econ_cols].to_csv(filepath, index=False)
        print(f"Saved economic data to {filepath}")


if __name__ == "__main__":
    # Example usage
    fetcher = EconomicDataFetcher()

    # Load price data
    try:
        price_df = pd.read_csv('data/raw/price_data.csv')
        print(f"Loaded {len(price_df)} days of price data\n")

        # Get economic data
        full_df = fetcher.get_full_dataset(price_df, use_fred=False)

        print(f"\nFull dataset: {len(full_df)} rows, {len(full_df.columns)} columns")
        print(f"\nEconomic indicators added:")

        econ_cols = [col for col in full_df.columns
                    if col not in price_df.columns and col != 'date']
        for col in econ_cols:
            print(f"  - {col}")

        # Save economic data
        fetcher.save_economic_data(full_df)

    except Exception as e:
        print(f"Error: {e}")
