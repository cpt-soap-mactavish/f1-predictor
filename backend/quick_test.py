"""Quick test to compare OLD vs NEW predictor"""
import pandas as pd
import numpy as np
import joblib

print("="*80)
print("BRAZILIAN GP 2024 - PREDICTION COMPARISON")
print("="*80)

# Load model
model = joblib.load('E:/Shivam/F1/f1-ai-predictor/models/race_winner_model_v3.pkl')
with open('E:/Shivam/F1/f1-ai-predictor/models/model_features_v3.txt', 'r') as f:
    features = [line.strip() for line in f.readlines()]

# Load data
df = pd.read_csv('E:/Shivam/F1/f1-ai-predictor/data/f1_race_data_prepared.csv')

# Get 2024 Brazilian GP ACTUAL race data
brazil_2024 = df[(df['season'] == 2024) & (df['round'] == 21)].copy()

if len(brazil_2024) > 0:
    print("\nACTUAL 2024 BRAZILIAN GP GRID (from qualifying):")
    print("-"*80)
    
    # Show actual grid
    grid_sorted = brazil_2024.sort_values('quali_pos').head(10)
    for _, row in grid_sorted.iterrows():
        print(f"  P{int(row['quali_pos']):2d}: {row['driver_id']:20s} ({row['constructor_id']})")
    
    # Get features for prediction
    X = brazil_2024[features]
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    
    brazil_2024['predicted_position'] = predictions + 1
    brazil_2024['win_prob'] = probabilities[:, 0]
    
    # Sort by prediction
    results = brazil_2024.sort_values('predicted_position').head(10)
    
    print("\nNEW PREDICTOR (Using ACTUAL Grid Positions):")
    print("-"*80)
    print(f"{'Pred':<6} {'Driver':<20} {'Actual Grid':<12} {'Win Prob':<10} {'Actual Result'}")
    print("-"*80)
    
    actual_results = {
        'max_verstappen': 1, 'ocon': 2, 'gasly': 3, 'russell': 4, 
        'leclerc': 5, 'norris': 6, 'tsunoda': 7, 'piastri': 8
    }
    
    for _, row in results.iterrows():
        actual_finish = actual_results.get(row['driver_id'], '?')
        emoji = "✅" if actual_finish == int(row['predicted_position']) else ""
        
        print(f"P{int(row['predicted_position']):<5} {row['driver_id']:<20} "
              f"P{int(row['quali_pos']):<11} {row['win_prob']*100:>7.1f}%    "
              f"P{actual_finish} {emoji}")
    
    # Calculate accuracy
    winner_predicted = results.iloc[0]['driver_id']
    winner_actual = 'max_verstappen'
    
    print("\n" + "="*80)
    print("ACCURACY:")
    print(f"  Winner: {'✅ CORRECT' if winner_predicted == winner_actual else f'❌ Wrong (predicted {winner_predicted})'}")
    
    predicted_top3 = set(results.head(3)['driver_id'])
    actual_top3 = {'max_verstappen', 'ocon', 'gasly'}
    overlap = len(predicted_top3 & actual_top3)
    print(f"  Podium: {overlap}/3 drivers correct")
    
else:
    print("❌ No 2024 Brazilian GP data found in database")

print("\n" + "="*80)
print("KEY DIFFERENCE:")
print("  OLD: Used championship standings (Max P1)")
print("  NEW: Uses actual qualifying (Max P17)")
print("="*80)
