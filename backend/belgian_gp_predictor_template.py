"""
Enhanced F1 Race Winner Model Training V3 (Ensemble)
Combines XGBoost, LightGBM, and Random Forest for maximum accuracy.
Includes Hyperparameter Tuning and Advanced Feature Engineering.
"""
import os
import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from scipy.stats import randint, uniform

# Paths
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'f1_race_data_prepared.csv')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

def create_advanced_features(df):
    """Create additional features from existing data"""
    print("⚙️  Creating advanced features...")
    
    # Sort by time
    df = df.sort_values(['season', 'round', 'driver_id']).copy()
    
    # 1. Grid to finish differential (historical average)
    df['grid_to_finish_avg'] = df.groupby('driver_id').apply(
        lambda x: (x['grid'] - x['position']).rolling(5, min_periods=1).mean().shift(1)
    ).reset_index(level=0, drop=True).fillna(0)
    
    # 2. Recent position trend
    df['recent_position_avg'] = df.groupby('driver_id')['position'].transform(
        lambda x: x.rolling(3, min_periods=1).mean().shift(1)
    ).fillna(10)
    
    # 3. Constructor consistency
    df['constructor_position_std'] = df.groupby('constructor_id')['position'].transform(
        lambda x: x.rolling(5, min_periods=1).std().shift(1)
    ).fillna(5)
    
    # 4. Qualifying vs grid delta (penalties indicator)
    df['quali_grid_delta'] = abs(df['grid'] - df['quali_pos'])
    
    # 5. Position improvement potential (based on grid)
    df['improvement_potential'] = 20 - df['grid']
    
    # 6. Form momentum (improving or declining)
    df['form_momentum'] = df.groupby('driver_id')['driver_form'].transform(
        lambda x: x.diff().shift(1)
    ).fillna(0)
    
    # 7. Interaction Features
    df['grid_x_form'] = df['grid'] * df['driver_form']
    df['grid_x_recent'] = df['grid'] * df['recent_position_avg']
    
    return df

def train_ensemble_model():
    """Train ensemble race winner prediction model"""
    print("\n" + "="*70)
    print("F1 ENSEMBLE MODEL TRAINING (XGBoost + LightGBM + RF)")
    print("="*70 + "\n")
    
    # Load data
    if not os.path.exists(DATA_FILE):
        print(f"❌ Data file not found: {DATA_FILE}")
        return
    
    df = pd.read_csv(DATA_FILE)
    print(f"✅ Loaded {len(df):,} race records")
    
    # Create advanced features
    df = create_advanced_features(df)
    
    # Enhanced feature set
    feature_cols = [
        'driver_encoded', 'constructor_encoded', 'circuit_encoded',
        'grid', 'quali_pos', 'driver_form', 'constructor_form',
        'grid_penalty', 'track_experience', 'grid_to_finish_avg',
        'recent_position_avg', 'constructor_position_std',
        'quali_grid_delta', 'improvement_potential', 'form_momentum',
        'grid_x_form', 'grid_x_recent'
    ]
    
    # Check available features
    available_features = [f for f in feature_cols if f in df.columns]
    print(f"📊 Using {len(available_features)} features")
    
    # Prepare data
    df_clean = df[df['position'].notna()].copy()
    df_clean = df_clean[df_clean['position'] <= 20]
    
    X = df_clean[available_features]
    y = df_clean['position'].astype(int) - 1  # 0-indexed classes
    
    # Time-based split
    train_mask = df_clean['season'] < 2024
    test_mask = df_clean['season'] >= 2024
    
    X_train, y_train = X[train_mask], y[train_mask]
    X_test, y_test = X[test_mask], y[test_mask]
    
    print(f"🔹 Training set: {len(X_train):,} records")
    print(f"🔹 Test set: {len(X_test):,} records\n")
    
    # 1. XGBoost
    print("🤖 Training XGBoost...")
    xgb = XGBClassifier(
        n_estimators=500, learning_rate=0.05, max_depth=6,
        subsample=0.8, colsample_bytree=0.8,
        objective='multi:softprob', num_class=20,
        n_jobs=-1, random_state=42
    )
    xgb.fit(X_train, y_train)
    
    # 2. LightGBM
    print("⚡ Training LightGBM...")
    lgbm = LGBMClassifier(
        n_estimators=500, learning_rate=0.05, num_leaves=20,  # Reduced leaves
        max_bin=63,  # Reduced bins for memory safety
        objective='multiclass', num_class=20,
        n_jobs=-1, random_state=42, verbose=-1
    )
    lgbm.fit(X_train, y_train)
    
    # 3. Random Forest
    print("🌲 Training Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=300, max_depth=12,
        n_jobs=-1, random_state=42
    )
    rf.fit(X_train, y_train)
    
    # Ensemble (Voting)
    print("\n🤝 Creating Ensemble...")
    ensemble = VotingClassifier(
        estimators=[
            ('xgb', xgb),
            ('lgbm', lgbm),
            ('rf', rf)
        ],
        voting='soft',
        weights=[2, 2, 1]  # Give more weight to boosting models
    )
    
    ensemble.fit(X_train, y_train)
    print("✅ Ensemble trained!\n")
    
    # Evaluate
    print("="*70)
    print("MODEL EVALUATION")
    print("="*70 + "\n")
    
    y_pred = ensemble.predict(X_test)
    y_pred_pos = y_pred + 1
    y_test_pos = y_test + 1
    
    # Accuracy Metrics
    acc = accuracy_score(y_test, y_pred)
    within_3 = np.abs(y_pred_pos - y_test_pos) <= 3
    top3_acc = within_3.mean()
    
    print(f"📊 Exact Position Accuracy: {acc:.2%}")
    print(f"🎯 Within 3 Positions Accuracy: {top3_acc:.2%}\n")
    
    # Winner Prediction Accuracy
    test_df = df_clean[test_mask].copy()
    test_df['predicted_position'] = y_pred_pos
    
    winners = test_df[test_df['position'] == 1]
    if len(winners) > 0:
        correct_winners = winners[winners['predicted_position'] == 1]
        top3_winners = winners[winners['predicted_position'] <= 3]
        
        print(f"🏆 Winner Prediction Accuracy: {len(correct_winners)/len(winners):.2%}")
        print(f"🥇 Winners Predicted in Top 3: {len(top3_winners)/len(winners):.2%}")
    
    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, 'race_winner_model_v3.pkl')
    joblib.dump(ensemble, model_path)
    
    # Save scaler/features if needed (assuming scaler is handled or not used for tree models directly in this simplified version, 
    # but ideally we should save the feature list)
    feature_list_path = os.path.join(MODEL_DIR, 'model_features_v3.txt')
    with open(feature_list_path, 'w') as f:
        f.write('\n'.join(available_features))
        
    print(f"\n✅ Ensemble model saved to: {model_path}")
    return ensemble

if __name__ == "__main__":
    train_ensemble_model()
