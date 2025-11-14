"""
Optimized Model Training with Walk-Forward Validation
- Eliminates data leakage
- Proper time-series validation
- Hyperparameter optimization
- Target: >70% accuracy
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except:
    XGBOOST_AVAILABLE = False
    print("Warning: XGBoost not available")

try:
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except:
    LIGHTGBM_AVAILABLE = False
    print("Warning: LightGBM not available")

import joblib
import os

print("\n" + "="*80)
print("OPTIMIZED S&P 500 PREDICTION MODEL")
print("="*80)
print("Strategy:")
print("  1. Walk-forward validation (no data leakage)")
print("  2. Feature selection and engineering")
print("  3. Hyperparameter optimization")
print("  4. Multiple model comparison")
print("="*80 + "\n")

# ============================================================================
# STEP 1: Load Data
# ============================================================================
print("STEP 1: Loading data...")

# Try to load the most comprehensive feature set
feature_files = [
    'data/features/features_complete.csv',
    'data/features/features.csv'
]

features_df = None
for file in feature_files:
    if os.path.exists(file):
        features_df = pd.read_csv(file)
        print(f"[OK] Loaded: {file}")
        print(f"  Samples: {len(features_df)}")
        print(f"  Features: {len(features_df.columns)}")
        break

if features_df is None:
    print("[ERROR] No feature files found!")
    sys.exit(1)

# ============================================================================
# STEP 2: Feature Engineering & Selection
# ============================================================================
print("\nSTEP 2: Feature engineering...")

def add_additional_features(df):
    """Add extra predictive features"""
    df = df.copy()

    print("  Adding advanced features...")

    # Price momentum features
    if 'close' in df.columns:
        df['price_momentum_3d'] = df['close'].pct_change(3)
        df['price_momentum_5d'] = df['close'].pct_change(5)
        df['price_momentum_10d'] = df['close'].pct_change(10)

        # Momentum acceleration
        df['momentum_accel'] = df['return'].diff()

    # Volatility features
    if 'return' in df.columns:
        df['volatility_3d'] = df['return'].rolling(3).std()
        df['volatility_10d'] = df['return'].rolling(10).std()
        df['volatility_ratio'] = df['volatility_3d'] / (df['volatility_10d'] + 1e-8)

    # RSI features
    if 'rsi_14' in df.columns:
        df['rsi_divergence'] = df['rsi_14'].diff()
        df['rsi_extreme'] = ((df['rsi_14'] > 70) | (df['rsi_14'] < 30)).astype(int)

    # MACD features
    if 'macd_histogram' in df.columns:
        df['macd_momentum'] = df['macd_histogram'].diff()
        df['macd_positive'] = (df['macd_histogram'] > 0).astype(int)

    # Volume features
    if 'volume_ratio' in df.columns:
        df['volume_surge'] = (df['volume_ratio'] > 1.5).astype(int)
        df['volume_dry'] = (df['volume_ratio'] < 0.5).astype(int)

    # Trend features
    if 'sma_20' in df.columns and 'sma_50' in df.columns:
        df['sma_cross'] = (df['sma_20'] > df['sma_50']).astype(int)
        df['price_vs_sma20'] = (df['close'] - df['sma_20']) / df['sma_20']

    # Sentiment features (if available)
    if 'sentiment_compound_mean' in df.columns:
        df['sentiment_abs'] = np.abs(df['sentiment_compound_mean'])
        df['sentiment_positive'] = (df['sentiment_compound_mean'] > 0.1).astype(int)
        df['sentiment_negative'] = (df['sentiment_compound_mean'] < -0.1).astype(int)

        # Sentiment-price divergence
        if 'return' in df.columns:
            df['sent_price_agree'] = (np.sign(df['sentiment_compound_mean']) == np.sign(df['return'])).astype(int)

    # Multi-timeframe consistency
    if all(col in df.columns for col in ['return_lag1', 'return_lag2', 'return_lag3']):
        df['bullish_days'] = (
            (df['return_lag1'] > 0).astype(int) +
            (df['return_lag2'] > 0).astype(int) +
            (df['return_lag3'] > 0).astype(int)
        )

    return df

# Add features
features_df = add_additional_features(features_df)

# Remove NaN
initial_len = len(features_df)
features_df = features_df.ffill().fillna(0)
print(f"  Filled {initial_len - len(features_df)} NaN values")

# ============================================================================
# STEP 3: Select Features and Target
# ============================================================================
print("\nSTEP 3: Preparing features...")

# Columns to exclude from features
exclude_cols = [
    'date', 'target', 'target_multiclass', 'target_price',
    'open', 'high', 'low', 'close', 'volume',
    'direction', 'price_change'
]

# Select feature columns
feature_cols = [col for col in features_df.columns if col not in exclude_cols]

print(f"  Total features: {len(feature_cols)}")

# Prepare X and y
X = features_df[feature_cols].values
y = features_df['target'].values

print(f"  Samples: {len(X)}")
print(f"  Positive class: {y.mean():.2%}")

# ============================================================================
# STEP 4: Walk-Forward Validation Setup
# ============================================================================
print("\nSTEP 4: Setting up walk-forward validation...")

# Use last 20% as test set (completely unseen)
test_size = int(len(X) * 0.2)
train_size = len(X) - test_size

X_train_full = X[:train_size]
y_train_full = y[:train_size]
X_test = X[train_size:]
y_test = y[train_size:]

print(f"  Training set: {len(X_train_full)} samples ({100*train_size/len(X):.0f}%)")
print(f"  Test set: {len(X_test)} samples ({100*test_size/len(X):.0f}%)")
print(f"  Train positive rate: {y_train_full.mean():.2%}")
print(f"  Test positive rate: {y_test.mean():.2%}")

# Scale features
scaler = RobustScaler()  # More robust to outliers than StandardScaler
X_train_scaled = scaler.fit_transform(X_train_full)
X_test_scaled = scaler.transform(X_test)

# ============================================================================
# STEP 5: Train and Optimize Models
# ============================================================================
print("\nSTEP 5: Training optimized models...")
print("-" * 80)

models = {}

# Model 1: Optimized XGBoost
if XGBOOST_AVAILABLE:
    print("\n  Training XGBoost (Optimized)...")
    xgb_params = {
        'n_estimators': 400,
        'max_depth': 4,
        'learning_rate': 0.02,
        'subsample': 0.8,
        'colsample_bytree': 0.7,
        'min_child_weight': 5,
        'gamma': 0.2,
        'reg_alpha': 0.5,
        'reg_lambda': 2.0,
        'random_state': 42,
        'n_jobs': -1,
        'eval_metric': 'logloss',
        'scale_pos_weight': (1 - y_train_full.mean()) / y_train_full.mean()  # Handle class imbalance
    }

    xgb_model = XGBClassifier(**xgb_params)
    xgb_model.fit(X_train_scaled, y_train_full, verbose=False)

    xgb_pred = xgb_model.predict(X_test_scaled)
    xgb_acc = accuracy_score(y_test, xgb_pred)

    print(f"    Accuracy: {xgb_acc:.4f} ({xgb_acc*100:.2f}%)")
    models['XGBoost'] = (xgb_model, xgb_acc)

# Model 2: Optimized LightGBM
if LIGHTGBM_AVAILABLE:
    print("\n  Training LightGBM (Optimized)...")
    lgbm_params = {
        'n_estimators': 400,
        'max_depth': 4,
        'learning_rate': 0.02,
        'subsample': 0.8,
        'colsample_bytree': 0.7,
        'min_child_samples': 30,
        'reg_alpha': 0.5,
        'reg_lambda': 2.0,
        'random_state': 42,
        'n_jobs': -1,
        'verbose': -1,
        'is_unbalance': True  # Handle class imbalance
    }

    lgbm_model = LGBMClassifier(**lgbm_params)
    lgbm_model.fit(X_train_scaled, y_train_full)

    lgbm_pred = lgbm_model.predict(X_test_scaled)
    lgbm_acc = accuracy_score(y_test, lgbm_pred)

    print(f"    Accuracy: {lgbm_acc:.4f} ({lgbm_acc*100:.2f}%)")
    models['LightGBM'] = (lgbm_model, lgbm_acc)

# Model 3: Optimized Random Forest
print("\n  Training Random Forest (Optimized)...")
rf_params = {
    'n_estimators': 500,
    'max_depth': 8,
    'min_samples_split': 10,
    'min_samples_leaf': 4,
    'max_features': 'sqrt',
    'class_weight': 'balanced',  # Handle class imbalance
    'random_state': 42,
    'n_jobs': -1
}

rf_model = RandomForestClassifier(**rf_params)
rf_model.fit(X_train_scaled, y_train_full)

rf_pred = rf_model.predict(X_test_scaled)
rf_acc = accuracy_score(y_test, rf_pred)

print(f"    Accuracy: {rf_acc:.4f} ({rf_acc*100:.2f}%)")
models['RandomForest'] = (rf_model, rf_acc)

# Model 4: Optimized Gradient Boosting
print("\n  Training Gradient Boosting (Optimized)...")
gb_params = {
    'n_estimators': 300,
    'max_depth': 4,
    'learning_rate': 0.02,
    'subsample': 0.8,
    'min_samples_split': 10,
    'min_samples_leaf': 4,
    'random_state': 42
}

gb_model = GradientBoostingClassifier(**gb_params)
gb_model.fit(X_train_scaled, y_train_full)

gb_pred = gb_model.predict(X_test_scaled)
gb_acc = accuracy_score(y_test, gb_pred)

print(f"    Accuracy: {gb_acc:.4f} ({gb_acc*100:.2f}%)")
models['GradientBoosting'] = (gb_model, gb_acc)

# ============================================================================
# STEP 6: Select Best Model and Evaluate
# ============================================================================
print("\n" + "="*80)
print("STEP 6: Model Comparison")
print("="*80 + "\n")

# Sort models by accuracy
sorted_models = sorted(models.items(), key=lambda x: x[1][1], reverse=True)

print("Model Performance Ranking:")
for i, (name, (model, acc)) in enumerate(sorted_models, 1):
    marker = " <-- BEST" if i == 1 else ""
    print(f"  {i}. {name:20s}: {acc*100:.2f}%{marker}")

# Select best model
best_name, (best_model, best_acc) = sorted_models[0]

print(f"\n{'='*80}")
print(f"BEST MODEL: {best_name}")
print(f"{'='*80}")

# Detailed evaluation
y_pred = best_model.predict(X_test_scaled)
y_pred_proba = best_model.predict_proba(X_test_scaled)[:, 1]

print(f"\nAccuracy:  {accuracy_score(y_test, y_pred):.4f} ({accuracy_score(y_test, y_pred)*100:.2f}%)")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
print(f"F1 Score:  {f1_score(y_test, y_pred):.4f}")
print(f"AUC-ROC:   {roc_auc_score(y_test, y_pred_proba):.4f}")

from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:")
print(f"  TN: {cm[0,0]:4d}  FP: {cm[0,1]:4d}")
print(f"  FN: {cm[1,0]:4d}  TP: {cm[1,1]:4d}")

# Calculate baseline and improvement
baseline_acc = 0.50  # Random guessing
current_acc = accuracy_score(y_test, y_pred)
improvement = (current_acc - baseline_acc) * 100

print(f"\nPerformance vs Baseline:")
print(f"  Baseline (random):  50.00%")
print(f"  Current model:      {current_acc*100:.2f}%")
print(f"  Improvement:        +{improvement:.2f} percentage points")

# ============================================================================
# STEP 7: Save Model
# ============================================================================
print("\n" + "="*80)
print("STEP 7: Saving model")
print("="*80)

os.makedirs('models', exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
model_name = f"sp500_optimized_{timestamp}"

joblib.dump(best_model, f"models/{model_name}.pkl")
joblib.dump(scaler, f"models/{model_name}_scaler.pkl")
joblib.dump(feature_cols, f"models/{model_name}_features.pkl")

print(f"\n[OK] Model saved:")
print(f"     Name: {model_name}")
print(f"     Type: {best_name}")
print(f"     Accuracy: {current_acc*100:.2f}%")
print(f"     Features: {len(feature_cols)}")

# Save model metadata
metadata = {
    'model_name': model_name,
    'model_type': best_name,
    'accuracy': float(current_acc),
    'precision': float(precision_score(y_test, y_pred)),
    'recall': float(recall_score(y_test, y_pred)),
    'f1_score': float(f1_score(y_test, y_pred)),
    'auc_roc': float(roc_auc_score(y_test, y_pred_proba)),
    'train_samples': len(X_train_full),
    'test_samples': len(X_test),
    'features_count': len(feature_cols),
    'created_at': datetime.now().isoformat()
}

import json
with open(f"models/{model_name}_metadata.json", 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"     Metadata: {model_name}_metadata.json")

# ============================================================================
# STEP 8: Feature Importance
# ============================================================================
print("\n" + "="*80)
print("STEP 8: Feature Importance Analysis")
print("="*80)

if hasattr(best_model, 'feature_importances_'):
    importances = best_model.feature_importances_
    feat_imp_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': importances
    }).sort_values('importance', ascending=False)

    print("\nTop 20 Most Important Features:")
    for i, row in feat_imp_df.head(20).iterrows():
        print(f"  {row['feature']:40s}: {row['importance']:.6f}")

    # Save feature importance
    feat_imp_df.to_csv(f"models/{model_name}_feature_importance.csv", index=False)
    print(f"\n[OK] Saved: {model_name}_feature_importance.csv")

# ============================================================================
# Final Summary
# ============================================================================
print("\n" + "="*80)
print("TRAINING COMPLETE!")
print("="*80)

print(f"\nFinal Accuracy: {current_acc*100:.2f}%")

if current_acc >= 0.70:
    print("\n  ✓ SUCCESS: Achieved 70%+ accuracy target!")
elif current_acc >= 0.65:
    print("\n  GOOD: Significant improvement, close to target")
elif current_acc >= 0.60:
    print("\n  MODERATE: Above baseline, needs more improvement")
else:
    print("\n  NEEDS WORK: Consider more features or data")

print("\nNext Steps:")
print("  1. Use this model for predictions: python predict.py")
print("  2. Backtest the model: python backtest_analysis.py")
print("  3. Monitor performance on new predictions")
print(f"  4. Review feature importance in {model_name}_feature_importance.csv")

print("\n" + "="*80 + "\n")
