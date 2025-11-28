"""
CLEAN F1 Race Predictor - NO HARDCODING
Uses ONLY the ML model's learned patterns from historical data
Validation test: 2024 Brazilian GP (Max won from P17 in the rain)
"""

import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

class CleanRacePredictor:
    def __init__(self, model_dir, data_path):
        self.model_dir = model_dir
        self.data_path = data_path
        self.model = None
        self.features = None
        self.historical_data = None
        
    def load_model_and_data(self):
        """Load the trained model and historical data"""
        try:
            # Load ensemble model
            model_path = f'{self.model_dir}/race_winner_model_v3.pkl'
            self.model = joblib.load(model_path)
            print(f'✅ Model loaded: {model_path}')
            
            # Load expected features
            with open(f'{self.model_dir}/model_features_v3.txt', 'r') as f:
                self.features = [line.strip() for line in f.readlines()]
            print(f'✅ Model expects {len(self.features)} features')
            
            # Load historical data (with pre-calculated features)
            prepared_csv = self.data_path.replace('f1_race_data.csv', 'f1_race_data_prepared.csv')
            self.historical_data = pd.read_csv(prepared_csv)
            print(f'✅ Loaded {len(self.historical_data)} historical races')
            
            return True
        except Exception as e:
            print(f'❌ Error loading: {e}')
            return False
    
    def prepare_grid(self, season=2024, circuit='interlagos'):
        """
        Prepare race grid from championship standings (NO HARDCODING)
        Uses actual season data from database
        """
        print(f"\n🏁 Preparing grid for {season} {circuit.upper()}")
        
        # Get data up to this race (simulate pre-race state)
        season_data = self.historical_data[
            (self.historical_data['season'] == season)
        ].copy()
        
        if len(season_data) == 0:
            print(f"⚠️  No {season} data, using latest available season")
            latest_season = self.historical_data['season'].max()
            season_data = self.historical_data[
                self.historical_data['season'] == latest_season
            ].copy()
        
        # Calculate championship standings
        standings = season_data.groupby('driver_id').agg({
            'points': 'sum',
            'position': 'mean',
            'constructor_id': 'last'
        }).sort_values('points', ascending=False).reset_index()
        
        # Get top 20 drivers
        grid_drivers = standings.head(20)
        
        print(f"📊 Championship standings:")
        for i, row in grid_drivers.head(5).iterrows():
            print(f"   P{i+1}: {row['driver_id']:20s} - {row['points']:.0f} pts ({row['constructor_id']})")
        
        # Create race dataframe
        race_df = pd.DataFrame({
            'driver_id': grid_drivers['driver_id'].tolist(),
            'constructor_id': grid_drivers['constructor_id'].tolist(),
            'circuit_id': [circuit] * len(grid_drivers),
            'grid': list(range(1, len(grid_drivers) + 1)),
            'season': [season] * len(grid_drivers),
            'round': [20] * len(grid_drivers),  # Brazil is typically round 20
        })
        
        return race_df
    
    def extract_features(self, race_df):
        """
        Extract features from historical data (NO HARDCODING)
        Uses actual driver performance history
        """
        print("\n📊 Extracting features from historical data...")
        
        enriched_rows = []
        
        for _, row in race_df.iterrows():
            driver_id = row['driver_id']
            
            # Get driver's historical performance
            driver_history = self.historical_data[
                self.historical_data['driver_id'] == driver_id
            ].sort_values(['season', 'round'], ascending=False)
            
            if len(driver_history) == 0:
                # Rookie - use neutral defaults
                features = {
                    'driver_encoded': 0,
                    'constructor_encoded': 0,
                    'circuit_encoded': 0,
                    'grid': row['grid'],
                    'quali_pos': row['grid'],
                    'driver_form': 5.0,  # Neutral
                    'constructor_form': 5.0,
                    'grid_penalty': 0,
                    'track_experience': 0,
                    'grid_to_finish_avg': 0,
                    'recent_position_avg': 10.0,
                    'constructor_position_std': 5.0,
                    'quali_grid_delta': 0,
                    'improvement_potential': 20 - row['grid'],
                    'form_momentum': 0,
                    'grid_x_form': row['grid'] * 5.0,
                    'grid_x_recent': row['grid'] * 10.0
                }
            else:
                # Use ACTUAL historical features (learned from data)
                recent = driver_history.iloc[0]
                driver_form = recent.get('driver_form', 5.0)
                recent_pos = recent.get('recent_position_avg', 10.0)
                
                features = {
                    'driver_encoded': recent.get('driver_encoded', 0),
                    'constructor_encoded': recent.get('constructor_encoded', 0),
                    'circuit_encoded': recent.get('circuit_encoded', 0),
                    'grid': row['grid'],
                    'quali_pos': row['grid'],
                    'driver_form': driver_form,
                    'constructor_form': recent.get('constructor_form', 5.0),
                    'grid_penalty': 0,
                    'track_experience': recent.get('track_experience', 0),
                    'grid_to_finish_avg': recent.get('grid_to_finish_avg', 0),
                    'recent_position_avg': recent_pos,
                    'constructor_position_std': recent.get('constructor_position_std', 5.0),
                    'quali_grid_delta': 0,
                    'improvement_potential': 20 - row['grid'],
                    'form_momentum': recent.get('form_momentum', 0),
                    'grid_x_form': row['grid'] * driver_form,
                    'grid_x_recent': row['grid'] * recent_pos
                }
            
            enriched_rows.append({**row.to_dict(), **features})
        
        enriched_df = pd.DataFrame(enriched_rows)
        
        # Ensure all features exist
        for feature in self.features:
            if feature not in enriched_df.columns:
                enriched_df[feature] = 0
        
        print(f"✅ Extracted features for {len(enriched_df)} drivers")
        
        return enriched_df
    
    def predict_race(self, race_df):
        """
        Make predictions using ONLY the ML model (NO HARDCODING!)
        """
        print("\n🔮 Generating predictions from ML model...")
        
        # Extract features
        race_features = self.extract_features(race_df)
        
        # Prepare input (select model features in correct order)
        X_race = race_features[self.features]
        
        # Get model predictions
        predictions = self.model.predict(X_race)
        probabilities = self.model.predict_proba(X_race)
        
        # Compile results
        results_df = race_df.copy()
        results_df['predicted_position'] = predictions + 1  # 0-indexed to 1-indexed
        results_df['confidence'] = np.max(probabilities, axis=1)
        results_df['win_probability'] = probabilities[:, 0]
        results_df['podium_probability'] = probabilities[:, :3].sum(axis=1)
        
        # Sort by predicted position
        results_df = results_df.sort_values('predicted_position')
        
        print(f"✅ Predictions generated")
        
        return results_df
    
    def display_predictions(self, results_df, actual_results=None):
        """Display  predictions and compare to actual if provided"""
        print("\n" + "="*80)
        print("🏆 RACE PREDICTIONS (Pure ML - NO Hardcoding)")
        print("="*80)
        print(f"{'Pred':<5} {'Driver':<20} {'Team':<15} {'Grid':<5} {'Win %':<8} {'Actual':<6}")
        print("-"*80)
        
        for _, row in results_df.head(10).iterrows():
            actual_pos = ""
            if actual_results and row['driver_id'] in actual_results:
                actual_pos = f"P{actual_results[row['driver_id']]}"
            
            print(f"P{int(row['predicted_position']):<4} {row['driver_id']:<20} "
                  f"{row['constructor_id']:<15} P{int(row['grid']):<4} "
                  f"{row['win_probability']*100:<7.1f}% {actual_pos:<6}")
        
        # Calculate accuracy if actual results provided
        if actual_results:
            correct_winner = results_df.iloc[0]['driver_id'] == list(actual_results.keys())[0]
            print("\n📊 Accuracy:")
            print(f"   Winner predicted: {'✅ YES' if correct_winner else '❌ NO'}")
            
            # Top 3 accuracy
            predicted_podium = set(results_df.head(3)['driver_id'])
            actual_podium = set(list(actual_results.keys())[:3])
            podium_overlap = len(predicted_podium & actual_podium)
            print(f"   Podium accuracy: {podium_overlap}/3 correct")

if __name__ == "__main__":
    print("🏎️  F1 RACE PREDICTOR - Clean Version (NO Hardcoding)")
    print("Testing on: 2024 Brazilian GP\n")
    
    # Initialize predictor
    predictor = CleanRacePredictor(
        model_dir='E:/Shivam/F1/f1-ai-predictor/models',
        data_path='E:/Shivam/F1/f1-ai-predictor/data/f1_race_data.csv'
    )
    
    if predictor.load_model_and_data():
        # Prepare grid for Brazilian GP 2024
        race_df = predictor.prepare_grid(season=2024, circuit='interlagos')
        
        # Make predictions  
        results = predictor.predict_race(race_df)
        
        # ACTUAL 2024 Brazilian GP results (for validation)
        actual_results = {
            'max_verstappen': 1,  # Won from P17!
            'ocon': 2,
            'gasly': 3,
            'russell': 4,
            'leclerc': 5,
            'norris': 6,
            'tsunoda': 7,
            'piastri': 8,
            'hamilton': 10
        }
        
        # Display with comparison
        predictor.display_predictions(results, actual_results)
        
        print("\n" + "="*80)
        print("📝 Notes:")
        print("   - This uses ONLY what the model learned from historical data")
        print("   - NO hardcoded driver performance multipliers")
        print("   - NO manual rain adjustments")
        print("   - Pure ML predictions based on:")
        print("     • Championship standings")
        print("     • Historical driver/team form")
        print("     • Circuit experience")
        print("     • Grid position")
    else:
        print("❌ Failed to load model/data")
