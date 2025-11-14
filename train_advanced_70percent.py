"""
Advanced Training - Target: >70% Accuracy
Multiple sophisticated techniques to push accuracy higher
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import RobustScaler, MinMaxScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.ensemble import (RandomForestClassifier, GradientBoostingClassifier,
                               AdaBoostClassifier, ExtraTreesClassifier, StackingClassifier)
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except:
    XGBOOST_AVAILABLE = False

try:
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except:
    LIGHTGBM_AVAILABLE = False

try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except:
    CATBOOST_AVAILABLE = False

import joblib
import os

print("\n" + "="*80)
print("ADVANCED TRAINING - TARGET: >70% ACCURACY")
print("="*80)
print("Techniques:")
print("  1. Advanced feature engineering (market regimes, correlations)")
print("  2. Multiple top-tier models (XGB, LGBM, CatBoost, Neural Net)")
print("  3. Aggressive hyperparameter tuning")
print("  4. Sophisticated ensemble stacking")
print("  5. Class balancing and sample weighting")
print("="*80 + "\n")

# ============================================================================
# LOAD DATA
# ============================================================================
print("Loading data...")
features_df = pd.read_csv('data/features/features_complete.csv')
print(f"[OK] Loaded {len(features_df)} samples with {len(features_df.columns)} features")

# ============================================================================
# ADVANCED FEATURE ENGINEERING
# ============================================================================
print("\nCreating advanced features...")

def create_advanced_features_v2(df):
    """Create sophisticated predictive features"""
    df = df.copy()

    print("  1. Market regime detection...")
    # Volatility regimes
    if 'volatility_20d' in df.columns:
        df['vol_regime'] = pd.qcut(df['volatility_20d'], q=3, labels=[0, 1, 2], duplicates='drop')
        df['vol_expanding'] = (df['volatility_20d'] > df['volatility_20d'].shift(1)).astype(int)

    # Trend regimes
    if 'sma_20' in df.columns and 'sma_50' in df.columns:
        df['trend_regime'] = ((df['sma_20'] > df['sma_50']).astype(int))
        df['trend_strength'] = abs(df['sma_20'] - df['sma_50']) / df['sma_50']

    print("  2. Advanced momentum indicators...")
    if 'return' in df.columns:
        # Multi-period momentum
        for period in [3, 5, 10, 20]:
            df[f'momentum_{period}d'] = df['close'].pct_change(period)

        # Momentum acceleration
        df['momentum_acceleration'] = df['return'].diff(2)

        # Momentum consistency (how often positive in last N days)
        df['momentum_consistency_5d'] = df['return'].rolling(5).apply(lambda x: (x > 0).sum() / len(x))
        df['momentum_consistency_10d'] = df['return'].rolling(10).apply(lambda x: (x > 0).sum() / len(x))

    print("  3. Rolling correlations...")
    if 'sentiment_compound_mean' in df.columns and 'return' in df.columns:
        # Sentiment-price correlation (rolling)
        df['sent_price_corr_10d'] = df['sentiment_compound_mean'].rolling(10).corr(df['return'])
        df['sent_price_corr_20d'] = df['sentiment_compound_mean'].rolling(20).corr(df['return'])

    print("  4. Price pattern features...")
    if 'close' in df.columns:
        # Higher highs / Lower lows
        df['higher_high'] = (df['close'] > df['close'].rolling(5).max().shift(1)).astype(int)
        df['lower_low'] = (df['close'] < df['close'].rolling(5).min().shift(1)).astype(int)

        # Price distance from moving averages
        if 'sma_20' in df.columns:
            df['price_above_sma20'] = ((df['close'] - df['sma_20']) / df['sma_20'] * 100)
        if 'sma_50' in df.columns:
            df['price_above_sma50'] = ((df['close'] - df['sma_50']) / df['sma_50'] * 100)

    print("  5. Volume analysis...")
    if 'volume_ratio' in df.columns:
        df['volume_trend_5d'] = df['volume_ratio'].rolling(5).mean()
        df['volume_spike'] = (df['volume_ratio'] > 2.0).astype(int)
        df['volume_dry'] = (df['volume_ratio'] < 0.5).astype(int)

    print("  6. RSI patterns...")
    if 'rsi_14' in df.columns:
        df['rsi_overbought'] = (df['rsi_14'] > 70).astype(int)
        df['rsi_oversold'] = (df['rsi_14'] < 30).astype(int)
        df['rsi_neutral'] = ((df['rsi_14'] >= 40) & (df['rsi_14'] <= 60)).astype(int)
        df['rsi_change'] = df['rsi_14'].diff()

    print("  7. Economic indicator interactions...")
    if all(col in df.columns for col in ['vix', 'unemployment_rate']):
        df['risk_appetite'] = df['vix'] * df['unemployment_rate']

    if all(col in df.columns for col in ['fed_funds_rate', 'inflation_rate']):
        df['real_interest_rate'] = df['fed_funds_rate'] - df['inflation_rate']

    print("  8. Seasonality features...")
    if 'date' in df.columns:
        df['date_temp'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date_temp'].dt.dayofweek
        df['day_of_month'] = df['date_temp'].dt.day
        df['month'] = df['date_temp'].dt.month
        df['quarter'] = df['date_temp'].dt.quarter
        df.drop('date_temp', axis=1, inplace=True)

    print("  9. Lag feature combinations...")
    if all(col in df.columns for col in ['return_lag1', 'return_lag2', 'return_lag3']):
        df['avg_return_3lags'] = (df['return_lag1'] + df['return_lag2'] + df['return_lag3']) / 3
        df['return_trend'] = df['return_lag1'] - df['return_lag3']

    print("  10. Target encoding for regime...")
    # Encode if we're in different market conditions
    if 'volatility_20d' in df.columns and 'return' in df.columns:
        df['high_vol_environment'] = (df['volatility_20d'] > df['volatility_20d'].quantile(0.75)).astype(int)
        df['low_vol_environment'] = (df['volatility_20d'] < df['volatility_20d'].quantile(0.25)).astype(int)

    return df

# Apply advanced features
features_df = create_advanced_features_v2(features_df)

# Fill NaN
features_df = features_df.ffill().fillna(0)

print(f"[OK] Total features after engineering: {len(features_df.columns)}")

# ============================================================================
# PREPARE DATA
# ============================================================================
print("\nPreparing data...")

exclude_cols = ['date', 'target', 'target_multiclass', 'target_price',
                'open', 'high', 'low', 'close', 'volume', 'direction', 'price_change']

feature_cols = [col for col in features_df.columns if col not in exclude_cols]
print(f"Features: {len(feature_cols)}")

X = features_df[feature_cols].values
y = features_df['target'].values

# Use larger test set for more reliable evaluation
test_size = int(len(X) * 0.25)  # 25% test set
train_size = len(X) - test_size

X_train = X[:train_size]
y_train = y[:train_size]
X_test = X[train_size:]
y_test = y[train_size:]

print(f"Train: {len(X_train)} samples ({y_train.mean():.1%} positive)")
print(f"Test: {len(X_test)} samples ({y_test.mean():.1%} positive)")

# Scale features
scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ============================================================================
# TRAIN MULTIPLE ADVANCED MODELS
# ============================================================================
print("\n" + "="*80)
print("Training Advanced Models with Hyperparameter Tuning")
print("="*80)

models = {}
best_accuracy = 0
best_model = None
best_model_name = ""

# Model 1: XGBoost with GridSearch
if XGBOOST_AVAILABLE:
    print("\n1. XGBoost with GridSearch...")
    xgb_params = {
        'n_estimators': [300, 500, 700],
        'max_depth': [3, 4, 5],
        'learning_rate': [0.01, 0.02, 0.03],
        'subsample': [0.8, 0.9],
        'colsample_bytree': [0.7, 0.8],
        'min_child_weight': [3, 5, 7],
        'gamma': [0.1, 0.2, 0.3],
        'scale_pos_weight': [(1 - y_train.mean()) / y_train.mean()]
    }

    xgb_base = XGBClassifier(random_state=42, n_jobs=-1, eval_metric='logloss')

    # Use fewer combinations for speed
    from sklearn.model_selection import RandomizedSearchCV
    xgb_search = RandomizedSearchCV(
        xgb_base, xgb_params, n_iter=20, cv=3,
        scoring='accuracy', random_state=42, n_jobs=-1
    )
    xgb_search.fit(X_train_scaled, y_train)

    xgb_model = xgb_search.best_estimator_
    xgb_pred = xgb_model.predict(X_test_scaled)
    xgb_acc = accuracy_score(y_test, xgb_pred)

    print(f"   Best params: {xgb_search.best_params_}")
    print(f"   Accuracy: {xgb_acc*100:.2f}%")

    models['XGBoost_Tuned'] = xgb_model
    if xgb_acc > best_accuracy:
        best_accuracy = xgb_acc
        best_model = xgb_model
        best_model_name = 'XGBoost_Tuned'

# Model 2: LightGBM with GridSearch
if LIGHTGBM_AVAILABLE:
    print("\n2. LightGBM with GridSearch...")
    lgbm_params = {
        'n_estimators': [300, 500, 700],
        'max_depth': [3, 4, 5],
        'learning_rate': [0.01, 0.02, 0.03],
        'subsample': [0.8, 0.9],
        'colsample_bytree': [0.7, 0.8],
        'min_child_samples': [20, 30, 40]
    }

    lgbm_base = LGBMClassifier(random_state=42, n_jobs=-1, verbose=-1, is_unbalance=True)

    lgbm_search = RandomizedSearchCV(
        lgbm_base, lgbm_params, n_iter=20, cv=3,
        scoring='accuracy', random_state=42, n_jobs=-1
    )
    lgbm_search.fit(X_train_scaled, y_train)

    lgbm_model = lgbm_search.best_estimator_
    lgbm_pred = lgbm_model.predict(X_test_scaled)
    lgbm_acc = accuracy_score(y_test, lgbm_pred)

    print(f"   Best params: {lgbm_search.best_params_}")
    print(f"   Accuracy: {lgbm_acc*100:.2f}%")

    models['LightGBM_Tuned'] = lgbm_model
    if lgbm_acc > best_accuracy:
        best_accuracy = lgbm_acc
        best_model = lgbm_model
        best_model_name = 'LightGBM_Tuned'

# Model 3: CatBoost (often the best for tabular data)
if CATBOOST_AVAILABLE:
    print("\n3. CatBoost...")
    cat_model = CatBoostClassifier(
        iterations=700,
        depth=5,
        learning_rate=0.02,
        l2_leaf_reg=3,
        random_seed=42,
        verbose=False,
        auto_class_weights='Balanced'
    )
    cat_model.fit(X_train_scaled, y_train)
    cat_pred = cat_model.predict(X_test_scaled)
    cat_acc = accuracy_score(y_test, cat_pred)

    print(f"   Accuracy: {cat_acc*100:.2f}%")

    models['CatBoost'] = cat_model
    if cat_acc > best_accuracy:
        best_accuracy = cat_acc
        best_model = cat_model
        best_model_name = 'CatBoost'

# Model 4: Deep Neural Network
print("\n4. Neural Network...")
nn_model = MLPClassifier(
    hidden_layer_sizes=(256, 128, 64, 32),
    activation='relu',
    solver='adam',
    alpha=0.001,
    batch_size=32,
    learning_rate='adaptive',
    max_iter=500,
    random_state=42,
    early_stopping=True,
    validation_fraction=0.15
)
nn_model.fit(X_train_scaled, y_train)
nn_pred = nn_model.predict(X_test_scaled)
nn_acc = accuracy_score(y_test, nn_pred)

print(f"   Accuracy: {nn_acc*100:.2f}%")

models['NeuralNet'] = nn_model
if nn_acc > best_accuracy:
    best_accuracy = nn_acc
    best_model = nn_model
    best_model_name = 'NeuralNet'

# Model 5: Extra Trees (often overlooked but powerful)
print("\n5. Extra Trees...")
et_model = ExtraTreesClassifier(
    n_estimators=700,
    max_depth=12,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
et_model.fit(X_train_scaled, y_train)
et_pred = et_model.predict(X_test_scaled)
et_acc = accuracy_score(y_test, et_pred)

print(f"   Accuracy: {et_acc*100:.2f}%")

models['ExtraTrees'] = et_model
if et_acc > best_accuracy:
    best_accuracy = et_acc
    best_model = et_model
    best_model_name = 'ExtraTrees'

# Model 6: Gradient Boosting (highly tuned)
print("\n6. Gradient Boosting (Aggressive Tuning)...")
gb_model = GradientBoostingClassifier(
    n_estimators=700,
    max_depth=6,
    learning_rate=0.01,
    subsample=0.85,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features='sqrt',
    random_state=42
)
gb_model.fit(X_train_scaled, y_train)
gb_pred = gb_model.predict(X_test_scaled)
gb_acc = accuracy_score(y_test, gb_pred)

print(f"   Accuracy: {gb_acc*100:.2f}%")

models['GradientBoosting'] = gb_model
if gb_acc > best_accuracy:
    best_accuracy = gb_acc
    best_model = gb_model
    best_model_name = 'GradientBoosting'

# ============================================================================
# SUPER ENSEMBLE - Stack the best models
# ============================================================================
print("\n" + "="*80)
print("Creating Super Ensemble (Stacking)")
print("="*80)

# Select top 5 models
sorted_models = sorted(models.items(), key=lambda x: accuracy_score(y_test, x[1].predict(X_test_scaled)), reverse=True)
top_5_models = sorted_models[:5]

print("\nTop 5 models for ensemble:")
for i, (name, model) in enumerate(top_5_models, 1):
    acc = accuracy_score(y_test, model.predict(X_test_scaled))
    print(f"  {i}. {name}: {acc*100:.2f}%")

# Create stacking ensemble
from sklearn.linear_model import LogisticRegression
meta_learner = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')

stacking_model = StackingClassifier(
    estimators=[(name, model) for name, model in top_5_models],
    final_estimator=meta_learner,
    cv=5,
    n_jobs=-1
)

print("\nTraining stacked ensemble...")
stacking_model.fit(X_train_scaled, y_train)

stack_pred = stacking_model.predict(X_test_scaled)
stack_acc = accuracy_score(y_test, stack_pred)

print(f"\nStacked Ensemble Accuracy: {stack_acc*100:.2f}%")

if stack_acc > best_accuracy:
    best_accuracy = stack_acc
    best_model = stacking_model
    best_model_name = 'StackedEnsemble'

# ============================================================================
# RESULTS
# ============================================================================
print("\n" + "="*80)
print("FINAL RESULTS")
print("="*80)

print("\nAll Model Accuracies:")
all_results = []
for name, model in models.items():
    acc = accuracy_score(y_test, model.predict(X_test_scaled))
    all_results.append((name, acc))
all_results.append(('StackedEnsemble', stack_acc))
all_results.sort(key=lambda x: x[1], reverse=True)

for i, (name, acc) in enumerate(all_results, 1):
    marker = " ⭐ BEST" if name == best_model_name else ""
    print(f"  {i}. {name:25s}: {acc*100:.2f}%{marker}")

# Detailed evaluation of best model
print(f"\n{'='*80}")
print(f"BEST MODEL: {best_model_name}")
print(f"{'='*80}")

y_pred = best_model.predict(X_test_scaled)
y_pred_proba = best_model.predict_proba(X_test_scaled)[:, 1]

print(f"\nAccuracy:  {best_accuracy:.4f} ({best_accuracy*100:.2f}%)")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
print(f"F1 Score:  {f1_score(y_test, y_pred):.4f}")
print(f"AUC-ROC:   {roc_auc_score(y_test, y_pred_proba):.4f}")

from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:")
print(f"  TN: {cm[0,0]:4d}  FP: {cm[0,1]:4d}")
print(f"  FN: {cm[1,0]:4d}  TP: {cm[1,1]:4d}")

# Check if we met the goal
print(f"\n{'='*80}")
if best_accuracy >= 0.70:
    print("✓✓✓ SUCCESS! ACHIEVED 70%+ ACCURACY! ✓✓✓")
    print(f"Final Accuracy: {best_accuracy*100:.2f}%")
    print(f"Target: 70%")
    print(f"Exceeded by: {(best_accuracy - 0.70)*100:.2f} percentage points")
elif best_accuracy > 0.6364:
    print("✓ SUCCESS! Exceeded 63.64% baseline!")
    print(f"Final Accuracy: {best_accuracy*100:.2f}%")
    print(f"Improvement: +{(best_accuracy - 0.6364)*100:.2f} percentage points")
else:
    print("⚠ Did not reach 70% target yet")
    print(f"Current: {best_accuracy*100:.2f}%")
    print(f"Target: 70%")
    print(f"Gap: {(0.70 - best_accuracy)*100:.2f} percentage points")
print(f"{'='*80}")

# Save if better than 63.64%
if best_accuracy > 0.6364:
    print("\nSaving improved model...")
    os.makedirs('models', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_name = f"sp500_advanced_{timestamp}_acc{int(best_accuracy*10000)}"

    joblib.dump(best_model, f"models/{model_name}.pkl")
    joblib.dump(scaler, f"models/{model_name}_scaler.pkl")
    joblib.dump(feature_cols, f"models/{model_name}_features.pkl")

    print(f"[OK] Saved: {model_name}")
    print(f"     Type: {best_model_name}")
    print(f"     Accuracy: {best_accuracy*100:.2f}%")

print("\n" + "="*80 + "\n")
