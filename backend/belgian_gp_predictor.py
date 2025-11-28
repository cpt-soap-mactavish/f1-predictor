import pandas as pd
import numpy as np
import joblib
import requests
import warnings
import os

warnings.filterwarnings('ignore')

# F1 Circuit Database with real data
CIRCUIT_DATA = {
    'spa': {
        'name': 'Belgian GP',
        'laps': 44,
        'length_km': 7.004,
        'overtaking_difficulty': 'medium',
        'safety_car_probability': 0.35,  # Historical average
        'tire_deg_factor': 1.3  # High degradation track
    },
    'monaco': {
        'name': 'Monaco GP',
        'laps': 78,
        'length_km': 3.337,
        'overtaking_difficulty': 'very_high',
        'safety_car_probability': 0.75,  # Safety car almost guaranteed
        'tire_deg_factor': 0.7  # Low degradation (slow corners)
    },
    'monza': {
        'name': 'Italian GP',
        'laps': 53,
        'length_km': 5.793,
        'overtaking_difficulty': 'low',
        'safety_car_probability': 0.25,
        'tire_deg_factor': 1.2  # High speed = high deg
    },
    'singapore': {
        'name': 'Singapore GP',
        'laps': 62,
        'length_km': 4.940,
        'overtaking_difficulty': 'high',
        'safety_car_probability': 0.65,  # Street circuit
        'tire_deg_factor': 1.1
    },
    'zandvoort': {
        'name': 'Dutch GP',
        'laps': 72,
        'length_km': 4.259,
        'overtaking_difficulty': 'high',
        'safety_car_probability': 0.30,
        'tire_deg_factor': 1.0
    },
    'baku': {
        'name': 'Azerbaijan GP',
        'laps': 51,
        'length_km': 6.003,
        'overtaking_difficulty': 'medium',
        'safety_car_probability': 0.70,  # Street circuit chaos
        'tire_deg_factor': 0.9
    }
}

# Tire compound performance characteristics
TIRE_COMPOUNDS = {
    'soft': {
        'pace_advantage': 0.8,  # seconds per lap faster
        'degradation_rate': 1.5,  # degrades 50% faster
        'optimal_stint_length': 15,  # laps
        'warm_up_time': 1  # laps to reach peak
    },
    'medium': {
        'pace_advantage': 0.0,  # baseline
        'degradation_rate': 1.0,
        'optimal_stint_length': 25,
        'warm_up_time': 2
    },
    'hard': {
        'pace_advantage': -0.5,  # slower but lasts
        'degradation_rate': 0.6,
        'optimal_stint_length': 40,
        'warm_up_time': 3
    }
}

class BelgianGPPredictor:
    def __init__(self, model_dir, data_path, weather_api_key):
        self.model_dir = model_dir
        self.data_path = data_path
        self.weather_api_key = weather_api_key
        self.model = None
        self.features = None
        self.historical_data = None
        
    def fetch_weather_forecast(self, lat=50.4372, lon=5.9714):
        """Fetch weather forecast"""
        print("🌤️  Fetching weather...")
        url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            forecast = data['list'][0]
            return {
                'temperature': forecast['main']['temp'],
                'humidity': forecast['main']['humidity'],
                'rain_probability': forecast.get('pop', 0) * 100,
            }
        except:
            return {'temperature': 20.0, 'humidity': 60.0, 'rain_probability': 20}

    def load_model_and_data(self):
        """Load model and prepared historical data"""
        try:
            v3_path = f'{self.model_dir}/race_winner_model_v3.pkl'
            self.model = joblib.load(v3_path)
            print(f'✅ Ensemble Model V3 loaded')
            
            with open(f'{self.model_dir}/model_features_v3.txt', 'r') as f:
                self.features = [line.strip() for line in f.readlines()]
            print(f'✅ Model expects {len(self.features)} features')

            prepared_csv = self.data_path.replace('f1_race_data.csv', 'f1_race_data_prepared.csv')
            self.historical_data = pd.read_csv(prepared_csv)
            self.historical_data = self.historical_data[self.historical_data['season'] >= 2020].copy()
            print(f'✅ Loaded {len(self.historical_data)} prepared records (2020+)')
            return True
        except Exception as e:
            print(f'❌ Error: {e}')
            import traceback
            traceback.print_exc()
            return False

    def calculate_tire_strategy(self, circuit, start_compound, pit_stops, race_laps):
        """
        Calculate optimal tire strategy based on compound and pit stops
        Returns performance modifier
        """
        compound_data = TIRE_COMPOUNDS[start_compound]
        circuit_deg = CIRCUIT_DATA[circuit]['tire_deg_factor']
        
        # Calculate average stint length
        avg_stint = race_laps / (pit_stops + 1)
        
        # Performance calculation
        if start_compound == 'soft':
            if pit_stops >= 2:
                # Soft works well with 2+ stops
                return 1.08
            elif avg_stint > compound_data['optimal_stint_length']:
                # Stint too long for soft = major degradation
                return 0.75
            else:
                return 1.00
        
        elif start_compound == 'medium':
            if pit_stops == 1:
                # Medium ideal for 1-stop
                return 1.05
            elif pit_stops == 2:
                return 1.02
            else:
                return 0.95
        
        elif start_compound == 'hard':
            if pit_stops <= 1 and race_laps > 50:
                # Hard ideal for long races, 1-stop
                return 1.10
            elif pit_stops == 0:
                # Risky but possible
                return 0.90
            else:
                # Hard with multiple stops is slow
                return 0.85
        
        return 1.0

    def apply_strategy_logic(self, results_df, simulation_params):
        """
        SMART F1 Strategy Logic - Phase 1
        Considers: Weather, Tires, Safety Cars, Circuit Characteristics
        """
        if not simulation_params:
            return results_df

        print("🧠 Applying SMART F1 Strategy Logic...")
        
        # Extract parameters
        rain_prob = simulation_params.get('rain_prob', 0)
        is_wet = rain_prob > 50
        tire = simulation_params.get('tire', 'medium').lower()
        pit_stops = simulation_params.get('pit_stops', 2)
        circuit = simulation_params.get('circuit', 'spa')
        air_temp = simulation_params.get('air_temp', 20)
        safety_car_risk = simulation_params.get('safety_car', 'medium')
        
        # Get circuit data
        circuit_info = CIRCUIT_DATA.get(circuit, CIRCUIT_DATA['spa'])
        race_laps = circuit_info['laps']
        
        print(f"📍 Circuit: {circuit_info['name']} - {race_laps} laps")
        
        # 1. CURRENT FORM & CAR PERFORMANCE (2025 reality)
        # McLaren is DOMINANT in dry 2025, Red Bull competitive in wet
        current_form = {
            'norris': {'dry': 1.15, 'wet': 1.25, 'team': 'mclaren'},
            'piastri': {'dry': 1.12, 'wet': 1.15, 'team': 'mclaren'},
            'max_verstappen': {'dry': 1.08, 'wet': 1.40, 'team': 'red_bull'},  # Rain master
            'hamilton': {'dry': 1.05, 'wet': 1.35, 'team': 'ferrari'},
            'leclerc': {'dry': 1.06, 'wet': 1.20, 'team': 'ferrari'},
            'russell': {'dry': 1.04, 'wet': 1.15, 'team': 'mercedes'},
            'sainz': {'dry': 1.03, 'wet': 1.10, 'team': 'williams'},
            'alonso': {'dry': 1.02, 'wet': 1.30, 'team': 'aston_martin'}
        }
        
        # Apply form based on weather
        condition = 'wet' if is_wet else 'dry'
        print(f"🌦️  Conditions: {'WET' if is_wet else 'DRY'} - Applying {condition} form")
        
        for driver, form_data in current_form.items():
            mask = results_df['driver_id'] == driver
            if mask.any():
                boost = form_data.get(condition, 1.0)
                results_df.loc[mask, 'win_probability'] *= boost
                if boost > 1.10:
                    print(f"   ✓ {driver}: {boost:.2f}x boost")
        
        # 2. TIRE STRATEGY (compound-specific performance)
        if not is_wet:
            tire_modifier = self.calculate_tire_strategy(circuit, tire, pit_stops, race_laps)
            print(f"🛞 Tire Strategy: {tire.upper()} start, {pit_stops} stops = {tire_modifier:.2f}x")
            results_df['win_ probability'] *= tire_modifier
        else:
            # Rain - only wet/intermediate tires work
            if tire not in ['intermediate', 'wet']:
                print(f"⚠️  CRITICAL: {tire.upper()} tires in rain = disaster!")
                results_df['win_probability'] *= 0.05
        
        # 3. SAFETY CAR IMPACT
        sc_prob_map = {'low': 0.2, 'medium': 0.5, 'high': 0.8}
        sc_likelihood = sc_prob_map.get(safety_car_risk, 0.5)
        
        if sc_likelihood > 0.5:
            # Safety car favors aggressive drivers and good restarters
            aggressive = ['max_verstappen', 'leclerc', 'norris', 'hamilton']
            print(f"🚨 Safety Car likely ({sc_likelihood:.0%}) - Boosting aggressive drivers")
            for driver in aggressive:
                mask = results_df['driver_id'] == driver
                if mask.any():
                    results_df.loc[mask, 'win_probability'] *= 1.10
        
        # 4. PIT STOP PENALTIES
        if pit_stops < 1:
            print("⚠️  Zero stops = tire failure!")
            results_df['win_probability'] *= 0.10
        elif pit_stops > 3:
            print("⚠️  Too many stops = lost time!")
            results_df['win_probability'] *= 0.70
        
        # NORMALIZE
        total = results_df['win_probability'].sum()
        if total > 0:
            results_df['win_probability'] /= total
            
        return results_df

    def prepare_race_data(self, circuit='spa'):
        """Prepare race grid from 2025 championship standings"""
        print(f"🏁 Preparing grid for {CIRCUIT_DATA.get(circuit, {}).get('name', circuit.upper())}...")
        
        latest_season = self.historical_data['season'].max()
        season_data = self.historical_data[self.historical_data['season'] == latest_season].copy()
        
        standings = season_data.groupby('driver_id').agg({
            'points': 'sum',
            'position': 'mean',
            'constructor_id': 'last'
        }).sort_values('points', ascending=False).reset_index()
        
        grid_drivers = standings.head(20)
        
        print(f"📊 2025 Championship Top 5:")
        for i, row in grid_drivers.head(5).iterrows():
            print(f"   P{i+1}: {row['driver_id']} ({row['constructor_id']}) - {row['points']:.0f} pts")
        
        race_df = pd.DataFrame({
            'driver_id': grid_drivers['driver_id'].tolist(),
            'constructor_id': grid_drivers['constructor_id'].tolist(),
            'circuit_id': [circuit] * len(grid_drivers),
            'grid': list(range(1, len(grid_drivers) + 1)),
            'season': [latest_season] * len(grid_drivers),
            'round': [13] * len(grid_drivers),
        })
        
        weather = self.fetch_weather_forecast()
        race_df['temperature'] = weather['temperature']
        race_df['humidity'] = weather['humidity']
        race_df['rain_probability'] = weather['rain_probability']
        
        return race_df

    def extract_features(self, race_df):
        """Extract features from prepared data"""
        print("📊 Extracting features...")
        
        enriched_rows = []
        
        for _, row in race_df.iterrows():
            driver_id = row['driver_id']
            
            driver_hist = self.historical_data[
                self.historical_data['driver_id'] == driver_id
            ].sort_values(['season', 'round'], ascending=False)
            
            if len(driver_hist) == 0:
                features = {
                    'driver_encoded': 0, 'constructor_encoded': 0, 'circuit_encoded': 0,
                    'grid': row['grid'], 'quali_pos': row['grid'],
                    'driver_form': 10.0, 'constructor_form': 10.0,
                    'grid_penalty': 0, 'track_experience': 0,
                    'grid_to_finish_avg': 0, 'recent_position_avg': 15.0,
                    'constructor_position_std': 5.0, 'quali_grid_delta': 0,
                    'improvement_potential': 20 - row['grid'],
                    'form_momentum': 0, 'grid_x_form': row['grid'] * 10.0,
                    'grid_x_recent': row['grid'] * 15.0
                }
            else:
                recent = driver_hist.iloc[0]
                driver_form = recent.get('driver_form', 10.0)
                recent_pos_avg = recent.get('recent_position_avg', 10.0)
                
                features = {
                    'driver_encoded': recent.get('driver_encoded', 0),
                    'constructor_encoded': recent.get('constructor_encoded', 0),
                    'circuit_encoded': recent.get('circuit_encoded', 0),
                    'grid': row['grid'], 'quali_pos': row['grid'],
                    'driver_form': driver_form,
                    'constructor_form': recent.get('constructor_form', 10.0),
                    'grid_penalty': 0,
                    'track_experience': recent.get('track_experience', 0),
                    'grid_to_finish_avg': recent.get('grid_to_finish_avg', 0),
                    'recent_position_avg': recent_pos_avg,
                    'constructor_position_std': recent.get('constructor_position_std', 5.0),
                    'quali_grid_delta': 0,
                    'improvement_potential': 20 - row['grid'],
                    'form_momentum': recent.get('form_momentum', 0),
                    'grid_x_form': row['grid'] * driver_form,
                    'grid_x_recent': row['grid'] * recent_pos_avg
                }
            
            enriched_rows.append({**row.to_dict(), **features})
        
        enriched_df = pd.DataFrame(enriched_rows)
        
        for feature in self.features:
            if feature not in enriched_df.columns:
                enriched_df[feature] = 0
        
        return enriched_df

    def predict_belgian_gp(self, simulation_params=None):
        """Predict race results with smart strategy"""
        print("🔮 Generating SMART predictions...")
        
        circuit = simulation_params.get('circuit', 'spa') if simulation_params else 'spa'
        race_df = self.prepare_race_data(circuit)
        
        if simulation_params:
            race_df['rain_probability'] = simulation_params.get('rain_prob', 20)
            race_df['temperature'] = simulation_params.get('air_temp', 20)
            race_df['humidity'] = simulation_params.get('humidity', 60)
        
        race_features = self.extract_features(race_df)
        X_race = race_features[self.features]
        
        predictions = self.model.predict(X_race)
        probabilities = self.model.predict_proba(X_race)
        
        results_df = race_df.copy()
        results_df['predicted_position'] = predictions + 1
        results_df['confidence'] = np.max(probabilities, axis=1)
        results_df['win_probability'] = probabilities[:, 0]
        results_df['podium_probability'] = probabilities[:, :3].sum(axis=1)
        
        if simulation_params:
            results_df = self.apply_strategy_logic(results_df, simulation_params)
            results_df = results_df.sort_values('win_probability', ascending=False)
            results_df['predicted_position'] = range(1, len(results_df) + 1)
        else:
            results_df = results_df.sort_values('predicted_position')
        
        return results_df

    def display_predictions(self, results_df):
        """Display predictions"""
        print("\n" + "="*80)
        print("🏆 RACE PREDICTIONS")
        print("="*80)
        print(f"{'Pos':<4} {'Driver':<20} {'Team':<15} {'Grid':<5} {'Win %':<8} {'Podium %':<10}")
        print("-"*80)
        
        for _, row in results_df.head(10).iterrows():
            print(f"{int(row['predicted_position']):<4} {row['driver_id']:<20} {row['constructor_id']:<15} "
                  f"{int(row['grid']):<5} {row['win_probability']*100:<8.1f} {row['podium_probability']*100:<10.1f}")
        
        print("\n🥇 PODIUM:")
        for i, (_, row) in enumerate(results_df.head(3).iterrows(), 1):
            print(f"{i}. {row['driver_id']} - {row['win_probability']*100:.1f}%")

    def save_predictions(self, results_df):
        """Save predictions"""
        output_df = results_df[['driver_id', 'constructor_id', 'grid', 'predicted_position', 
                               'win_probability', 'podium_probability', 'confidence']].copy()
        output_df.to_csv('race_predictions.csv', index=False)
        print("✅ Saved to CSV")

if __name__ == "__main__":
    predictor = BelgianGPPredictor(
        model_dir='E:/Shivam/F1/f1-ai-predictor/models',
        data_path='E:/Shivam/F1/f1-ai-predictor/data/f1_race_data.csv',
        weather_api_key='87e5ba753df3d9e4f6fc96f167f6a7a6'
    )
    
    if predictor.load_model_and_data():
        results = predictor.predict_belgian_gp()
        predictor.display_predictions(results)
        predictor.save_predictions(results)
        print("\n🎉 Complete!")
    else:
        print("❌ Failed to load")