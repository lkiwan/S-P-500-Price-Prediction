"""
Prediction Module
Make predictions using trained models
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import yaml
import os
import joblib
from datetime import datetime, timedelta


class Predictor:
    """Make predictions for S&P 500 price movements"""

    def __init__(self, config_path: str = "config.yaml", model_name: str = None):
        """
        Initialize predictor

        Args:
            config_path: Path to configuration file
            model_name: Name of trained model to load
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.prediction_config = self.config['prediction']
        self.models_path = self.config['paths']['models']

        self.model = None
        self.scaler = None
        self.feature_names = None

        if model_name:
            self.load_model(model_name)

    def load_model(self, model_name: str) -> bool:
        """
        Load trained model

        Args:
            model_name: Name of the model (without .pkl extension)

        Returns:
            True if successful
        """
        model_path = os.path.join(self.models_path, f"{model_name}.pkl")
        scaler_path = os.path.join(self.models_path, f"{model_name}_scaler.pkl")
        features_path = os.path.join(self.models_path, f"{model_name}_features.pkl")

        if not all(os.path.exists(p) for p in [model_path, scaler_path, features_path]):
            print(f"Model files not found for: {model_name}")
            return False

        try:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.feature_names = joblib.load(features_path)

            print(f"Model loaded: {model_name}")
            print(f"Features required: {len(self.feature_names)}")
            return True

        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def predict(self, features: pd.DataFrame) -> Dict:
        """
        Make prediction for given features

        Args:
            features: DataFrame with feature values

        Returns:
            Dictionary with prediction results
        """
        if not self.model or not self.feature_names:
            print("Error: Model not loaded")
            return {}

        try:
            # Ensure all required features are present
            missing_features = set(self.feature_names) - set(features.columns)
            if missing_features:
                print(f"Warning: Missing features: {missing_features}")
                for feat in missing_features:
                    features[feat] = 0  # Fill with default value

            # Select and order features
            X = features[self.feature_names].values

            # Scale features
            X_scaled = self.scaler.transform(X)

            # Make prediction
            prediction = self.model.predict(X_scaled)[0]
            probability = self.model.predict_proba(X_scaled)[0]

            # Interpret results
            direction = "UP" if prediction == 1 else "DOWN"
            confidence = probability[int(prediction)]

            result = {
                'prediction': int(prediction),
                'direction': direction,
                'probability_down': float(probability[0]),
                'probability_up': float(probability[1]),
                'confidence': float(confidence),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            return result

        except Exception as e:
            print(f"Error making prediction: {e}")
            return {}

    def predict_next_day(self, latest_features: pd.DataFrame) -> Dict:
        """
        Predict next day's market direction

        Args:
            latest_features: DataFrame with most recent features

        Returns:
            Prediction results
        """
        result = self.predict(latest_features)

        if result:
            threshold = self.prediction_config['threshold']
            conf_level = self.prediction_config['confidence_level']

            print("\n=== S&P 500 Prediction for Next Trading Day ===")
            print(f"Prediction: {result['direction']}")
            print(f"Confidence: {result['confidence']:.2%}")
            print(f"Probability Up: {result['probability_up']:.2%}")
            print(f"Probability Down: {result['probability_down']:.2%}")

            if result['confidence'] >= conf_level:
                print(f"\n[HIGH CONFIDENCE] Prediction confidence > {conf_level:.0%}")
            else:
                print(f"\n[LOW CONFIDENCE] Prediction confidence < {conf_level:.0%}")
                print("  Consider waiting for more data or signals")

            print(f"\nTimestamp: {result['timestamp']}")

        return result

    def predict_batch(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Make predictions for multiple time periods

        Args:
            features_df: DataFrame with features for multiple dates

        Returns:
            DataFrame with predictions
        """
        if features_df.empty:
            return pd.DataFrame()

        predictions = []
        probabilities = []

        for idx, row in features_df.iterrows():
            result = self.predict(pd.DataFrame([row]))
            if result:
                predictions.append(result['prediction'])
                probabilities.append(result['probability_up'])
            else:
                predictions.append(None)
                probabilities.append(None)

        features_df['predicted_direction'] = predictions
        features_df['predicted_probability'] = probabilities

        return features_df

    def backtest(self, features_df: pd.DataFrame, actual_col: str = 'target') -> Dict:
        """
        Backtest predictions against actual outcomes

        Args:
            features_df: DataFrame with features and actual outcomes
            actual_col: Column name with actual outcomes

        Returns:
            Dictionary with backtest results
        """
        if actual_col not in features_df.columns:
            print(f"Error: Actual outcomes column '{actual_col}' not found")
            return {}

        # Make predictions
        predictions_df = self.predict_batch(features_df)

        # Calculate metrics
        y_true = predictions_df[actual_col].values
        y_pred = predictions_df['predicted_direction'].values

        # Remove any NaN values
        valid_idx = ~(pd.isna(y_true) | pd.isna(y_pred))
        y_true = y_true[valid_idx]
        y_pred = y_pred[valid_idx]

        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

        results = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0),
            'total_predictions': len(y_pred),
            'correct_predictions': int((y_true == y_pred).sum())
        }

        print("\n=== Backtest Results ===")
        print(f"Total Predictions: {results['total_predictions']}")
        print(f"Correct Predictions: {results['correct_predictions']}")
        print(f"Accuracy: {results['accuracy']:.2%}")
        print(f"Precision: {results['precision']:.2%}")
        print(f"Recall: {results['recall']:.2%}")
        print(f"F1 Score: {results['f1_score']:.2%}")

        return results

    def simulate_trading_strategy(self, features_df: pd.DataFrame,
                                  actual_returns_col: str = 'return',
                                  initial_capital: float = 10000) -> Dict:
        """
        Simulate a simple trading strategy based on predictions

        Args:
            features_df: DataFrame with features
            actual_returns_col: Column with actual returns
            initial_capital: Starting capital

        Returns:
            Dictionary with strategy performance
        """
        # Make predictions
        predictions_df = self.predict_batch(features_df)

        if 'predicted_direction' not in predictions_df.columns:
            print("Error: Predictions failed")
            return {}

        # Simple strategy: Buy if predict UP, sell/stay out if predict DOWN
        capital = initial_capital
        position = 0  # 0 = no position, 1 = long position
        trades = []

        for idx, row in predictions_df.iterrows():
            if pd.isna(row['predicted_direction']) or pd.isna(row[actual_returns_col]):
                continue

            predicted_direction = row['predicted_direction']
            actual_return = row[actual_returns_col]

            # Trading logic
            if predicted_direction == 1 and position == 0:
                # Buy signal
                position = 1
                entry_capital = capital
            elif predicted_direction == 0 and position == 1:
                # Sell signal
                position = 0
                capital = entry_capital * (1 + actual_return)
                trades.append({
                    'date': row.get('date', idx),
                    'return': actual_return,
                    'capital': capital
                })
            elif position == 1:
                # Holding position, update based on actual return
                capital = entry_capital * (1 + actual_return)

        # Calculate metrics
        total_return = (capital - initial_capital) / initial_capital
        num_trades = len(trades)

        results = {
            'initial_capital': initial_capital,
            'final_capital': capital,
            'total_return': total_return,
            'num_trades': num_trades,
            'trades': trades
        }

        print("\n=== Trading Strategy Simulation ===")
        print(f"Initial Capital: ${initial_capital:,.2f}")
        print(f"Final Capital: ${capital:,.2f}")
        print(f"Total Return: {total_return:.2%}")
        print(f"Number of Trades: {num_trades}")

        return results


if __name__ == "__main__":
    print("Prediction Module")
    print("Load a trained model and make predictions on new data")
