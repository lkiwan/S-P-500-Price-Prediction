"""
Final Ensemble Model - Combining Best Performers
Target: Push past 65% accuracy
"""

import sys
sys.path.append('src')

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.ensemble import VotingClassifier, RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_selection import SelectFromModel

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
print("FINAL ENSEMBLE MODEL FOR S&P 500 PREDICTION")
print("="*80)
print("Strategy:")
print("  1. Feature selection (keep only best features)")
print("  2. Train multiple optimized models")
print("  3. Ensemble with weighted voting")
print("  4. Confidence-based predictions")
print("="*80 + "\n")

# Load data
print("Loading data...")
features_df = None
for file in ['data/features/features_complete.csv', 'data/features/features.csv']:
    if os.path.exists(file):
        features_df = pd.read_csv(file)
        print(f"[OK] Loaded: {file} ({len(features_df)} samples)")
        break

if features_df is None:
    print("[ERROR] No feature files found!")
    sys.exit(1)

# Prepare features
exclude_cols = ['date', 'target', 'target_multiclass', 'target_price',
                'open', 'high', 'low', 'close', 'volume', 'direction', 'price_change']
feature_cols = [col for col in features_df.columns if col not in exclude_cols]

# Fill NaN
features_df = features_df.ffill().fillna(0)

X = features_df[feature_cols].values
y = features_df['target'].values

# Split data (80/20)
test_size = int(len(X) * 0.2)
train_size = len(X) - test_size

X_train = X[:train_size]
y_train = y[:train_size]
X_test = X[train_size:]
y_test = y[train_size:]

print(f"Training: {len(X_train)} samples")
print(f"Test: {len(X_test)} samples")

# ============================================================================
# Feature Selection - Keep Only Best Features
# ============================================================================
print("\nFeature Selection...")

# Train a simple model for feature selection
selector_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
selector_model.fit(X_train, y_train)

# Select features with importance > threshold
selector = SelectFromModel(selector_model, threshold='median', prefit=True)
X_train_selected = selector.transform(X_train)
X_test_selected = selector.transform(X_test)

selected_features = [feature_cols[i] for i in range(len(feature_cols)) if selector.get_support()[i]]

print(f"  Original features: {len(feature_cols)}")
print(f"  Selected features: {len(selected_features)}")
print(f"  Reduction: {100*(1-len(selected_features)/len(feature_cols)):.1f}%")

# Scale selected features
scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(X_train_selected)
X_test_scaled = scaler.transform(X_test_selected)

# ============================================================================
# Train Individual Models with Best Hyperparameters
# ============================================================================
print("\nTraining individual models...")
print("-" * 80)

models_list = []

# Model 1: Gradient Boosting (our best performer)
print("\n1. Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=400,
    max_depth=5,
    learning_rate=0.015,
    subsample=0.85,
    min_samples_split=8,
    min_samples_leaf=3,
    max_features='sqrt',
    random_state=42
)
gb_model.fit(X_train_scaled, y_train)
gb_acc = accuracy_score(y_test, gb_model.predict(X_test_scaled))
print(f"   Accuracy: {gb_acc*100:.2f}%")
models_list.append(('gb', gb_model))

# Model 2: XGBoost
if XGBOOST_AVAILABLE:
    print("\n2. XGBoost...")
    xgb_model = XGBClassifier(
        n_estimators=500,
        max_depth=4,
        learning_rate=0.015,
        subsample=0.85,
        colsample_bytree=0.7,
        min_child_weight=5,
        gamma=0.3,
        reg_alpha=1.0,
        reg_lambda=2.0,
        scale_pos_weight=(1 - y_train.mean()) / y_train.mean(),
        random_state=42,
        n_jobs=-1,
        eval_metric='logloss'
    )
    xgb_model.fit(X_train_scaled, y_train, verbose=False)
    xgb_acc = accuracy_score(y_test, xgb_model.predict(X_test_scaled))
    print(f"   Accuracy: {xgb_acc*100:.2f}%")
    models_list.append(('xgb', xgb_model))

# Model 3: LightGBM
if LIGHTGBM_AVAILABLE:
    print("\n3. LightGBM...")
    lgbm_model = LGBMClassifier(
        n_estimators=500,
        max_depth=4,
        learning_rate=0.015,
        subsample=0.85,
        colsample_bytree=0.7,
        min_child_samples=25,
        reg_alpha=1.0,
        reg_lambda=2.0,
        is_unbalance=True,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    lgbm_model.fit(X_train_scaled, y_train)
    lgbm_acc = accuracy_score(y_test, lgbm_model.predict(X_test_scaled))
    print(f"   Accuracy: {lgbm_acc*100:.2f}%")
    models_list.append(('lgbm', lgbm_model))

# Model 4: Random Forest (deep trees)
print("\n4. Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=600,
    max_depth=10,
    min_samples_split=8,
    min_samples_leaf=3,
    max_features='sqrt',
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_train)
rf_acc = accuracy_score(y_test, rf_model.predict(X_test_scaled))
print(f"   Accuracy: {rf_acc*100:.2f}%")
models_list.append(('rf', rf_model))

# ============================================================================
# Create Weighted Ensemble
# ============================================================================
print("\n" + "="*80)
print("Creating Ensemble...")
print("="*80)

# Soft voting ensemble
ensemble_model = VotingClassifier(
    estimators=models_list,
    voting='soft',  # Use probability predictions
    n_jobs=-1
)

ensemble_model.fit(X_train_scaled, y_train)
ensemble_pred = ensemble_model.predict(X_test_scaled)
ensemble_pred_proba = ensemble_model.predict_proba(X_test_scaled)

ensemble_acc = accuracy_score(y_test, ensemble_pred)

print(f"\nEnsemble Accuracy: {ensemble_acc*100:.2f}%")

# ============================================================================
# Advanced: Confidence-Based Predictions
# ============================================================================
print("\n" + "="*80)
print("Confidence-Based Strategy")
print("="*80)

# Only make predictions when confidence > threshold
confidence_thresholds = [0.55, 0.60, 0.65, 0.70]

print("\nAccuracy by confidence threshold:")
for threshold in confidence_thresholds:
    # Get probabilities
    proba = ensemble_pred_proba[:, 1]
    confident_mask = (proba > threshold) | (proba < (1 - threshold))

    if confident_mask.sum() > 0:
        confident_pred = ensemble_pred[confident_mask]
        confident_true = y_test[confident_mask]
        confident_acc = accuracy_score(confident_true, confident_pred)
        coverage = confident_mask.sum() / len(y_test)

        print(f"  Threshold {threshold:.2f}: {confident_acc*100:.2f}% accuracy on {coverage*100:.1f}% of samples ({confident_mask.sum()}/{len(y_test)})")

# ============================================================================
# Final Evaluation
# ============================================================================
print("\n" + "="*80)
print("FINAL RESULTS")
print("="*80)

print(f"\nAccuracy:  {ensemble_acc:.4f} ({ensemble_acc*100:.2f}%)")
print(f"Precision: {precision_score(y_test, ensemble_pred):.4f}")
print(f"Recall:    {recall_score(y_test, ensemble_pred):.4f}")
print(f"F1 Score:  {f1_score(y_test, ensemble_pred):.4f}")
print(f"AUC-ROC:   {roc_auc_score(y_test, ensemble_pred_proba[:, 1]):.4f}")

from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, ensemble_pred)
print(f"\nConfusion Matrix:")
print(f"  TN: {cm[0,0]:4d}  FP: {cm[0,1]:4d}")
print(f"  FN: {cm[1,0]:4d}  TP: {cm[1,1]:4d}")

# Calculate improvement
baseline = 0.50
improvement = (ensemble_acc - baseline) * 100
print(f"\nImprovement over baseline: +{improvement:.2f} percentage points")

# ============================================================================
# Save Final Model
# ============================================================================
print("\n" + "="*80)
print("Saving Model")
print("="*80)

os.makedirs('models', exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
model_name = f"sp500_ensemble_{timestamp}"

joblib.dump(ensemble_model, f"models/{model_name}.pkl")
joblib.dump(scaler, f"models/{model_name}_scaler.pkl")
joblib.dump(selected_features, f"models/{model_name}_features.pkl")
joblib.dump(selector, f"models/{model_name}_selector.pkl")

print(f"\n[OK] Saved: {model_name}")
print(f"     Accuracy: {ensemble_acc*100:.2f}%")
print(f"     Models: {len(models_list)} ({', '.join([name for name, _ in models_list])})")
print(f"     Features: {len(selected_features)}")

# Save metadata
metadata = {
    'model_name': model_name,
    'model_type': 'Soft Voting Ensemble',
    'base_models': [name for name, _ in models_list],
    'accuracy': float(ensemble_acc),
    'precision': float(precision_score(y_test, ensemble_pred)),
    'recall': float(recall_score(y_test, ensemble_pred)),
    'f1_score': float(f1_score(y_test, ensemble_pred)),
    'auc_roc': float(roc_auc_score(y_test, ensemble_pred_proba[:, 1])),
    'features_count': len(selected_features),
    'train_samples': len(X_train),
    'test_samples': len(X_test),
    'created_at': datetime.now().isoformat()
}

import json
with open(f"models/{model_name}_metadata.json", 'w') as f:
    json.dump(metadata, f, indent=2)

# Save selected features
pd.DataFrame({'feature': selected_features}).to_csv(
    f"models/{model_name}_selected_features.csv", index=False
)

print(f"\n[OK] Saved metadata and feature list")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print(f"\nFinal Ensemble Accuracy: {ensemble_acc*100:.2f}%")

if ensemble_acc >= 0.70:
    status = "✓ EXCELLENT - Target achieved!"
elif ensemble_acc >= 0.65:
    status = "GOOD - Close to target, solid performance"
elif ensemble_acc >= 0.60:
    status = "MODERATE - Above baseline, usable"
else:
    status = "NEEDS IMPROVEMENT"

print(f"Status: {status}")

print("\nKey Insights:")
print(f"  - Used {len(selected_features)} most important features")
print(f"  - Ensemble of {len(models_list)} models")
print(f"  - Soft voting for probability-based predictions")
print(f"  - Improvement: +{improvement:.2f} percentage points over random")

print("\nRecommendations:")
print("  - Use confidence threshold >= 0.60 for live predictions")
print("  - Monitor accuracy on new data continuously")
print("  - Retrain monthly with new data")
print("  - Combine with other indicators for best results")

print("\n" + "="*80 + "\n")
