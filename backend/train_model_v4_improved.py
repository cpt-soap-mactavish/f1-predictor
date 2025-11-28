"""
Model V4 - FIXED VERSION
Addresses overfitting and improves accuracy
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.calibration import CalibratedClassifierCV
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("MODEL V4 - IMPROVED VERSION (Fixing Overfitting)")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load data
print("\n📁 Loading data...")
df = pd.read_csv('E:/Shivam/F1/f1-ai-predictor/data/f1_race_data_prepared.csv')
print(f"✅ Loaded {len(df)} records")

# Select features
feature_cols = [
    'quali_pos', 'grid', 'driver_form', 'constructor_form',
    'pace_ratio', 'recent_pace', 'recent_consistency',
    'num_pit_stops', 'avg_pit_duration', 'recent_pit_form',
    'grid_penalty', 'track_experience',
    'driver_encoded', 'constructor_encoded', 'circuit_encoded'
]

# Target: Winner
df['winner'] = (df['position'] == 1).astype(int)

# Also create podium and points targets for comparison
df['podium'] = (df['position'] <= 3).astype(int)
df['points'] = (df['position'] <= 10).astype(int)

# Clean data
df_clean = df[feature_cols + ['winner', 'podium', 'points', 'season']].dropna()

print(f"\n✅ Clean dataset: {len(df_clean)} records")
print(f"   Winners: {df_clean['winner'].sum()} ({df_clean['winner'].mean()*100:.1f}%)")
print(f"   Podium: {df_clean['podium'].sum()} ({df_clean['podium'].mean()*100:.1f}%)")
print(f"   Points: {df_clean['points'].sum()} ({df_clean['points'].mean()*100:.1f}%)")

# Split data
train_df = df_clean[df_clean['season'] < 2024]
val_df = df_clean[df_clean['season'] == 2024]

X_train = train_df[feature_cols]
y_train_winner = train_df['winner']
y_train_podium = train_df['podium']
y_train_points = train_df['points']

X_val = val_df[feature_cols]
y_val_winner = val_df['winner']
y_val_podium = val_df['podium']
y_val_points = val_df['points']

print(f"\n📊 Data split:")
print(f"   Training: {len(X_train)} records")
print(f"   Validation: {len(X_val)} records")

# IMPROVED MODELS with class balancing and less complexity
print("\n🎓 Training improved models...")

# 1. Winner Prediction (with improvements)
print("\n1️⃣  Winner Prediction Model (IMPROVED)...")
rf_winner = RandomForestClassifier(
    n_estimators=100,          # Reduced from 200
    max_depth=8,               # Reduced from 15
    min_samples_split=10,      # Increased from 5
    min_samples_leaf=5,        # Increased from 2
    class_weight='balanced',   # FIX: Handle class imbalance!
    random_state=42,
    n_jobs=-1
)
rf_winner.fit(X_train, y_train_winner)

# Calibrate probabilities
print("   Calibrating probabilities...")
rf_winner_calibrated = CalibratedClassifierCV(rf_winner, method='sigmoid', cv=3)
rf_winner_calibrated.fit(X_train, y_train_winner)

# Validate
val_pred_winner = rf_winner_calibrated.predict(X_val)
val_prob_winner = rf_winner_calibrated.predict_proba(X_val)[:, 1]
winner_acc = accuracy_score(y_val_winner, val_pred_winner)

print(f"   ✅ Validation accuracy: {winner_acc:.1%}")
print(f"   ✅ ROC-AUC: {roc_auc_score(y_val_winner, val_prob_winner):.3f}")

# 2. Podium Prediction (easier task, better accuracy expected)
print("\n2️⃣  Podium Prediction Model...")
rf_podium = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=8,
    min_samples_leaf=4,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
rf_podium.fit(X_train, y_train_podium)
val_pred_podium = rf_podium.predict(X_val)
podium_acc = accuracy_score(y_val_podium, val_pred_podium)

print(f"   ✅ Validation accuracy: {podium_acc:.1%}")

# 3. Points Finish Prediction (easiest, highest accuracy)
print("\n3️⃣  Points Finish (Top 10) Prediction Model...")
rf_points = RandomForestClassifier(
    n_estimators=100,
    max_depth=12,
    min_samples_split=8,
    min_samples_leaf=4,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
rf_points.fit(X_train, y_train_points)
val_pred_points = rf_points.predict(X_val)
points_acc = accuracy_score(y_val_points, val_pred_points)

print(f"   ✅ Validation accuracy: {points_acc:.1%}")

# Save all models
print("\n💾 Saving models...")
joblib.dump(rf_winner_calibrated, 'E:/Shivam/F1/f1-ai-predictor/backend/models/race_winner_model_v4_improved.pkl')
joblib.dump(rf_podium, 'E:/Shivam/F1/f1-ai-predictor/backend/models/podium_model_v4.pkl')
joblib.dump(rf_points, 'E:/Shivam/F1/f1-ai-predictor/backend/models/points_model_v4.pkl')

# Save features
with open('E:/Shivam/F1/f1-ai-predictor/backend/models/model_features_v4_improved.txt', 'w') as f:
    for feat in feature_cols:
        f.write(f'{feat}\n')

print("✅ Models saved")

# Detailed results
print("\n" + "="*80)
print("VALIDATION RESULTS (2024 Season)")
print("="*80)

print("\n📊 WINNER PREDICTION:")
print(classification_report(y_val_winner, val_pred_winner, 
                          target_names=['Not Winner', 'Winner'], zero_division=0))

print("\n📊 PODIUM PREDICTION:")
print(classification_report(y_val_podium, val_pred_podium, 
                          target_names=['Not Podium', 'Podium'], zero_division=0))

print("\n📊 POINTS FINISH PREDICTION:")
print(classification_report(y_val_points, val_pred_points, 
                          target_names=['No Points', 'Points'], zero_division=0))

# Feature importance
print("\n" + "="*80)
print("TOP 10 MOST IMPORTANT FEATURES (Winner Model)")
print("="*80)

importances = rf_winner.feature_importances_
feature_importance = sorted(zip(feature_cols, importances), 
                           key=lambda x: x[1], reverse=True)

for i, (feat, imp) in enumerate(feature_importance[:10], 1):
    print(f"{i:2d}. {feat:25s}: {imp:.4f}")

# Summary
print("\n" + "="*80)
print("✅ MODEL V4 IMPROVED - TRAINING COMPLETE!")
print("="*80)
print(f"\nAccuracy Summary:")
print(f"  Winner:       {winner_acc:>6.1%}")
print(f"  Podium:       {podium_acc:>6.1%}")
print(f"  Points (Top10): {points_acc:>6.1%}")
print("\nModels saved to: E:/Shivam/F1/f1-ai-predictor/backend/models/")
print("="*80)
