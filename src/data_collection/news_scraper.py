"""
News Scraper Module
Collects financial news from multiple sources for S&P 500 sentiment analysis
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import yaml
import os
from typing import List, Dict, Optional


class NewsScraper:
    """Scrapes financial news from various sources"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the news scraper with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.newsapi_key = self.config['news'].get('newsapi_key')
        self.max_articles = self.config['news']['max_articles_per_day']
        self.raw_data_path = self.config['paths']['raw_data']

        # Create data directory if it doesn't exist
        os.makedirs(self.raw_data_path, exist_ok=True)

    def scrape_newsapi(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Scrape news from NewsAPI.org

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with columns: date, title, description, source, url
        """
        if not self.newsapi_key or self.newsapi_key == "YOUR_API_KEY_HERE":
            print("Warning: NewsAPI key not configured. Skipping NewsAPI scraping.")
            return pd.DataFrame()

        base_url = "https://newsapi.org/v2/everything"

        params = {
            'q': 'S&P 500 OR stock market OR economy OR Federal Reserve',
            'language': 'en',
            'from': start_date,
            'to': end_date,
            'sortBy': 'relevancy',
            'pageSize': self.max_articles,
            'apiKey': self.newsapi_key
        }

        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'date': article['publishedAt'][:10],
                    'title': article['title'],
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'source': article['source']['name'],
                    'url': article['url']
                })

            return pd.DataFrame(articles)

        except Exception as e:
            print(f"Error scraping NewsAPI: {e}")
            return pd.DataFrame()

    def scrape_finviz_news(self) -> pd.DataFrame:
        """
        Scrape recent news from Finviz for S&P 500

        Returns:
            DataFrame with news articles
        """
        url = "https://finviz.com/quote.ashx?t=SPY"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            news_table = soup.find('table', class_='news-table')
            articles = []

            if news_table:
                current_date = datetime.now().strftime('%Y-%m-%d')

                for row in news_table.find_all('tr'):
                    try:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            # Parse date/time
                            date_cell = cells[0].text.strip()
                            if len(date_cell.split()) > 1:
                                current_date = datetime.strptime(
                                    date_cell.split()[0], '%b-%d-%y'
                                ).strftime('%Y-%m-%d')

                            # Parse article
                            link = cells[1].find('a')
                            if link:
                                articles.append({
                                    'date': current_date,
                                    'title': link.text.strip(),
                                    'description': '',
                                    'content': '',
                                    'source': 'Finviz',
                                    'url': link.get('href', '')
                                })
                    except Exception as e:
                        continue

            return pd.DataFrame(articles)

        except Exception as e:
            print(f"Error scraping Finviz: {e}")
            return pd.DataFrame()

    def load_existing_news(self, news_file: str = None) -> pd.DataFrame:
        """
        Load news from existing file (all news.md)

        Args:
            news_file: Path to news file

        Returns:
            DataFrame with parsed news
        """
        if news_file is None:
            news_file = self.config['paths']['news_file']

        if not os.path.exists(news_file):
            print(f"News file {news_file} not found.")
            return pd.DataFrame()

        try:
            with open(news_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the content - assuming format with dates and news items
            # This is a simple parser - adjust based on your actual file format
            articles = []

            lines = content.strip().split('\n')
            current_article = {}

            for line in lines:
                line = line.strip()
                if not line:
                    if current_article:
                        articles.append(current_article)
                        current_article = {}
                    continue

                # Simple heuristic parsing - adjust to your format
                if line.startswith('#') or line.startswith('Date:'):
                    # Extract date if present
                    pass
                else:
                    if 'title' not in current_article:
                        current_article = {
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'title': line,
                            'description': '',
                            'content': line,
                            'source': 'Manual',
                            'url': ''
                        }

            if current_article:
                articles.append(current_article)

            return pd.DataFrame(articles)

        except Exception as e:
            print(f"Error loading existing news: {e}")
            return pd.DataFrame()

    def scrape_all(self, days_back: int = 30) -> pd.DataFrame:
        """
        Scrape news from all configured sources

        Args:
            days_back: Number of days to look back

        Returns:
            Combined DataFrame from all sources
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        print(f"Scraping news from {start_str} to {end_str}...")

        all_news = []

        # Scrape from NewsAPI
        print("Scraping NewsAPI...")
        newsapi_df = self.scrape_newsapi(start_str, end_str)
        if not newsapi_df.empty:
            all_news.append(newsapi_df)
            print(f"  Found {len(newsapi_df)} articles from NewsAPI")

        # Scrape from Finviz
        print("Scraping Finviz...")
        finviz_df = self.scrape_finviz_news()
        if not finviz_df.empty:
            all_news.append(finviz_df)
            print(f"  Found {len(finviz_df)} articles from Finviz")

        # Load existing news
        print("Loading existing news file...")
        existing_df = self.load_existing_news()
        if not existing_df.empty:
            all_news.append(existing_df)
            print(f"  Found {len(existing_df)} articles from file")

        # Combine all sources
        if all_news:
            combined_df = pd.concat(all_news, ignore_index=True)

            # Remove duplicates based on title
            combined_df = combined_df.drop_duplicates(subset=['title'], keep='first')

            # Sort by date
            combined_df = combined_df.sort_values('date').reset_index(drop=True)

            print(f"\nTotal unique articles: {len(combined_df)}")

            return combined_df
        else:
            print("No news articles found.")
            return pd.DataFrame()

    def save_news(self, df: pd.DataFrame, filename: str = "news_data.csv"):
        """Save news data to CSV file"""
        filepath = os.path.join(self.raw_data_path, filename)
        df.to_csv(filepath, index=False)
        print(f"Saved {len(df)} articles to {filepath}")


if __name__ == "__main__":
    # Example usage
    scraper = NewsScraper()
    news_df = scraper.scrape_all(days_back=90)

    if not news_df.empty:
        scraper.save_news(news_df)
        print("\nSample articles:")
        print(news_df.head())
