"""
Helper Utilities
Common utility functions for the project
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os


def setup_plotting_style():
    """Set up consistent plotting style"""
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['font.size'] = 10


def plot_sentiment_over_time(sentiment_df: pd.DataFrame,
                            date_col: str = 'date',
                            sentiment_col: str = 'sentiment_compound_mean',
                            save_path: Optional[str] = None):
    """
    Plot sentiment scores over time

    Args:
        sentiment_df: DataFrame with sentiment data
        date_col: Column name for dates
        sentiment_col: Column name for sentiment scores
        save_path: Optional path to save the plot
    """
    setup_plotting_style()

    fig, ax = plt.subplots(figsize=(14, 6))

    # Convert date to datetime
    sentiment_df[date_col] = pd.to_datetime(sentiment_df[date_col])

    # Plot sentiment
    ax.plot(sentiment_df[date_col], sentiment_df[sentiment_col],
           label='Daily Sentiment', linewidth=2)

    # Add horizontal line at 0
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Neutral')

    # Add rolling average if available
    if 'sentiment_ma5' in sentiment_df.columns:
        ax.plot(sentiment_df[date_col], sentiment_df['sentiment_ma5'],
               label='5-day MA', linewidth=1.5, alpha=0.7)

    ax.set_xlabel('Date')
    ax.set_ylabel('Sentiment Score')
    ax.set_title('News Sentiment Over Time')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")

    plt.show()


def plot_price_and_sentiment(combined_df: pd.DataFrame,
                            date_col: str = 'date',
                            price_col: str = 'close',
                            sentiment_col: str = 'sentiment_compound_mean',
                            save_path: Optional[str] = None):
    """
    Plot price and sentiment on dual y-axis

    Args:
        combined_df: DataFrame with both price and sentiment
        date_col: Column name for dates
        price_col: Column name for prices
        sentiment_col: Column name for sentiment
        save_path: Optional path to save the plot
    """
    setup_plotting_style()

    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Convert date to datetime
    combined_df[date_col] = pd.to_datetime(combined_df[date_col])

    # Plot price
    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('S&P 500 Price', color=color)
    ax1.plot(combined_df[date_col], combined_df[price_col],
            color=color, linewidth=2, label='Price')
    ax1.tick_params(axis='y', labelcolor=color)

    # Create second y-axis for sentiment
    ax2 = ax1.twinx()
    color = 'tab:orange'
    ax2.set_ylabel('Sentiment Score', color=color)
    ax2.plot(combined_df[date_col], combined_df[sentiment_col],
            color=color, linewidth=2, alpha=0.7, label='Sentiment')
    ax2.axhline(y=0, color='red', linestyle='--', alpha=0.3)
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('S&P 500 Price vs News Sentiment')
    fig.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")

    plt.show()


def plot_confusion_matrix(cm: np.ndarray,
                         labels: List[str] = ['Down', 'Up'],
                         save_path: Optional[str] = None):
    """
    Plot confusion matrix

    Args:
        cm: Confusion matrix
        labels: Class labels
        save_path: Optional path to save the plot
    """
    setup_plotting_style()

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
               xticklabels=labels, yticklabels=labels)
    plt.title('Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")

    plt.show()


def plot_feature_importance(feature_importance_df: pd.DataFrame,
                           top_n: int = 20,
                           save_path: Optional[str] = None):
    """
    Plot feature importance

    Args:
        feature_importance_df: DataFrame with features and importance scores
        top_n: Number of top features to show
        save_path: Optional path to save the plot
    """
    setup_plotting_style()

    top_features = feature_importance_df.head(top_n)

    plt.figure(figsize=(10, 8))
    plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Importance')
    plt.title(f'Top {top_n} Most Important Features')
    plt.gca().invert_yaxis()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")

    plt.show()


def plot_prediction_performance(predictions_df: pd.DataFrame,
                               date_col: str = 'date',
                               actual_col: str = 'target',
                               pred_col: str = 'predicted_direction',
                               save_path: Optional[str] = None):
    """
    Plot prediction performance over time

    Args:
        predictions_df: DataFrame with predictions and actuals
        date_col: Column name for dates
        actual_col: Column name for actual values
        pred_col: Column name for predictions
        save_path: Optional path to save the plot
    """
    setup_plotting_style()

    predictions_df[date_col] = pd.to_datetime(predictions_df[date_col])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # Plot 1: Actual vs Predicted
    ax1.plot(predictions_df[date_col], predictions_df[actual_col],
            label='Actual', marker='o', markersize=3)
    ax1.plot(predictions_df[date_col], predictions_df[pred_col],
            label='Predicted', marker='x', markersize=3, alpha=0.7)
    ax1.set_ylabel('Direction (0=Down, 1=Up)')
    ax1.set_title('Actual vs Predicted Market Direction')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Accuracy over time (rolling)
    correct = (predictions_df[actual_col] == predictions_df[pred_col]).astype(int)
    rolling_accuracy = correct.rolling(window=20).mean()

    ax2.plot(predictions_df[date_col], rolling_accuracy, linewidth=2)
    ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Random Guess')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Accuracy')
    ax2.set_title('Rolling 20-Day Accuracy')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")

    plt.show()


def calculate_summary_statistics(df: pd.DataFrame) -> Dict:
    """
    Calculate summary statistics for the dataset

    Args:
        df: Input dataframe

    Returns:
        Dictionary with statistics
    """
    stats = {
        'total_rows': len(df),
        'date_range': f"{df['date'].min()} to {df['date'].max()}" if 'date' in df.columns else 'N/A',
        'missing_values': df.isnull().sum().sum(),
        'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
        'categorical_columns': len(df.select_dtypes(include=['object']).columns)
    }

    return stats


def print_dataset_info(df: pd.DataFrame, name: str = "Dataset"):
    """
    Print information about a dataset

    Args:
        df: Input dataframe
        name: Name of the dataset
    """
    print(f"\n{'='*50}")
    print(f"{name} Information")
    print(f"{'='*50}")

    stats = calculate_summary_statistics(df)

    print(f"Total Rows: {stats['total_rows']}")
    print(f"Total Columns: {len(df.columns)}")
    print(f"Date Range: {stats['date_range']}")
    print(f"Missing Values: {stats['missing_values']}")
    print(f"Numeric Columns: {stats['numeric_columns']}")
    print(f"Categorical Columns: {stats['categorical_columns']}")

    print(f"\nColumn Names:")
    for col in df.columns:
        dtype = df[col].dtype
        non_null = df[col].count()
        print(f"  {col:30s} {str(dtype):15s} {non_null} non-null")

    print(f"{'='*50}\n")


def create_data_report(news_df: pd.DataFrame,
                      price_df: pd.DataFrame,
                      sentiment_df: pd.DataFrame,
                      features_df: pd.DataFrame,
                      save_path: str = "data_report.txt"):
    """
    Create a comprehensive data report

    Args:
        news_df: News dataframe
        price_df: Price dataframe
        sentiment_df: Sentiment dataframe
        features_df: Features dataframe
        save_path: Path to save the report
    """
    with open(save_path, 'w') as f:
        f.write("="*70 + "\n")
        f.write("S&P 500 PRICE PREDICTION PROJECT - DATA REPORT\n")
        f.write("="*70 + "\n\n")
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # News data
        f.write("NEWS DATA\n")
        f.write("-"*70 + "\n")
        f.write(f"Total Articles: {len(news_df)}\n")
        if 'date' in news_df.columns:
            f.write(f"Date Range: {news_df['date'].min()} to {news_df['date'].max()}\n")
        if 'source' in news_df.columns:
            f.write(f"Sources: {news_df['source'].nunique()}\n")
        f.write("\n")

        # Price data
        f.write("PRICE DATA\n")
        f.write("-"*70 + "\n")
        f.write(f"Total Days: {len(price_df)}\n")
        if 'date' in price_df.columns:
            f.write(f"Date Range: {price_df['date'].min()} to {price_df['date'].max()}\n")
        if 'close' in price_df.columns:
            f.write(f"Price Range: ${price_df['close'].min():.2f} - ${price_df['close'].max():.2f}\n")
        f.write("\n")

        # Sentiment data
        f.write("SENTIMENT DATA\n")
        f.write("-"*70 + "\n")
        f.write(f"Total Days: {len(sentiment_df)}\n")
        if 'sentiment_compound_mean' in sentiment_df.columns:
            f.write(f"Average Sentiment: {sentiment_df['sentiment_compound_mean'].mean():.4f}\n")
            f.write(f"Sentiment Range: {sentiment_df['sentiment_compound_mean'].min():.4f} to ")
            f.write(f"{sentiment_df['sentiment_compound_mean'].max():.4f}\n")
        f.write("\n")

        # Features data
        f.write("FEATURES DATA\n")
        f.write("-"*70 + "\n")
        f.write(f"Total Samples: {len(features_df)}\n")
        f.write(f"Total Features: {len(features_df.columns)}\n")
        if 'target' in features_df.columns:
            target_dist = features_df['target'].value_counts()
            f.write(f"Target Distribution:\n")
            f.write(f"  Down (0): {target_dist.get(0, 0)} ({target_dist.get(0, 0)/len(features_df)*100:.1f}%)\n")
            f.write(f"  Up (1): {target_dist.get(1, 0)} ({target_dist.get(1, 0)/len(features_df)*100:.1f}%)\n")
        f.write("\n")

        f.write("="*70 + "\n")

    print(f"Data report saved to {save_path}")


if __name__ == "__main__":
    print("Helper Utilities Module")
    print("Functions for visualization and analysis")
