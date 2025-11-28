"""
Model V5 - UNIFIED TRAINING
Trains on 6,871 races with aligned historical + OpenF1 features
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.calibration import CalibratedClassifierCV
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("MODEL V5 - UNIFIED TRAINING (Old + New Data)")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load data
print("\n📁 Loading unified dataset...")
df = pd.read_csv('E:/Shivam/F1/f1-ai-predictor/data/f1_race_data_unified_v5.csv')
print(f"✅ Loaded {len(df)} records")

# Create 'has_telemetry' feature
# If gap_trend is not 0 (or we can check year >= 2023), it has telemetry
df['has_telemetry'] = (df['season'] >= 2023).astype(int)

# Select features
feature_cols = [
    # Core Features (Available for all years)
    'quali_pos', 'grid', 'driver_form', 'constructor_form',
    'pace_ratio',          # Aligned (Historical + OpenF1)
    'lap_std_ms',          # Aligned (Historical + OpenF1)
    'num_pit_stops',       # Aligned (Historical + OpenF1)
    'avg_pit_duration', 'recent_pit_form',
    'grid_penalty', 'track_experience',
    'driver_encoded', 'constructor_encoded', 'circuit_encoded',
    
    # New Telemetry Features (Available for 2023+, 0 otherwise)
    'gap_trend', 'overtakes_made', 'positions_gained', 
    'radio_messages', 'safety_car_count',
    'has_telemetry'        # Indicator
]

# Targets
df['winner'] = (df['position'] == 1).astype(int)
df['podium'] = (df['position'] <= 3).astype(int)
df['points'] = (df['position'] <= 10).astype(int)

# Clean data
df_clean = df[feature_cols + ['winner', 'podium', 'points', 'season']].dropna()

print(f"\n✅ Clean dataset: {len(df_clean)} records")
print(f"   Has Telemetry: {df_clean['has_telemetry'].sum()} records")

# Split data
# Train: 2010-2024 (Include 2024 in training as requested)
# Validation: 2025 (Test on the latest data)
train_df = df_clean[df_clean['season'] < 2025]
val_df = df_clean[df_clean['season'] == 2025]

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

# Train Models
print("\n🎓 Training Unified Model V5...")

# 1. Winner Model
print("\n1️⃣  Winner Model (Unified)...")
rf_winner = RandomForestClassifier(
    n_estimators=150,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=4,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
# Calibrate
rf_winner_calibrated = CalibratedClassifierCV(rf_winner, method='sigmoid', cv=3)
rf_winner_calibrated.fit(X_train, y_train_winner)

val_pred_winner = rf_winner_calibrated.predict(X_val)
winner_acc = accuracy_score(y_val_winner, val_pred_winner)
print(f"   ✅ Validation accuracy: {winner_acc:.1%}")

# 2. Podium Model
print("\n2️⃣  Podium Model (Unified)...")
rf_podium = RandomForestClassifier(
    n_estimators=150,
    max_depth=12,
    min_samples_leaf=4,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
rf_podium.fit(X_train, y_train_podium)
val_pred_podium = rf_podium.predict(X_val)
podium_acc = accuracy_score(y_val_podium, val_pred_podium)
print(f"   ✅ Validation accuracy: {podium_acc:.1%}")

# 3. Points Model
print("\n3️⃣  Points Model (Unified)...")
rf_points = RandomForestClassifier(
    n_estimators=150,
    max_depth=12,
    min_samples_leaf=4,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
rf_points.fit(X_train, y_train_points)
val_pred_points = rf_points.predict(X_val)
points_acc = accuracy_score(y_val_points, val_pred_points)
print(f"   ✅ Validation accuracy: {points_acc:.1%}")

# Save models
print("\n💾 Saving models...")
joblib.dump(rf_winner_calibrated, 'E:/Shivam/F1/f1-ai-predictor/backend/models/race_winner_model_v5.pkl')
joblib.dump(rf_podium, 'E:/Shivam/F1/f1-ai-predictor/backend/models/podium_model_v5.pkl')
joblib.dump(rf_points, 'E:/Shivam/F1/f1-ai-predictor/backend/models/points_model_v5.pkl')

# Save features
with open('E:/Shivam/F1/f1-ai-predictor/backend/models/model_features_v5.txt', 'w') as f:
    for feat in feature_cols:
        f.write(f'{feat}\n')

# Feature Importance (Fit base model separately to get importance)
print("\n" + "="*80)
print("TOP 10 FEATURES (Winner Model)")
print("="*80)

rf_base = RandomForestClassifier(
    n_estimators=150,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=4,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
rf_base.fit(X_train, y_train_winner)
importances = rf_base.feature_importances_
feature_importance = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)

for i, (feat, imp) in enumerate(feature_importance[:10], 1):
    print(f"{i:2d}. {feat:25s}: {imp:.4f}")

print("\n" + "="*80)
print("✅ MODEL V5 TRAINING COMPLETE!")
print("="*80)
print(f"  Winner: {winner_acc:.1%}")
print(f"  Podium: {podium_acc:.1%}")
print(f"  Points: {points_acc:.1%}")
print("="*80)
