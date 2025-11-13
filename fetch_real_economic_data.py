"""
Fetch REAL Economic Data from FRED and BEA APIs
"""

import sys
sys.path.append('src')

from data_collection.economic_data import EconomicDataFetcher
import pandas as pd
import requests
import yaml
from datetime import datetime

print("\n" + "="*70)
print("FETCHING REAL ECONOMIC DATA")
print("="*70)
print("Using your FRED and BEA API keys")
print("="*70 + "\n")

# Load config to get API keys
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

fred_key = config['economic_data']['fred_api_key']
bea_key = config['economic_data']['bea_api_key']

print(f"FRED API Key: {fred_key[:10]}...{fred_key[-4:]}")
print(f"BEA API Key:  {bea_key[:10]}...{bea_key[-4:]}\n")

# Step 1: Fetch from FRED
print("STEP 1: Fetching data from FRED API...")
print("-" * 70)

fred_series = {
    'DFF': 'Federal Funds Rate',
    'UNRATE': 'Unemployment Rate',
    'CPIAUCSL': 'Consumer Price Index (CPI)',
    'VIXCLS': 'VIX Volatility Index',
    'DGS10': '10-Year Treasury Yield',
    'DGS2': '2-Year Treasury Yield',
    'T10Y2Y': '10Y-2Y Treasury Spread',
    'DEXUSEU': 'USD/EUR Exchange Rate',
    'DCOILWTICO': 'WTI Crude Oil Price',
    'UMCSENT': 'Consumer Sentiment',
    'INDPRO': 'Industrial Production',
    'PAYEMS': 'Nonfarm Payrolls',
    'HOUST': 'Housing Starts',
}

fred_data = None
successful_fetches = 0

for series_id, name in fred_series.items():
    try:
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': series_id,
            'api_key': fred_key,
            'file_type': 'json',
            'observation_start': '2020-01-01',
            'observation_end': datetime.now().strftime('%Y-%m-%d')
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if 'observations' in data:
                df = pd.DataFrame(data['observations'])
                df = df[['date', 'value']]
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df = df.dropna()
                df.columns = ['date', series_id]

                if fred_data is None:
                    fred_data = df
                else:
                    fred_data = pd.merge(fred_data, df, on='date', how='outer')

                print(f"  [OK] {name:40s} {len(df):5d} observations")
                successful_fetches += 1
            else:
                print(f"  [FAIL] {name:40s} No data returned")
        else:
            print(f"  [FAIL] {name:40s} HTTP {response.status_code}")

    except Exception as e:
        print(f"  [ERROR] {name:40s} Error: {str(e)[:40]}")

print(f"\nFRED: Successfully fetched {successful_fetches}/{len(fred_series)} series")

# Step 2: Fetch from BEA (GDP data)
print("\nSTEP 2: Fetching GDP data from BEA API...")
print("-" * 70)

try:
    # BEA NIPA API for GDP
    url = "https://apps.bea.gov/api/data"
    params = {
        'UserID': bea_key,
        'method': 'GetData',
        'datasetname': 'NIPA',
        'TableName': 'T10101',  # GDP table
        'Frequency': 'Q',  # Quarterly
        'Year': 'X',  # All years
        'ResultFormat': 'json'
    }

    response = requests.get(url, params=params, timeout=15)

    if response.status_code == 200:
        data = response.json()

        if 'BEAAPI' in data and 'Results' in data['BEAAPI']:
            results = data['BEAAPI']['Results']

            if 'Data' in results:
                bea_records = []
                for item in results['Data']:
                    try:
                        # Extract year and quarter
                        time_period = item.get('TimePeriod', '')
                        value = item.get('DataValue', '')

                        if time_period and value:
                            # Convert quarterly to approximate date
                            year = time_period[:4]
                            quarter = time_period[-2:]

                            month_map = {'Q1': '03', 'Q2': '06', 'Q3': '09', 'Q4': '12'}
                            month = month_map.get(quarter, '12')

                            date_str = f"{year}-{month}-01"

                            # Clean value (remove commas)
                            clean_value = value.replace(',', '')

                            bea_records.append({
                                'date': date_str,
                                'GDP': float(clean_value)
                            })
                    except:
                        continue

                if bea_records:
                    bea_df = pd.DataFrame(bea_records)
                    bea_df['date'] = pd.to_datetime(bea_df['date'])
                    bea_df = bea_df.sort_values('date')

                    print(f"  [OK] GDP Data: {len(bea_df)} quarterly observations")
                    print(f"    Latest GDP: ${bea_df['GDP'].iloc[-1]:.1f} billion")
                else:
                    print("  [FAIL] No GDP data could be parsed")
                    bea_df = None
            else:
                print("  [FAIL] No data in BEA response")
                bea_df = None
        else:
            print("  [FAIL] Unexpected BEA response format")
            bea_df = None
    else:
        print(f"  [FAIL] BEA API returned HTTP {response.status_code}")
        bea_df = None

except Exception as e:
    print(f"  [ERROR] Error fetching BEA data: {e}")
    bea_df = None

# Step 3: Merge and save
print("\nSTEP 3: Processing and saving economic data...")
print("-" * 70)

if fred_data is not None:
    fred_data['date'] = pd.to_datetime(fred_data['date'])
    fred_data = fred_data.sort_values('date')

    # Merge BEA data if available
    if bea_df is not None:
        # Forward fill GDP to daily
        all_dates = pd.DataFrame({
            'date': pd.date_range(start=fred_data['date'].min(),
                                 end=fred_data['date'].max(),
                                 freq='D')
        })

        bea_daily = pd.merge(all_dates, bea_df, on='date', how='left')
        bea_daily['GDP'] = bea_daily['GDP'].ffill()

        fred_data = pd.merge(fred_data, bea_daily, on='date', how='left')
        print(f"  [OK] Merged BEA GDP data")

    # Calculate derived features
    print("  Calculating derived indicators...")

    # Inflation rate (YoY CPI change)
    if 'CPIAUCSL' in fred_data.columns:
        fred_data['inflation_rate'] = fred_data['CPIAUCSL'].pct_change(252) * 100  # Approx 1 year

    # Fed rate changes
    if 'DFF' in fred_data.columns:
        fred_data['fed_rate_change'] = fred_data['DFF'].diff()
        fred_data['fed_rate_change_3m'] = fred_data['DFF'].diff(60)

    # Unemployment changes
    if 'UNRATE' in fred_data.columns:
        fred_data['unemployment_change'] = fred_data['UNRATE'].diff()

    # VIX features
    if 'VIXCLS' in fred_data.columns:
        fred_data['vix_ma20'] = fred_data['VIXCLS'].rolling(20).mean()
        fred_data['vix_spike'] = (fred_data['VIXCLS'] > fred_data['vix_ma20'] * 1.5).astype(int)

    # Yield curve inversion
    if 'T10Y2Y' in fred_data.columns:
        fred_data['yield_curve_inverted'] = (fred_data['T10Y2Y'] < 0).astype(int)

    # Save to CSV
    fred_data.to_csv('data/raw/economic_data_real.csv', index=False)
    print(f"  [OK] Saved to: data/raw/economic_data_real.csv")

    print(f"\n  Total indicators: {len(fred_data.columns) - 1}")
    print(f"  Date range: {fred_data['date'].min().date()} to {fred_data['date'].max().date()}")
    print(f"  Total observations: {len(fred_data)}")

    # Show sample
    print("\n  Sample of latest data:")
    print(fred_data.tail(3).to_string())

    print("\n" + "="*70)
    print("SUCCESS! Real economic data fetched and saved")
    print("="*70)
    print("\nNext step: Run complete pipeline with real economic data")
    print("  Command: python run_complete_pipeline.py")
    print("="*70 + "\n")

else:
    print("\n[ERROR] Failed to fetch FRED data. Check your API key.")
    print("  Your FRED key:", fred_key)
    print("\n  To get a new key: https://fred.stlouisfed.org/docs/api/api_key.html")
