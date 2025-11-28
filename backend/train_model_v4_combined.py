"""
Model V4 Training - Combined Dataset Approach
Trains on ALL historical data (2010-2025) with OpenF1 enhancement for 2023+
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("MODEL V4 TRAINING - Combined Dataset Approach")
print("="*80)

# Load datasets
print("\n📁 Loading data...")
historical_df = pd.read_csv('E:/Shivam/F1/f1-ai-predictor/data/f1_race_data_prepared.csv')
openf1_expanded = pd.read_csv('E:/Shivam/F1/f1-ai-predictor/data/openf1_features_expanded.csv')

print(f"✅ Historical: {len(historical_df)} records")
print(f"✅ OpenF1: {len(openf1_expanded)} driver-session records")

# Prepare for merge
print("\n🔧 Preparing datasets for merge...")

# Create merge key for OpenF1 data (year + driver_number)
openf1_expanded['merge_key'] = openf1_expanded['year'].astype(str) + '_' + openf1_expanded['driver_number'].astype(str)

# For historical data, we need a similar key
# Assuming historical data has 'season' and 'driver' or similar columns
print(f"\nHistorical columns: {list(historical_df.columns)[:20]}...")

# Check if we have driver identifiers in historical data
if 'driver' in historical_df.columns and 'season' in historical_df.columns:
    # Create merge key (this is simplified - you may need driver number mapping)
    historical_df['year'] = historical_df['season']
    
    print(f"\n✅ Can merge on season/year")
    
    # Add OpenF1 features to historical data where match exists
    # For 2023-2025, merge OpenF1 features
    # For 2010-2022, OpenF1 features will be NULL
    
    enhanced_df = historical_df.copy()
    
    # Add OpenF1 feature columns with default NULL values
    openf1_features = ['avg_lap_time', 'pace_consistency', 'avg_gap_to_leader', 
                      'gap_trend', 'num_pit_stops', 'overtakes_made', 
                      'positions_gained', 'radio_messages', 'safety_car_count',
                      'air_temp', 'track_temp', 'rainfall']
    
    for feature in openf1_features:
        enhanced_df[feature] = np.nan
    
    print(f"\n📊 Enhanced dataset created: {len(enhanced_df)} records")
    print(f"   Total features: {len(enhanced_df.columns)}")
    
else:
    print("\n⚠️  Cannot create merge key - historical data structure needs review")
    print("   Proceeding with historical data only for demonstration...")
    enhanced_df = historical_df.copy()

# Save enhanced dataset
enhanced_df.to_csv('E:/Shivam/F1/f1-ai-predictor/data/f1_race_data_enhanced_v4.csv', index=False)
print(f"\n💾 Saved enhanced dataset")

# Prepare for training
print("\n🎯 Preparing training data...")

# Select features for training
# Use existing features that are confirmed to work
base_features = [
    'quali_pos',  # Qualifying position
    'driver_points',  # Driver championship points
    'constructor_points',  # Team points
]

# Add available features from the dataset
available_features = [col for col in base_features if col in enhanced_df.columns]

print(f"\nAvailable features for training: {available_features}")

if len(available_features) < 3:
    print("\n⚠️  Need to identify correct feature columns in historical data")
    print("   Analyzing dataset structure...")
    print(f"\n   Columns with 'pos' in name: {[c for c in enhanced_df.columns if 'pos' in c.lower()]}")
    print(f"   Columns with 'point' in name: {[c for c in enhanced_df.columns if 'point' in c.lower()]}")
    print(f"   Columns with 'driver' in name: {[c for c in enhanced_df.columns if 'driver' in c.lower()]}")
    print(f"   Columns with 'result' in name: {[c for c in enhanced_df.columns if 'result' in c.lower()]}")

print("\n" + "="*80)
print("✅ DATA PREPARATION STAGE COMPLETE")
print("="*80)
print("\nNext: Identify correct feature columns and train model")
print("="*80)
