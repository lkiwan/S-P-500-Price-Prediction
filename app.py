"""
Professional S&P 500 Prediction Dashboard
Flask Backend Application
"""

from flask import Flask, render_template, jsonify, request, send_file
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
import json
from io import BytesIO
import base64

# Add src to path
sys.path.append('src')

app = Flask(__name__)

# Configuration
DATA_DIR = 'data'
MODELS_DIR = 'models'
PREDICTIONS_FILE = 'predictions_history.csv'
FEATURES_FILE = 'data/features/features_complete.csv'
PRICE_FILE = 'data/raw/price_data.csv'


@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/latest_prediction')
def get_latest_prediction():
    """Get the latest prediction"""
    try:
        if os.path.exists(PREDICTIONS_FILE):
            df = pd.read_csv(PREDICTIONS_FILE)
            if len(df) > 0:
                latest = df.iloc[-1].to_dict()
                return jsonify({
                    'success': True,
                    'prediction': {
                        'date': latest['prediction_date'],
                        'data_date': latest['data_date'],
                        'direction': latest['direction'],
                        'confidence': float(latest['confidence']),
                        'prob_up': float(latest['prob_up']),
                        'prob_down': float(latest['prob_down'])
                    }
                })

        return jsonify({'success': False, 'message': 'No predictions yet'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/prediction_history')
def get_prediction_history():
    """Get prediction history for charts - Monthly aggregated for last 12 months"""
    try:
        if not os.path.exists(PREDICTIONS_FILE):
            return jsonify({'success': False, 'message': 'No history yet'})

        df = pd.read_csv(PREDICTIONS_FILE)

        # Convert to datetime
        df['prediction_date'] = pd.to_datetime(df['prediction_date'])

        # Get last 12 months
        twelve_months_ago = datetime.now() - timedelta(days=365)
        df_recent = df[df['prediction_date'] >= twelve_months_ago]

        if len(df_recent) == 0:
            # If no data in last 12 months, return all data
            df_recent = df

        # Group by month
        df_recent['month'] = df_recent['prediction_date'].dt.to_period('M')

        monthly_stats = df_recent.groupby('month').agg({
            'confidence': 'mean',
            'direction': lambda x: (x == 'UP').sum(),  # Count UP predictions
            'prob_up': 'mean',
            'prob_down': 'mean'
        }).reset_index()

        # Calculate total predictions per month
        monthly_counts = df_recent.groupby('month').size().reset_index(name='total_predictions')
        monthly_stats = monthly_stats.merge(monthly_counts, on='month')

        # Calculate percentage of UP predictions
        monthly_stats['up_percentage'] = (monthly_stats['direction'] / monthly_stats['total_predictions']) * 100

        # Format month names
        monthly_stats['month_str'] = monthly_stats['month'].astype(str)

        history = {
            'months': monthly_stats['month_str'].tolist(),
            'avg_confidence': monthly_stats['confidence'].tolist(),
            'up_count': monthly_stats['direction'].tolist(),
            'total_predictions': monthly_stats['total_predictions'].tolist(),
            'up_percentage': monthly_stats['up_percentage'].tolist(),
            'avg_prob_up': monthly_stats['prob_up'].tolist(),
            'avg_prob_down': monthly_stats['prob_down'].tolist()
        }

        return jsonify({'success': True, 'history': history})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/performance_metrics')
def get_performance_metrics():
    """Calculate and return performance metrics"""
    try:
        # Load predictions
        if not os.path.exists(PREDICTIONS_FILE):
            return jsonify({'success': False, 'message': 'No predictions yet'})

        pred_df = pd.read_csv(PREDICTIONS_FILE)

        # Load actual prices
        if not os.path.exists(PRICE_FILE):
            return jsonify({'success': False, 'message': 'No price data'})

        price_df = pd.read_csv(PRICE_FILE)
        price_df['date'] = pd.to_datetime(price_df['date'])

        # Calculate accuracy (simplified version)
        total_predictions = len(pred_df)

        # Calculate average confidence
        avg_confidence = pred_df['confidence'].mean()

        # Count up/down predictions
        up_predictions = len(pred_df[pred_df['direction'] == 'UP'])
        down_predictions = len(pred_df[pred_df['direction'] == 'DOWN'])

        # Get high confidence predictions
        high_conf = len(pred_df[pred_df['confidence'] >= 0.70])
        medium_conf = len(pred_df[(pred_df['confidence'] >= 0.60) & (pred_df['confidence'] < 0.70)])
        low_conf = len(pred_df[pred_df['confidence'] < 0.60])

        metrics = {
            'total_predictions': int(total_predictions),
            'avg_confidence': float(avg_confidence),
            'up_predictions': int(up_predictions),
            'down_predictions': int(down_predictions),
            'high_confidence_count': int(high_conf),
            'medium_confidence_count': int(medium_conf),
            'low_confidence_count': int(low_conf),
            'model_accuracy': 63.64,  # From backtest
            'backtest_accuracy': 63.64,
            'edge_over_random': 13.64
        }

        return jsonify({'success': True, 'metrics': metrics})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/recent_predictions_table')
def get_recent_predictions_table():
    """Get recent predictions for table display"""
    try:
        if not os.path.exists(PREDICTIONS_FILE):
            return jsonify({'success': False, 'message': 'No predictions yet'})

        df = pd.read_csv(PREDICTIONS_FILE)

        # Get last 10 predictions
        df_recent = df.tail(10).sort_values('prediction_date', ascending=False)

        predictions = []
        for _, row in df_recent.iterrows():
            predictions.append({
                'date': row['prediction_date'],
                'direction': row['direction'],
                'confidence': float(row['confidence']),
                'prob_up': float(row['prob_up']),
                'prob_down': float(row['prob_down'])
            })

        return jsonify({'success': True, 'predictions': predictions})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sentiment_data')
def get_sentiment_data():
    """Get sentiment analysis data"""
    try:
        # Try to load sentiment data
        sentiment_files = [
            'data/processed/sentiment_daily_real.csv',
            'data/processed/sentiment_daily.csv'
        ]

        sentiment_df = None
        for file in sentiment_files:
            if os.path.exists(file):
                sentiment_df = pd.read_csv(file)
                break

        if sentiment_df is None:
            return jsonify({'success': False, 'message': 'No sentiment data'})

        # Get last 30 days
        sentiment_df = sentiment_df.tail(30)

        data = {
            'dates': sentiment_df['date'].tolist(),
            'sentiment': sentiment_df['sentiment_compound_mean'].tolist() if 'sentiment_compound_mean' in sentiment_df.columns else []
        }

        return jsonify({'success': True, 'sentiment': data})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/run_prediction', methods=['POST'])
def run_prediction():
    """Trigger a new prediction"""
    try:
        # Import the predict module
        from models.predict import Predictor

        # Check if model exists
        model_name = "sp500_complete_20251113"
        model_path = f"models/{model_name}.pkl"

        if not os.path.exists(model_path):
            return jsonify({
                'success': False,
                'error': 'Model not found. Run: python run_complete_pipeline.py'
            })

        # Load features
        if not os.path.exists(FEATURES_FILE):
            return jsonify({
                'success': False,
                'error': 'Features not found. Run: python run_complete_pipeline.py'
            })

        features_df = pd.read_csv(FEATURES_FILE)
        latest = features_df.tail(1)

        # Make prediction
        predictor = Predictor(model_name=model_name)
        result = predictor.predict(latest)

        if result:
            # Save to history
            save_prediction_to_history(result, latest['date'].values[0])

            return jsonify({
                'success': True,
                'prediction': {
                    'direction': result['direction'],
                    'confidence': result['confidence'],
                    'prob_up': result['probability_up'],
                    'prob_down': result['probability_down'],
                    'timestamp': result['timestamp']
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Prediction failed'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def save_prediction_to_history(result, data_date):
    """Save prediction to history file"""
    try:
        new_record = {
            'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_date': data_date,
            'direction': result['direction'],
            'confidence': result['confidence'],
            'prob_up': result['probability_up'],
            'prob_down': result['probability_down']
        }

        if os.path.exists(PREDICTIONS_FILE):
            df = pd.read_csv(PREDICTIONS_FILE)
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        else:
            df = pd.DataFrame([new_record])

        df.to_csv(PREDICTIONS_FILE, index=False)

    except Exception as e:
        print(f"Error saving prediction: {e}")


@app.route('/api/market_status')
def get_market_status():
    """Get current market status"""
    try:
        if not os.path.exists(PRICE_FILE):
            return jsonify({'success': False, 'message': 'No price data'})

        df = pd.read_csv(PRICE_FILE)
        df['date'] = pd.to_datetime(df['date'])

        # Get latest price
        latest = df.iloc[-1]
        previous = df.iloc[-2]

        current_price = float(latest['close'])
        prev_price = float(previous['close'])
        change = current_price - prev_price
        change_pct = (change / prev_price) * 100

        status = {
            'current_price': current_price,
            'change': change,
            'change_pct': change_pct,
            'date': latest['date'].strftime('%Y-%m-%d') if hasattr(latest['date'], 'strftime') else str(latest['date'])
        }

        return jsonify({'success': True, 'market': status})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/report')
def project_report():
    """Project report and analysis page"""
    return render_template('report.html')


@app.route('/api/accuracy_stats')
def get_accuracy_stats():
    """Get prediction accuracy statistics"""
    try:
        accuracy_file = 'predictions_with_accuracy.csv'

        if not os.path.exists(accuracy_file):
            return jsonify({'success': False, 'message': 'Accuracy data not calculated yet'})

        df = pd.read_csv(accuracy_file)

        # Overall stats
        total = len(df)
        correct = df['is_correct'].sum()
        accuracy = (correct / total) * 100 if total > 0 else 0

        # By confidence level
        high_conf = df[df['confidence'] >= 0.70]
        medium_conf = df[(df['confidence'] >= 0.60) & (df['confidence'] < 0.70)]
        low_conf = df[df['confidence'] < 0.60]

        stats = {
            'overall_accuracy': accuracy,
            'total_predictions': int(total),
            'correct_predictions': int(correct),
            'wrong_predictions': int(total - correct),
            'high_confidence': {
                'accuracy': (high_conf['is_correct'].sum() / len(high_conf) * 100) if len(high_conf) > 0 else 0,
                'count': int(len(high_conf)),
                'correct': int(high_conf['is_correct'].sum())
            },
            'medium_confidence': {
                'accuracy': (medium_conf['is_correct'].sum() / len(medium_conf) * 100) if len(medium_conf) > 0 else 0,
                'count': int(len(medium_conf)),
                'correct': int(medium_conf['is_correct'].sum())
            },
            'low_confidence': {
                'accuracy': (low_conf['is_correct'].sum() / len(low_conf) * 100) if len(low_conf) > 0 else 0,
                'count': int(len(low_conf)),
                'correct': int(low_conf['is_correct'].sum())
            }
        }

        return jsonify({'success': True, 'stats': stats})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/predictions_with_accuracy')
def get_predictions_with_accuracy():
    """Get predictions with accuracy results"""
    try:
        accuracy_file = 'predictions_with_accuracy.csv'

        if not os.path.exists(accuracy_file):
            return jsonify({'success': False, 'message': 'Accuracy data not calculated yet'})

        df = pd.read_csv(accuracy_file)

        # Get last 20 predictions with accuracy
        df_recent = df.tail(20).sort_values('prediction_date', ascending=False)

        predictions = []
        for _, row in df_recent.iterrows():
            predictions.append({
                'date': row['prediction_date'],
                'predicted': row['predicted_direction'],
                'actual': row['actual_direction'],
                'confidence': float(row['confidence']),
                'is_correct': bool(row['is_correct']),
                'actual_return': float(row['actual_return'])
            })

        return jsonify({'success': True, 'predictions': predictions})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/feature_importance')
def get_feature_importance():
    """Get feature importance from the trained model"""
    try:
        import pickle
        model_name = "sp500_complete_20251113"
        model_path = f"models/{model_name}.pkl"

        if not os.path.exists(model_path):
            return jsonify({'success': False, 'message': 'Model not found'})

        # Load model
        with open(model_path, 'rb') as f:
            model = pickle.load(f)

        # Load features to get feature names
        if not os.path.exists(FEATURES_FILE):
            return jsonify({'success': False, 'message': 'Features file not found'})

        features_df = pd.read_csv(FEATURES_FILE)
        # Exclude target columns and basic price columns
        exclude_cols = ['date', 'target', 'target_binary', 'target_multiclass', 'close', 'high', 'low', 'open', 'volume', 'return', 'direction']
        feature_names = [col for col in features_df.columns if col not in exclude_cols]

        # Get feature importance
        importance = model.feature_importances_

        # Create dataframe and sort
        feature_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False).head(15)

        data = {
            'features': feature_df['feature'].tolist(),
            'importance': feature_df['importance'].tolist()
        }

        return jsonify({'success': True, 'data': data})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/trading_simulation')
def get_trading_simulation():
    """Calculate trading simulation results"""
    try:
        accuracy_file = 'predictions_with_accuracy.csv'

        if not os.path.exists(accuracy_file):
            return jsonify({'success': False, 'message': 'Accuracy data not available'})

        df = pd.read_csv(accuracy_file)
        df['prediction_date'] = pd.to_datetime(df['prediction_date'])
        df = df.sort_values('prediction_date')

        # Trading simulation parameters
        initial_capital = 10000
        capital = initial_capital
        position_size = 0.5  # 50% of capital per trade

        trades = []
        capital_history = [initial_capital]

        for _, row in df.iterrows():
            if row['predicted_direction'] == 'UP':
                # Buy signal
                investment = capital * position_size
                returns = row['actual_return'] / 100
                profit = investment * returns
                capital += profit

                trades.append({
                    'date': row['prediction_date'],
                    'action': 'BUY',
                    'return': row['actual_return'],
                    'profit': profit,
                    'capital': capital
                })
            else:
                # Hold or short (we'll just hold)
                trades.append({
                    'date': row['prediction_date'],
                    'action': 'HOLD',
                    'return': 0,
                    'profit': 0,
                    'capital': capital
                })

            capital_history.append(capital)

        # Calculate metrics
        total_return = ((capital - initial_capital) / initial_capital) * 100
        winning_trades = len([t for t in trades if t.get('profit', 0) > 0])
        losing_trades = len([t for t in trades if t.get('profit', 0) < 0])
        total_trades = winning_trades + losing_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        # Buy and hold comparison
        if os.path.exists(PRICE_FILE):
            price_df = pd.read_csv(PRICE_FILE)
            price_df['date'] = pd.to_datetime(price_df['date'])

            # Get price range for predictions
            start_date = df['data_date'].min()
            end_date = df['data_date'].max()

            price_range = price_df[(price_df['date'] >= start_date) & (price_df['date'] <= end_date)]

            if len(price_range) > 1:
                buy_hold_return = ((price_range.iloc[-1]['close'] - price_range.iloc[0]['close']) /
                                  price_range.iloc[0]['close']) * 100
            else:
                buy_hold_return = 0
        else:
            buy_hold_return = 0

        results = {
            'initial_capital': initial_capital,
            'final_capital': capital,
            'total_return': total_return,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'buy_hold_return': buy_hold_return,
            'outperformance': total_return - buy_hold_return,
            'total_trades': total_trades,
            'dates': [t['date'].strftime('%Y-%m-%d') if isinstance(t['date'], pd.Timestamp) else str(t['date']) for t in trades],
            'capital_history': capital_history
        }

        return jsonify({'success': True, 'simulation': results})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/rolling_accuracy')
def get_rolling_accuracy():
    """Calculate rolling accuracy metrics"""
    try:
        accuracy_file = 'predictions_with_accuracy.csv'

        if not os.path.exists(accuracy_file):
            return jsonify({'success': False, 'message': 'Accuracy data not available'})

        df = pd.read_csv(accuracy_file)
        df['prediction_date'] = pd.to_datetime(df['prediction_date'])
        df = df.sort_values('prediction_date')

        # Calculate rolling accuracies
        windows = [7, 30, 90]
        rolling_data = {}

        for window in windows:
            if len(df) >= window:
                rolling_acc = []
                for i in range(window - 1, len(df)):
                    window_data = df.iloc[i - window + 1:i + 1]
                    acc = (window_data['is_correct'].sum() / len(window_data)) * 100
                    rolling_acc.append(acc)

                rolling_data[f'{window}d'] = {
                    'values': rolling_acc,
                    'current': rolling_acc[-1] if rolling_acc else 0,
                    'avg': sum(rolling_acc) / len(rolling_acc) if rolling_acc else 0
                }
            else:
                rolling_data[f'{window}d'] = {
                    'values': [],
                    'current': 0,
                    'avg': 0
                }

        # Overall accuracy
        overall_acc = (df['is_correct'].sum() / len(df)) * 100 if len(df) > 0 else 0

        results = {
            'overall_accuracy': overall_acc,
            'rolling_7d': rolling_data.get('7d', {}),
            'rolling_30d': rolling_data.get('30d', {}),
            'rolling_90d': rolling_data.get('90d', {}),
            'total_predictions': len(df)
        }

        return jsonify({'success': True, 'accuracy': results})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/economic_indicators')
def get_economic_indicators():
    """Get current economic indicators"""
    try:
        if not os.path.exists(FEATURES_FILE):
            return jsonify({'success': False, 'message': 'Features not found'})

        df = pd.read_csv(FEATURES_FILE)
        latest = df.iloc[-1]

        # Get previous values for trends
        prev = df.iloc[-2] if len(df) > 1 else latest

        indicators = {
            'fed_funds_rate': {
                'value': float(latest['fed_funds_rate']) if 'fed_funds_rate' in df.columns else 0,
                'change': float(latest['fed_funds_rate'] - prev['fed_funds_rate']) if 'fed_funds_rate' in df.columns else 0,
                'label': 'Fed Funds Rate'
            },
            'unemployment_rate': {
                'value': float(latest['unemployment_rate']) if 'unemployment_rate' in df.columns else 0,
                'change': float(latest['unemployment_rate'] - prev['unemployment_rate']) if 'unemployment_rate' in df.columns else 0,
                'label': 'Unemployment Rate'
            },
            'cpi': {
                'value': float(latest['cpi']) if 'cpi' in df.columns else 0,
                'change': float(latest['cpi'] - prev['cpi']) if 'cpi' in df.columns else 0,
                'label': 'CPI (Inflation)'
            },
            'vix': {
                'value': float(latest['vix']) if 'vix' in df.columns else 0,
                'change': float(latest['vix'] - prev['vix']) if 'vix' in df.columns else 0,
                'label': 'VIX (Fear Index)'
            },
            'treasury_10y': {
                'value': float(latest['treasury_10y']) if 'treasury_10y' in df.columns else 0,
                'change': float(latest['treasury_10y'] - prev['treasury_10y']) if 'treasury_10y' in df.columns else 0,
                'label': '10Y Treasury'
            },
            'yield_curve': {
                'value': float(latest['yield_curve']) if 'yield_curve' in df.columns else 0,
                'change': float(latest['yield_curve'] - prev['yield_curve']) if 'yield_curve' in df.columns else 0,
                'label': 'Yield Curve'
            }
        }

        return jsonify({'success': True, 'indicators': indicators})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/technical_indicators')
def get_technical_indicators():
    """Get technical indicators for charting"""
    try:
        if not os.path.exists(FEATURES_FILE):
            return jsonify({'success': False, 'message': 'Features not found'})

        df = pd.read_csv(FEATURES_FILE)
        df['date'] = pd.to_datetime(df['date'])

        # Get last 60 days
        df_recent = df.tail(60)

        data = {
            'dates': df_recent['date'].dt.strftime('%Y-%m-%d').tolist(),
            'close': df_recent['close'].tolist() if 'close' in df.columns else [],
            'sma_20': df_recent['sma_20'].tolist() if 'sma_20' in df.columns else [],
            'sma_50': df_recent['sma_50'].tolist() if 'sma_50' in df.columns else [],
            'bb_upper': df_recent['bb_upper'].tolist() if 'bb_upper' in df.columns else [],
            'bb_lower': df_recent['bb_lower'].tolist() if 'bb_lower' in df.columns else [],
            'rsi': df_recent['rsi_14'].tolist() if 'rsi_14' in df.columns else [],
            'macd': df_recent['macd'].tolist() if 'macd' in df.columns else [],
            'macd_signal': df_recent['macd_signal'].tolist() if 'macd_signal' in df.columns else [],
            'volume': df_recent['volume'].tolist() if 'volume' in df.columns else []
        }

        return jsonify({'success': True, 'data': data})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/recent_news')
def get_recent_news():
    """Get recent analyzed news"""
    try:
        # Try to load sentiment data with news
        news_file = 'data/processed/sentiment_daily_real.csv'

        if not os.path.exists(news_file):
            news_file = 'data/processed/sentiment_daily.csv'

        if not os.path.exists(news_file):
            return jsonify({'success': False, 'message': 'News data not found'})

        df = pd.read_csv(news_file)
        df['date'] = pd.to_datetime(df['date'])

        # Get last 10 days
        df_recent = df.tail(10).sort_values('date', ascending=False)

        news_items = []
        for _, row in df_recent.iterrows():
            sentiment_score = row['sentiment_compound_mean'] if 'sentiment_compound_mean' in df.columns else 0
            news_count = row['news_count'] if 'news_count' in df.columns else 0

            # Determine sentiment category
            if sentiment_score > 0.1:
                sentiment_label = 'Positive'
                sentiment_class = 'success'
            elif sentiment_score < -0.1:
                sentiment_label = 'Negative'
                sentiment_class = 'danger'
            else:
                sentiment_label = 'Neutral'
                sentiment_class = 'secondary'

            news_items.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'sentiment_score': float(sentiment_score),
                'sentiment_label': sentiment_label,
                'sentiment_class': sentiment_class,
                'news_count': int(news_count),
                'headline': f'{int(news_count)} articles analyzed'
            })

        return jsonify({'success': True, 'news': news_items})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/confusion_matrix')
def get_confusion_matrix():
    """Get confusion matrix data"""
    try:
        accuracy_file = 'predictions_with_accuracy.csv'

        if not os.path.exists(accuracy_file):
            return jsonify({'success': False, 'message': 'Accuracy data not available'})

        df = pd.read_csv(accuracy_file)

        # Calculate confusion matrix
        true_positives = len(df[(df['predicted_direction'] == 'UP') & (df['actual_direction'] == 'UP')])
        false_positives = len(df[(df['predicted_direction'] == 'UP') & (df['actual_direction'] == 'DOWN')])
        true_negatives = len(df[(df['predicted_direction'] == 'DOWN') & (df['actual_direction'] == 'DOWN')])
        false_negatives = len(df[(df['predicted_direction'] == 'DOWN') & (df['actual_direction'] == 'UP')])

        total = len(df)

        # Calculate metrics
        accuracy = ((true_positives + true_negatives) / total * 100) if total > 0 else 0
        precision = (true_positives / (true_positives + false_positives) * 100) if (true_positives + false_positives) > 0 else 0
        recall = (true_positives / (true_positives + false_negatives) * 100) if (true_positives + false_negatives) > 0 else 0
        f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0

        matrix = {
            'true_positives': int(true_positives),
            'false_positives': int(false_positives),
            'true_negatives': int(true_negatives),
            'false_negatives': int(false_negatives),
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1_score),
            'total': int(total)
        }

        return jsonify({'success': True, 'matrix': matrix})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/risk_metrics')
def get_risk_metrics():
    """Calculate risk and performance metrics"""
    try:
        accuracy_file = 'predictions_with_accuracy.csv'

        if not os.path.exists(accuracy_file):
            return jsonify({'success': False, 'message': 'Accuracy data not available'})

        df = pd.read_csv(accuracy_file)
        df['prediction_date'] = pd.to_datetime(df['prediction_date'])
        df = df.sort_values('prediction_date')

        # Calculate returns assuming 50% position size
        df['strategy_return'] = 0.0
        df.loc[df['predicted_direction'] == 'UP', 'strategy_return'] = df['actual_return'] * 0.5

        # Cumulative returns
        cumulative_returns = (1 + df['strategy_return'] / 100).cumprod()

        # Calculate drawdown
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max * 100
        max_drawdown = drawdown.min()

        # Calculate Sharpe Ratio (annualized, assuming 252 trading days)
        mean_return = df['strategy_return'].mean()
        std_return = df['strategy_return'].std()
        sharpe_ratio = (mean_return / std_return * (252 ** 0.5)) if std_return > 0 else 0

        # Win/Loss streaks
        df['is_win'] = df['strategy_return'] > 0

        current_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        current_win_streak = 0
        current_loss_streak = 0

        for is_win in df['is_win']:
            if is_win:
                current_win_streak += 1
                current_loss_streak = 0
                max_win_streak = max(max_win_streak, current_win_streak)
            else:
                current_loss_streak += 1
                current_win_streak = 0
                max_loss_streak = max(max_loss_streak, current_loss_streak)

        # Get current streak
        last_predictions = df.tail(5)
        current_streak_type = 'win' if last_predictions['is_win'].iloc[-1] else 'loss'
        current_streak_count = 1

        for i in range(len(last_predictions) - 2, -1, -1):
            if last_predictions['is_win'].iloc[i] == last_predictions['is_win'].iloc[-1]:
                current_streak_count += 1
            else:
                break

        # Total wins/losses
        total_wins = df['is_win'].sum()
        total_losses = len(df) - total_wins

        metrics = {
            'max_drawdown': float(max_drawdown),
            'sharpe_ratio': float(sharpe_ratio),
            'max_win_streak': int(max_win_streak),
            'max_loss_streak': int(max_loss_streak),
            'current_streak_type': current_streak_type,
            'current_streak_count': int(current_streak_count),
            'total_wins': int(total_wins),
            'total_losses': int(total_losses),
            'avg_win_return': float(df[df['is_win']]['strategy_return'].mean()) if total_wins > 0 else 0,
            'avg_loss_return': float(df[~df['is_win']]['strategy_return'].mean()) if total_losses > 0 else 0
        }

        return jsonify({'success': True, 'metrics': metrics})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/best_worst_predictions')
def get_best_worst_predictions():
    """Get best and worst predictions"""
    try:
        accuracy_file = 'predictions_with_accuracy.csv'

        if not os.path.exists(accuracy_file):
            return jsonify({'success': False, 'message': 'Accuracy data not available'})

        df = pd.read_csv(accuracy_file)
        df['prediction_date'] = pd.to_datetime(df['prediction_date'])

        # Calculate absolute return (for impact)
        df['abs_return'] = df['actual_return'].abs()

        # Best predictions (correct AND high impact)
        best_correct = df[df['is_correct'] == True].nlargest(5, 'abs_return')

        # Worst predictions (incorrect AND high impact)
        worst_incorrect = df[df['is_correct'] == False].nlargest(5, 'abs_return')

        def format_prediction(row):
            return {
                'date': row['prediction_date'].strftime('%Y-%m-%d') if isinstance(row['prediction_date'], pd.Timestamp) else str(row['prediction_date']),
                'predicted': row['predicted_direction'],
                'actual': row['actual_direction'],
                'confidence': float(row['confidence']),
                'actual_return': float(row['actual_return']),
                'is_correct': bool(row['is_correct'])
            }

        best = [format_prediction(row) for _, row in best_correct.iterrows()]
        worst = [format_prediction(row) for _, row in worst_incorrect.iterrows()]

        return jsonify({
            'success': True,
            'best': best,
            'worst': worst
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/ai_explanation')
def get_ai_explanation():
    """Get AI explanation for the latest prediction showing feature contributions"""
    try:
        import pickle
        import numpy as np

        model_name = "sp500_complete_20251113"
        model_path = f"models/{model_name}.pkl"

        if not os.path.exists(model_path):
            return jsonify({'success': False, 'message': 'Model not found'})

        # Load model
        with open(model_path, 'rb') as f:
            model = pickle.load(f)

        # Load features
        if not os.path.exists(FEATURES_FILE):
            return jsonify({'success': False, 'message': 'Features file not found'})

        features_df = pd.read_csv(FEATURES_FILE)

        # Get latest feature values
        latest_features = features_df.iloc[-1]

        # Exclude target columns and basic price columns
        exclude_cols = ['date', 'target', 'target_binary', 'target_multiclass', 'close', 'high', 'low', 'open', 'volume', 'return', 'direction']
        feature_names = [col for col in features_df.columns if col not in exclude_cols]

        # Get feature importances
        importance = model.feature_importances_

        # Get feature values for latest prediction
        feature_values = [latest_features[name] if name in latest_features else 0 for name in feature_names]

        # Calculate contributions (normalize feature values and multiply by importance)
        # We'll use simple scaling: contribution = feature_value * importance
        contributions = []
        for i, (name, value, imp) in enumerate(zip(feature_names, feature_values, importance)):
            # Simple contribution calculation
            contribution = float(value) * float(imp)
            contributions.append({
                'feature': name,
                'contribution': contribution,
                'importance': float(imp),
                'value': float(value)
            })

        # Sort by absolute contribution and get top 10
        contributions_sorted = sorted(contributions, key=lambda x: abs(x['contribution']), reverse=True)[:10]

        # Format feature names for display (make them more readable)
        def format_feature_name(name):
            # Replace underscores with spaces and capitalize
            return ' '.join(word.capitalize() for word in name.replace('_', ' ').split())

        features_list = []
        for item in contributions_sorted:
            features_list.append({
                'feature': format_feature_name(item['feature']),
                'contribution': item['contribution'],
                'importance': item['importance'],
                'value': item['value'],
                'direction': 'bullish' if item['contribution'] > 0 else 'bearish'
            })

        # Get latest prediction direction
        prediction_direction = 'UP'
        if os.path.exists(PREDICTIONS_FILE):
            pred_df = pd.read_csv(PREDICTIONS_FILE)
            if len(pred_df) > 0:
                prediction_direction = pred_df.iloc[-1]['direction']

        return jsonify({
            'success': True,
            'features': features_list,
            'prediction': prediction_direction
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/candlestick_data')
def get_candlestick_data():
    """Get OHLC data for candlestick chart"""
    try:
        # Get days parameter (default 90)
        days = int(request.args.get('days', 90))

        if not os.path.exists(PRICE_FILE):
            return jsonify({'success': False, 'message': 'Price data not found'})

        df = pd.read_csv(PRICE_FILE)
        df['date'] = pd.to_datetime(df['date'])

        # Get last N days
        df_recent = df.tail(days)

        # Format data for ApexCharts candlestick
        # ApexCharts expects: {x: timestamp, y: [open, high, low, close]}
        candlestick_data = []

        for _, row in df_recent.iterrows():
            candlestick_data.append({
                'x': row['date'].strftime('%Y-%m-%d'),
                'y': [
                    float(row['open']),
                    float(row['high']),
                    float(row['low']),
                    float(row['close'])
                ]
            })

        # Also include volume data
        volume_data = []
        for _, row in df_recent.iterrows():
            volume_data.append({
                'x': row['date'].strftime('%Y-%m-%d'),
                'y': float(row['volume']) if 'volume' in df.columns else 0
            })

        return jsonify({
            'success': True,
            'candlestick': candlestick_data,
            'volume': volume_data,
            'days': days
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/economic_calendar')
def get_economic_calendar():
    """Get upcoming economic events based on realistic scheduling patterns"""
    try:
        from datetime import datetime, timedelta
        import calendar as cal

        today = datetime.now()
        events = []

        # Helper function to find next weekday occurrence
        def next_weekday(start_date, weekday):
            """Find next occurrence of a specific weekday (0=Monday, 4=Friday)"""
            days_ahead = weekday - start_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return start_date + timedelta(days=days_ahead)

        # Helper function to find Nth weekday of month
        def nth_weekday_of_month(year, month, weekday, n):
            """Find the Nth occurrence of a weekday in a month"""
            first_day = datetime(year, month, 1)
            first_weekday = next_weekday(first_day, weekday)
            return first_weekday + timedelta(weeks=n-1)

        # 1. FOMC Meetings (8 times per year, roughly every 6-7 weeks)
        # Next FOMC meetings in 2024-2025: Dec 17-18, Jan 28-29, Mar 18-19, May 6-7
        fomc_dates = [
            datetime(2024, 12, 18, 14, 0),  # Dec 2024
            datetime(2025, 1, 29, 14, 0),   # Jan 2025
            datetime(2025, 3, 19, 14, 0),   # Mar 2025
            datetime(2025, 5, 7, 14, 0),    # May 2025
            datetime(2025, 6, 18, 14, 0),   # Jun 2025
            datetime(2025, 7, 30, 14, 0),   # Jul 2025
        ]

        for fomc_date in fomc_dates:
            if fomc_date > today and fomc_date < today + timedelta(days=90):
                events.append({
                    'title': 'FOMC Meeting',
                    'date': fomc_date.strftime('%b %d, %Y'),
                    'time': '2:00 PM ET',
                    'impact': 'High',
                    'description': 'Federal Reserve interest rate decision',
                    'impact_class': 'danger'
                })

        # 2. CPI Reports (usually around 10th-15th of each month)
        for i in range(4):
            month = (today.month + i) % 12 or 12
            year = today.year if today.month + i <= 12 else today.year + 1

            # CPI usually released around the 13th
            cpi_date = datetime(year, month, 13, 8, 30)

            # Adjust to next business day if weekend
            while cpi_date.weekday() >= 5:  # Saturday or Sunday
                cpi_date += timedelta(days=1)

            if cpi_date > today and cpi_date < today + timedelta(days=90):
                events.append({
                    'title': 'CPI Report',
                    'date': cpi_date.strftime('%b %d, %Y'),
                    'time': '8:30 AM ET',
                    'impact': 'High',
                    'description': 'Consumer Price Index (Inflation data)',
                    'impact_class': 'danger'
                })

        # 3. Jobs Report (First Friday of each month)
        for i in range(4):
            month = (today.month + i) % 12 or 12
            year = today.year if today.month + i <= 12 else today.year + 1

            # Find first Friday
            first_friday = nth_weekday_of_month(year, month, 4, 1)  # 4 = Friday
            first_friday = first_friday.replace(hour=8, minute=30)

            if first_friday > today and first_friday < today + timedelta(days=90):
                events.append({
                    'title': 'Jobs Report',
                    'date': first_friday.strftime('%b %d, %Y'),
                    'time': '8:30 AM ET',
                    'impact': 'High',
                    'description': 'Non-farm payrolls and unemployment rate',
                    'impact_class': 'danger'
                })

        # 4. GDP Reports (Quarterly, usually end of month)
        gdp_months = [1, 4, 7, 10]  # End of Jan, Apr, Jul, Oct
        for month in gdp_months:
            if month >= today.month or month + 12 >= today.month:
                year = today.year if month >= today.month else today.year + 1
                gdp_date = datetime(year, month, 28, 8, 30)

                if gdp_date > today and gdp_date < today + timedelta(days=120):
                    quarter = (month - 1) // 3
                    prev_quarter = f"Q{(quarter) or 4}"
                    events.append({
                        'title': 'GDP Growth',
                        'date': gdp_date.strftime('%b %d, %Y'),
                        'time': '8:30 AM ET',
                        'impact': 'Medium',
                        'description': f'{prev_quarter} GDP growth rate',
                        'impact_class': 'warning'
                    })

        # 5. Retail Sales (Mid-month, usually around 15th)
        for i in range(3):
            month = (today.month + i) % 12 or 12
            year = today.year if today.month + i <= 12 else today.year + 1

            retail_date = datetime(year, month, 15, 8, 30)

            # Adjust to business day
            while retail_date.weekday() >= 5:
                retail_date += timedelta(days=1)

            if retail_date > today and retail_date < today + timedelta(days=90):
                events.append({
                    'title': 'Retail Sales',
                    'date': retail_date.strftime('%b %d, %Y'),
                    'time': '8:30 AM ET',
                    'impact': 'Medium',
                    'description': 'Monthly retail sales data',
                    'impact_class': 'warning'
                })

        # 6. PCE Price Index (Last Friday of month)
        for i in range(3):
            month = (today.month + i) % 12 or 12
            year = today.year if today.month + i <= 12 else today.year + 1

            # Find last day of month
            last_day = cal.monthrange(year, month)[1]
            last_date = datetime(year, month, last_day)

            # Find last Friday
            while last_date.weekday() != 4:  # 4 = Friday
                last_date -= timedelta(days=1)

            last_date = last_date.replace(hour=8, minute=30)

            if last_date > today and last_date < today + timedelta(days=90):
                events.append({
                    'title': 'PCE Price Index',
                    'date': last_date.strftime('%b %d, %Y'),
                    'time': '8:30 AM ET',
                    'impact': 'Medium',
                    'description': "Fed's preferred inflation gauge",
                    'impact_class': 'warning'
                })

        # Sort events by date
        events.sort(key=lambda x: datetime.strptime(x['date'], '%b %d, %Y'))

        # Return only next 10 events
        return jsonify({
            'success': True,
            'events': events[:10]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/export_pdf')
def export_pdf():
    """Generate and export PDF report"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

        # Container for elements
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Title
        title = Paragraph("S&P 500 AI Prediction Report", title_style)
        elements.append(title)

        # Date
        date_text = Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal'])
        elements.append(date_text)
        elements.append(Spacer(1, 20))

        # Latest Prediction Section
        elements.append(Paragraph("Latest Prediction", heading_style))

        if os.path.exists(PREDICTIONS_FILE):
            pred_df = pd.read_csv(PREDICTIONS_FILE)
            if len(pred_df) > 0:
                latest = pred_df.iloc[-1]

                pred_data = [
                    ['Metric', 'Value'],
                    ['Prediction Date', latest['prediction_date']],
                    ['Data Date', latest['data_date']],
                    ['Direction', latest['direction']],
                    ['Confidence', f"{latest['confidence']*100:.2f}%"],
                    ['Probability UP', f"{latest['prob_up']*100:.2f}%"],
                    ['Probability DOWN', f"{latest['prob_down']*100:.2f}%"]
                ]

                pred_table = Table(pred_data, colWidths=[2.5*inch, 3*inch])
                pred_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                elements.append(pred_table)
                elements.append(Spacer(1, 20))

        # Accuracy Statistics
        if os.path.exists('predictions_with_accuracy.csv'):
            elements.append(Paragraph("Accuracy Statistics", heading_style))

            df = pd.read_csv('predictions_with_accuracy.csv')
            total = len(df)
            correct = df['is_correct'].sum()
            accuracy = (correct / total) * 100 if total > 0 else 0

            # High/Medium/Low confidence breakdown
            high_conf = df[df['confidence'] >= 0.70]
            medium_conf = df[(df['confidence'] >= 0.60) & (df['confidence'] < 0.70)]
            low_conf = df[df['confidence'] < 0.60]

            acc_data = [
                ['Category', 'Accuracy', 'Predictions'],
                ['Overall', f'{accuracy:.2f}%', f'{correct}/{total}'],
                ['High Confidence (>70%)',
                 f'{(high_conf["is_correct"].sum()/len(high_conf)*100):.2f}%' if len(high_conf) > 0 else 'N/A',
                 f'{len(high_conf)}'],
                ['Medium Confidence (60-70%)',
                 f'{(medium_conf["is_correct"].sum()/len(medium_conf)*100):.2f}%' if len(medium_conf) > 0 else 'N/A',
                 f'{len(medium_conf)}'],
                ['Low Confidence (<60%)',
                 f'{(low_conf["is_correct"].sum()/len(low_conf)*100):.2f}%' if len(low_conf) > 0 else 'N/A',
                 f'{len(low_conf)}']
            ]

            acc_table = Table(acc_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            acc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(acc_table)
            elements.append(Spacer(1, 20))

            # Recent Predictions
            elements.append(Paragraph("Recent Predictions (Last 10)", heading_style))

            recent_df = df.tail(10).sort_values('prediction_date', ascending=False)

            recent_data = [['Date', 'Predicted', 'Actual', 'Result', 'Return']]
            for _, row in recent_df.iterrows():
                result = '✓ Correct' if row['is_correct'] else '✗ Wrong'
                recent_data.append([
                    row['data_date'][:10],
                    row['predicted_direction'],
                    row['actual_direction'],
                    result,
                    f"{row['actual_return']:+.2f}%"
                ])

            recent_table = Table(recent_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1.2*inch, 1.1*inch])
            recent_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(recent_table)

        # Model Information
        elements.append(PageBreak())
        elements.append(Paragraph("Model Information", heading_style))

        model_info = [
            ['Parameter', 'Value'],
            ['Model Type', 'XGBoost Classifier'],
            ['Model Name', 'sp500_complete_20251113'],
            ['Features', '91 technical and sentiment indicators'],
            ['Training Period', '2020-2024'],
            ['Update Frequency', 'Daily']
        ]

        model_table = Table(model_info, colWidths=[2.5*inch, 3*inch])
        model_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(model_table)
        elements.append(Spacer(1, 20))

        # Disclaimer
        elements.append(Spacer(1, 30))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        disclaimer = Paragraph(
            "<b>DISCLAIMER:</b> This report is for informational purposes only. "
            "Past performance does not guarantee future results. "
            "Always conduct your own research before making investment decisions.",
            disclaimer_style
        )
        elements.append(disclaimer)

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'SP500_Prediction_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    print("\n" + "="*70)
    print("S&P 500 PREDICTION DASHBOARD")
    print("="*70)
    print("\nStarting server...")
    print("Dashboard will be available at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
