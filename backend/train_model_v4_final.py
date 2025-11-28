"""
Model V4 - Final Training Script
Trains on ALL historical data (2010-2025) with OpenF1 enhancement
Target: 60-65% winner accuracy
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
from datetime import datetime

print("="*80)
print("MODEL V4 - FINAL TRAINING")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load data
print("\n📁 Loading data...")
df = pd.read_csv('E:/Shivam/F1/f1-ai-predictor/data/f1_race_data_prepared.csv')
openf1_features = pd.read_csv('E:/Shivam/F1/f1-ai-predictor/data/openf1_features_expanded.csv')

print(f"✅ Historical: {len(df)} records")
print(f"✅ OpenF1: {len(openf1_features)} driver-session records")

# Select training features
feature_cols = [
    'quali_pos',           # Qualifying position (strongest predictor)
    'grid',                # Actual grid position (with penalties)
    'driver_form',         # Recent driver performance
    'constructor_form',    # Recent team performance
    'pace_ratio',          # Race pace vs field
    'recent_pace',         # Recent race pace
    'recent_consistency',  # Lap time consistency
    'num_pit_stops',       # Pit strategy
    'avg_pit_duration',    # Pit efficiency
    'recent_pit_form',     # Recent pit performance
    'grid_penalty',        # Grid penalty indicator
    'track_experience',    # Driver experience at circuit
    'driver_encoded',      # Driver ID (encoded)
    'constructor_encoded', # Team ID (encoded)
    'circuit_encoded',     # Circuit ID (encoded)
]

# Create target variable (1 = winner, 0 = not winner)
df['winner'] = (df['position'] == 1).astype(int)

print(f"\n🎯 Training features: {len(feature_cols)}")
for i, feat in enumerate(feature_cols, 1):
    print(f"   {i}. {feat}")

# Prepare training data
print("\n🔧 Preparing training data...")

# Remove rows with missing values in key features
df_clean = df[feature_cols + ['winner', 'season']].dropna()

print(f"✅ Clean dataset: {len(df_clean)} records")
print(f"   Winners: {df_clean['winner'].sum()}")
print(f"   Non-winners: {len(df_clean) - df_clean['winner'].sum()}")

# Split data: 
# Train: 2020-2023
# Validation: 2024
# Test: 2025 (if available)

train_df = df_clean[df_clean['season'] < 2024]
val_df = df_clean[df_clean['season'] == 2024]
test_df = df_clean[df_clean['season'] >= 2025]

X_train = train_df[feature_cols]
y_train = train_df['winner']

X_val = val_df[feature_cols]
y_val = val_df['winner']

print(f"\n📊 Data split:")
print(f"   Training: {len(X_train)} records (seasons < 2024)")
print(f"   Validation: {len(X_val)} records (season 2024)")
print(f"   Test: {len(test_df)} records (season >= 2025)")

# Train ensemble
print("\n🎓 Training models...")

print("\n1️⃣  Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)
rf_train_acc = accuracy_score(y_train, rf_model.predict(X_train))
rf_val_acc = accuracy_score(y_val, rf_model.predict(X_val))
print(f"   ✅ Train accuracy: {rf_train_acc:.1%}")
print(f"   ✅ Validation accuracy: {rf_val_acc:.1%}")

print("\n2️⃣  Training Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)
gb_model.fit(X_train, y_train)
gb_train_acc = accuracy_score(y_train, gb_model.predict(X_train))
gb_val_acc = accuracy_score(y_val, gb_model.predict(X_val))
print(f"   ✅ Train accuracy: {gb_train_acc:.1%}")
print(f"   ✅ Validation accuracy: {gb_val_acc:.1%}")

# Ensemble prediction (average)
print("\n🔮 Creating ensemble...")
val_pred_rf = rf_model.predict_proba(X_val)[:, 1]
val_pred_gb = gb_model.predict_proba(X_val)[:, 1]
val_pred_ensemble = (val_pred_rf * 0.6 + val_pred_gb * 0.4)
val_pred_ensemble_binary = (val_pred_ensemble > 0.5).astype(int)

ensemble_val_acc = accuracy_score(y_val, val_pred_ensemble_binary)
print(f"✅ Ensemble validation accuracy: {ensemble_val_acc:.1%}")

# Save models
print("\n💾 Saving models...")
joblib.dump(rf_model, 'E:/Shivam/F1/f1-ai-predictor/backend/models/race_winner_model_v4_rf.pkl')
joblib.dump(gb_model, 'E:/Shivam/F1/f1-ai-predictor/backend/models/race_winner_model_v4_gb.pkl')

# Save feature list
with open('E:/Shivam/F1/f1-ai-predictor/backend/models/model_features_v4.txt', 'w') as f:
    for feat in feature_cols:
        f.write(f'{feat}\n')

print("✅ Models saved")

# Detailed validation results
print("\n" + "="*80)
print("VALIDATION RESULTS (2024 Season)")
print("="*80)

print("\nConfusion Matrix:")
cm = confusion_matrix(y_val, val_pred_ensemble_binary)
print(cm)

print("\nClassification Report:")
print(classification_report(y_val, val_pred_ensemble_binary, 
                          target_names=['Not Winner', 'Winner']))

# Feature importance
print("\n" + "="*80)
print("TOP 10 MOST IMPORTANT FEATURES")
print("="*80)

importances = rf_model.feature_importances_
feature_importance = sorted(zip(feature_cols, importances), 
                           key=lambda x: x[1], reverse=True)

for i, (feat, imp) in enumerate(feature_importance[:10], 1):
    print(f"{i}. {feat:25s}: {imp:.4f}")

print("\n" + "="*80)
print("✅ MODEL V4 TRAINING COMPLETE!")
print("="*80)
print(f"\nFinal ensemble accuracy: {ensemble_val_acc:.1%}")
print(f"Models saved to: E:/Shivam/F1/f1-ai-predictor/backend/models/")
print("="*80)
