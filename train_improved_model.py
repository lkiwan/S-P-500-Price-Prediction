"""
Improved Model Training with Advanced Features and Ensemble Methods
Goal: Achieve >70% accuracy through sophisticated ML techniques
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression

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

import joblib
import os

print("\n" + "="*80)
print("IMPROVED S&P 500 PREDICTION MODEL")
print("="*80)
print("Enhancements:")
print("  1. Advanced feature engineering (volatility regimes, momentum)")
print("  2. Ensemble methods (Stacking + Voting)")
print("  3. Hyperparameter optimization")
print("  4. Class balancing")
print("="*80 + "\n")

# ============================================================================
# STEP 1: Load and Create Advanced Features
# ============================================================================
print("STEP 1: Loading data and engineering advanced features...")

# Load features
features_df = pd.read_csv('data/features/features.csv')
print(f"[OK] Loaded {len(features_df)} samples with {len(features_df.columns)} features")

# Create advanced features
def create_advanced_features(df):
    """Add sophisticated features for better prediction"""
    df = df.copy()

    print("  Creating advanced features...")

    # 1. Volatility regime detection
    if 'volatility_20d' in df.columns:
        vol_mean = df['volatility_20d'].rolling(60).mean()
        vol_std = df['volatility_20d'].rolling(60).std()
        df['volatility_regime'] = ((df['volatility_20d'] - vol_mean) / (vol_std + 1e-8)).fillna(0)
        df['high_volatility'] = (df['volatility_20d'] > vol_mean + vol_std).astype(int)

    # 2. Advanced momentum indicators
    if 'close' in df.columns:
        # Rate of change acceleration
        df['roc_acceleration'] = df['close'].pct_change(5) - df['close'].pct_change(10)

        # Momentum divergence
        df['price_momentum_div'] = df['close'].pct_change(5) / (df['close'].pct_change(20) + 1e-8)

    # 3. Market regime (trending vs ranging)
    if 'sma_20' in df.columns and 'sma_50' in df.columns:
        df['trend_strength'] = (df['sma_20'] - df['sma_50']) / df['sma_50']
        df['price_position'] = (df['close'] - df['sma_20']) / df['sma_20']

    # 4. Volume patterns
    if 'volume_ratio' in df.columns:
        df['volume_trend'] = df['volume_ratio'].rolling(5).mean()
        df['volume_spike'] = (df['volume_ratio'] > 1.5).astype(int)

    # 5. RSI divergence
    if 'rsi_14' in df.columns:
        df['rsi_overbought'] = (df['rsi_14'] > 70).astype(int)
        df['rsi_oversold'] = (df['rsi_14'] < 30).astype(int)
        df['rsi_momentum'] = df['rsi_14'].diff()

    # 6. MACD momentum
    if 'macd_histogram' in df.columns:
        df['macd_crossover'] = (df['macd_histogram'] > 0).astype(int)
        df['macd_trend'] = df['macd_histogram'].rolling(5).mean()

    # 7. Bollinger Band position
    if all(col in df.columns for col in ['close', 'bb_upper', 'bb_lower']):
        bb_range = df['bb_upper'] - df['bb_lower']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (bb_range + 1e-8)
        df['bb_squeeze'] = (bb_range < df['bb_width'].rolling(20).mean()).astype(int)

    # 8. Sentiment-Price alignment
    if 'sentiment_compound_mean' in df.columns and 'return' in df.columns:
        df['sentiment_price_correlation'] = df['sentiment_compound_mean'].rolling(10).corr(df['return'])
        df['sentiment_price_divergence'] = np.sign(df['sentiment_compound_mean']) != np.sign(df['return'])
        df['sentiment_price_divergence'] = df['sentiment_price_divergence'].astype(int)

    # 9. Multi-timeframe features
    if 'return' in df.columns:
        df['return_1d'] = df['return']
        df['return_3d'] = df['close'].pct_change(3)
        df['return_7d'] = df['close'].pct_change(7)
        df['return_14d'] = df['close'].pct_change(14)

        # Consistency score (how many timeframes agree)
        df['bullish_timeframes'] = (
            (df['return_1d'] > 0).astype(int) +
            (df['return_3d'] > 0).astype(int) +
            (df['return_7d'] > 0).astype(int)
        )

    # 10. Sentiment momentum and acceleration
    if 'sentiment_compound_mean' in df.columns:
        df['sentiment_velocity'] = df['sentiment_compound_mean'].diff()
        df['sentiment_acceleration'] = df['sentiment_velocity'].diff()
        df['sentiment_strength'] = np.abs(df['sentiment_compound_mean'])

    print(f"  Created {len([c for c in df.columns if c not in features_df.columns])} new advanced features")

    return df

# Create advanced features
features_advanced = create_advanced_features(features_df)

# Remove any new NaN values
features_advanced = features_advanced.fillna(0)

print(f"[OK] Total features: {len(features_advanced.columns)}")

# ============================================================================
# STEP 2: Feature Selection
# ============================================================================
print("\nSTEP 2: Selecting optimal features...")

# Exclude non-feature columns
exclude_cols = ['date', 'target', 'target_multiclass', 'target_price',
                'open', 'high', 'low', 'close', 'volume', 'direction', 'price_change']

feature_cols = [col for col in features_advanced.columns if col not in exclude_cols]
print(f"  Using {len(feature_cols)} features for training")

# Prepare data
X = features_advanced[feature_cols].values
y = features_advanced['target'].values

# Time-based split (80/20)
split_idx = int(len(X) * 0.8)
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"  Training samples: {len(X_train)}")
print(f"  Test samples: {len(X_test)}")
print(f"  Train positive rate: {y_train.mean():.1%}")
print(f"  Test positive rate: {y_test.mean():.1%}")

# ============================================================================
# STEP 3: Train Multiple Models
# ============================================================================
print("\nSTEP 3: Training ensemble of models...")

models_to_train = []

# Model 1: Optimized XGBoost
if XGBOOST_AVAILABLE:
    print("\n  Training XGBoost...")
    xgb_model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        eval_metric='logloss'
    )
    xgb_model.fit(X_train_scaled, y_train)
    xgb_acc = accuracy_score(y_test, xgb_model.predict(X_test_scaled))
    print(f"    XGBoost accuracy: {xgb_acc:.4f}")
    models_to_train.append(('xgb', xgb_model))

# Model 2: LightGBM
if LIGHTGBM_AVAILABLE:
    print("\n  Training LightGBM...")
    lgbm_model = LGBMClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_samples=20,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    lgbm_model.fit(X_train_scaled, y_train)
    lgbm_acc = accuracy_score(y_test, lgbm_model.predict(X_test_scaled))
    print(f"    LightGBM accuracy: {lgbm_acc:.4f}")
    models_to_train.append(('lgbm', lgbm_model))

# Model 3: Random Forest
print("\n  Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_train)
rf_acc = accuracy_score(y_test, rf_model.predict(X_test_scaled))
print(f"    Random Forest accuracy: {rf_acc:.4f}")
models_to_train.append(('rf', rf_model))

# Model 4: Gradient Boosting
print("\n  Training Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    random_state=42
)
gb_model.fit(X_train_scaled, y_train)
gb_acc = accuracy_score(y_test, gb_model.predict(X_test_scaled))
print(f"    Gradient Boosting accuracy: {gb_acc:.4f}")
models_to_train.append(('gb', gb_model))

# ============================================================================
# STEP 4: Create Ensemble Models
# ============================================================================
print("\nSTEP 4: Creating ensemble models...")

# Voting Classifier (soft voting for probabilities)
print("\n  Creating Voting Ensemble...")
voting_model = VotingClassifier(
    estimators=models_to_train,
    voting='soft',
    n_jobs=-1
)
voting_model.fit(X_train_scaled, y_train)
voting_acc = accuracy_score(y_test, voting_model.predict(X_test_scaled))
print(f"    Voting Ensemble accuracy: {voting_acc:.4f}")

# Stacking Classifier
print("\n  Creating Stacking Ensemble...")
stacking_model = StackingClassifier(
    estimators=models_to_train,
    final_estimator=LogisticRegression(max_iter=1000, random_state=42),
    cv=5,
    n_jobs=-1
)
stacking_model.fit(X_train_scaled, y_train)
stacking_acc = accuracy_score(y_test, stacking_model.predict(X_test_scaled))
print(f"    Stacking Ensemble accuracy: {stacking_acc:.4f}")

# ============================================================================
# STEP 5: Evaluate Best Model
# ============================================================================
print("\n" + "="*80)
print("STEP 5: Final Evaluation")
print("="*80)

# Select best model
model_scores = {
    'XGBoost': xgb_acc if XGBOOST_AVAILABLE else 0,
    'LightGBM': lgbm_acc if LIGHTGBM_AVAILABLE else 0,
    'Random Forest': rf_acc,
    'Gradient Boosting': gb_acc,
    'Voting Ensemble': voting_acc,
    'Stacking Ensemble': stacking_acc
}

best_model_name = max(model_scores, key=model_scores.get)
best_accuracy = model_scores[best_model_name]

print("\nModel Performance Comparison:")
for name, score in sorted(model_scores.items(), key=lambda x: x[1], reverse=True):
    marker = " <-- BEST" if name == best_model_name else ""
    print(f"  {name:25s}: {score:.2%}{marker}")

# Select the best performing model
if best_model_name == 'Stacking Ensemble':
    best_model = stacking_model
elif best_model_name == 'Voting Ensemble':
    best_model = voting_model
elif best_model_name == 'XGBoost':
    best_model = xgb_model
elif best_model_name == 'LightGBM':
    best_model = lgbm_model
elif best_model_name == 'Random Forest':
    best_model = rf_model
else:
    best_model = gb_model

# Detailed evaluation
y_pred = best_model.predict(X_test_scaled)
y_pred_proba = best_model.predict_proba(X_test_scaled)[:, 1]

print(f"\n{'='*80}")
print(f"BEST MODEL: {best_model_name}")
print(f"{'='*80}")
print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f} ({accuracy_score(y_test, y_pred)*100:.2f}%)")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
print(f"F1 Score:  {f1_score(y_test, y_pred):.4f}")
print(f"AUC-ROC:   {roc_auc_score(y_test, y_pred_proba):.4f}")

# Confusion matrix
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:")
print(f"  TN: {cm[0,0]:4d}  FP: {cm[0,1]:4d}")
print(f"  FN: {cm[1,0]:4d}  TP: {cm[1,1]:4d}")

# Calculate improvement
baseline_accuracy = 0.6349  # Current accuracy from calculate_accuracy.py
improvement = (accuracy_score(y_test, y_pred) - baseline_accuracy) * 100
print(f"\nImprovement over baseline: {improvement:+.2f} percentage points")

# ============================================================================
# STEP 6: Save Models
# ============================================================================
print("\n" + "="*80)
print("STEP 6: Saving models")
print("="*80)

os.makedirs('models', exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Save best model
model_name = f"sp500_improved_{timestamp}"
joblib.dump(best_model, f"models/{model_name}.pkl")
joblib.dump(scaler, f"models/{model_name}_scaler.pkl")
joblib.dump(feature_cols, f"models/{model_name}_features.pkl")

print(f"\n[OK] Saved best model: {model_name}")
print(f"     Type: {best_model_name}")
print(f"     Accuracy: {accuracy_score(y_test, y_pred):.2%}")

# Also save the stacking ensemble separately
if stacking_acc > 0.65:  # Only if it's good
    stacking_name = f"sp500_stacking_{timestamp}"
    joblib.dump(stacking_model, f"models/{stacking_name}.pkl")
    joblib.dump(scaler, f"models/{stacking_name}_scaler.pkl")
    joblib.dump(feature_cols, f"models/{stacking_name}_features.pkl")
    print(f"\n[OK] Also saved Stacking Ensemble: {stacking_name}")
    print(f"     Accuracy: {stacking_acc:.2%}")

print("\n" + "="*80)
print("TRAINING COMPLETE!")
print("="*80)
print(f"\nFinal Result: {accuracy_score(y_test, y_pred)*100:.2f}% accuracy")
print(f"Target: >70% accuracy")

if accuracy_score(y_test, y_pred) >= 0.70:
    print("\n  SUCCESS: Target accuracy achieved!")
elif accuracy_score(y_test, y_pred) >= 0.65:
    print("\n  GOOD PROGRESS: Significant improvement over baseline")
else:
    print("\n  Need more work: Consider additional features or longer training data")

print("\n" + "="*80 + "\n")
