"""
Model Training Module
Train machine learning models for S&P 500 price prediction
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import yaml
import os
import joblib
from datetime import datetime

from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)

import warnings
warnings.filterwarnings('ignore')

# Import ML models
try:
    from xgboost import XGBClassifier, XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("Warning: XGBoost not installed")

try:
    from lightgbm import LGBMClassifier, LGBMRegressor
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("Warning: LightGBM not installed")

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression


class ModelTrainer:
    """Train and evaluate ML models for price prediction"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize model trainer"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.model_config = self.config['model']
        self.training_config = self.config['training']
        self.models_path = self.config['paths']['models']

        os.makedirs(self.models_path, exist_ok=True)

        self.scaler = StandardScaler()
        self.model = None
        self.feature_names = None

    def prepare_data(self, df: pd.DataFrame,
                    feature_cols: List[str],
                    target_col: str = 'target',
                    test_size: float = None) -> Tuple:
        """
        Prepare data for training

        Args:
            df: Feature dataframe
            feature_cols: List of feature column names
            target_col: Target column name
            test_size: Test set size (default from config)

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        if test_size is None:
            test_size = 1 - self.config['data']['train_test_split']

        # Separate features and target
        X = df[feature_cols].values
        y = df[target_col].values

        # Store feature names
        self.feature_names = feature_cols

        # Split data (maintaining temporal order)
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Scale features
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)

        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        print(f"Features: {len(feature_cols)}")

        return X_train, X_test, y_train, y_test

    def create_model(self, model_type: str = None, task: str = None):
        """
        Create ML model based on configuration

        Args:
            model_type: Type of model (xgboost, lightgbm, random_forest)
            task: 'classification' or 'regression'

        Returns:
            Initialized model
        """
        model_type = model_type or self.model_config['type']
        task = task or self.model_config['task']

        if model_type == 'xgboost':
            if not XGBOOST_AVAILABLE:
                print("XGBoost not available, falling back to Random Forest")
                model_type = 'random_forest'
            else:
                params = self.model_config['xgboost'].copy()
                # Remove None/null values
                params = {k: v for k, v in params.items() if v is not None}
                if task == 'classification':
                    return XGBClassifier(**params, random_state=self.training_config['random_state'])
                else:
                    return XGBRegressor(**params, random_state=self.training_config['random_state'])

        if model_type == 'lightgbm':
            if not LIGHTGBM_AVAILABLE:
                print("LightGBM not available, falling back to Random Forest")
                model_type = 'random_forest'
            else:
                if task == 'classification':
                    return LGBMClassifier(random_state=self.training_config['random_state'])
                else:
                    return LGBMRegressor(random_state=self.training_config['random_state'])

        if model_type == 'random_forest':
            params = self.model_config['random_forest']
            if task == 'classification':
                return RandomForestClassifier(**params, random_state=self.training_config['random_state'])
            else:
                return RandomForestRegressor(**params, random_state=self.training_config['random_state'])

        raise ValueError(f"Unknown model type: {model_type}")

    def train(self, X_train: np.ndarray, y_train: np.ndarray,
             X_val: Optional[np.ndarray] = None,
             y_val: Optional[np.ndarray] = None):
        """
        Train the model

        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)
        """
        print(f"\nTraining {self.model_config['type']} model...")

        self.model = self.create_model()

        # Train with early stopping if validation data provided
        if X_val is not None and y_val is not None and hasattr(self.model, 'fit'):
            if 'XGB' in str(type(self.model)):
                self.model.fit(
                    X_train, y_train,
                    eval_set=[(X_val, y_val)],
                    verbose=False
                )
            else:
                self.model.fit(X_train, y_train)
        else:
            self.model.fit(X_train, y_train)

        print("Training complete")

    def evaluate_classification(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """
        Evaluate classification model

        Args:
            X_test: Test features
            y_test: True labels

        Returns:
            Dictionary of evaluation metrics
        """
        # Predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]

        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0),
            'auc_roc': roc_auc_score(y_test, y_pred_proba)
        }

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)

        print("\n=== Model Evaluation ===")
        print(f"Accuracy:  {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall:    {metrics['recall']:.4f}")
        print(f"F1 Score:  {metrics['f1_score']:.4f}")
        print(f"AUC-ROC:   {metrics['auc_roc']:.4f}")

        print("\nConfusion Matrix:")
        print(f"  TN: {cm[0,0]}  FP: {cm[0,1]}")
        print(f"  FN: {cm[1,0]}  TP: {cm[1,1]}")

        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Down', 'Up']))

        return metrics

    def cross_validate(self, X: np.ndarray, y: np.ndarray, cv_folds: int = None) -> Dict:
        """
        Perform time series cross-validation

        Args:
            X: Features
            y: Labels
            cv_folds: Number of CV folds

        Returns:
            Dictionary with CV scores
        """
        cv_folds = cv_folds or self.training_config['cross_validation_folds']

        print(f"\nPerforming {cv_folds}-fold time series cross-validation...")

        tscv = TimeSeriesSplit(n_splits=cv_folds)
        cv_scores = cross_val_score(
            self.model, X, y, cv=tscv, scoring='accuracy', n_jobs=-1
        )

        print(f"CV Scores: {cv_scores}")
        print(f"Mean CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

        return {
            'cv_scores': cv_scores,
            'mean_score': cv_scores.mean(),
            'std_score': cv_scores.std()
        }

    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get feature importance from trained model

        Args:
            top_n: Number of top features to return

        Returns:
            DataFrame with feature importances
        """
        if not self.model or not self.feature_names:
            print("Model not trained yet")
            return pd.DataFrame()

        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
        else:
            print("Model doesn't support feature importance")
            return pd.DataFrame()

        # Create dataframe
        feat_imp = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)

        print(f"\nTop {top_n} Most Important Features:")
        print(feat_imp.head(top_n).to_string(index=False))

        return feat_imp

    def save_model(self, model_name: str = None):
        """Save trained model and scaler"""
        if not self.model:
            print("No model to save")
            return

        if model_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = f"model_{self.model_config['type']}_{timestamp}"

        # Save model
        model_path = os.path.join(self.models_path, f"{model_name}.pkl")
        joblib.dump(self.model, model_path)

        # Save scaler
        scaler_path = os.path.join(self.models_path, f"{model_name}_scaler.pkl")
        joblib.dump(self.scaler, scaler_path)

        # Save feature names
        features_path = os.path.join(self.models_path, f"{model_name}_features.pkl")
        joblib.dump(self.feature_names, features_path)

        print(f"\nModel saved to: {model_path}")
        print(f"Scaler saved to: {scaler_path}")
        print(f"Features saved to: {features_path}")

    def load_model(self, model_name: str):
        """Load trained model and scaler"""
        model_path = os.path.join(self.models_path, f"{model_name}.pkl")
        scaler_path = os.path.join(self.models_path, f"{model_name}_scaler.pkl")
        features_path = os.path.join(self.models_path, f"{model_name}_features.pkl")

        if not os.path.exists(model_path):
            print(f"Model not found: {model_path}")
            return False

        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.feature_names = joblib.load(features_path)

        print(f"Model loaded from: {model_path}")
        return True


if __name__ == "__main__":
    print("Model Training Module")
    print("Use this module to train ML models for S&P 500 prediction")
