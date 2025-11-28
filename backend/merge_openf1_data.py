"""
OpenF1 Data Integration & Feature Extraction
Merges collected OpenF1 data with historical race dataset
Extracts prediction features from all endpoints
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

# Paths
OPENF1_DIR = 'E:/Shivam/F1/f1-ai-predictor/data/openf1_final'
HISTORICAL_DATA = 'E:/Shivam/F1/f1-ai-predictor/data/f1_race_data_prepared.csv'
OUTPUT_FILE = 'E:/Shivam/F1/f1-ai-predictor/data/f1_race_data_with_openf1.csv'

print("="*80)
print("OpenF1 DATA INTEGRATION & FEATURE EXTRACTION")
print("="*80)

# Load historical data
print("\n📁 Loading historical data...")
historical_df = pd.read_csv(HISTORICAL_DATA)
print(f"✅ Loaded {len(historical_df)} historical race records")
print(f"   Columns: {len(historical_df.columns)}")

# Find all OpenF1 sessions
print("\n📋 Finding OpenF1 sessions...")
openf1_sessions = []

for year in ['2023', '2024', '2025']:
    year_path = os.path.join(OPENF1_DIR, year)
    if os.path.exists(year_path):
        for session_dir in os.listdir(year_path):
            if session_dir.startswith('session_'):
                session_key = int(session_dir.split('_')[1])
                session_path = os.path.join(year_path, session_dir)
                openf1_sessions.append({
                    'session_key': session_key,
                    'year': int(year),
                    'path': session_path
                })

print(f"✅ Found {len(openf1_sessions)} OpenF1 sessions")

def extract_features_from_session(session_path):
    """Extract prediction features from one OpenF1 session"""
    
    features = {}
    
    # 1. LAPS - Pace analysis
    laps_file = os.path.join(session_path, 'laps.csv')
    if os.path.exists(laps_file):
        laps = pd.read_csv(laps_file)
        
        # Average lap time per driver (convert to numeric, handle errors)
        if 'driver_number' in laps.columns and 'lap_duration' in laps.columns:
            laps['lap_duration_numeric'] = pd.to_numeric(laps['lap_duration'], errors='coerce')
            avg_pace = laps.groupby('driver_number')['lap_duration_numeric'].mean()
            features['avg_lap_time'] = avg_pace.to_dict()
            
            # Pace consistency (std deviation)
            pace_std = laps.groupby('driver_number')['lap_duration_numeric'].std()
            features['pace_consistency'] = pace_std.to_dict()
    
    # 2. INTERVALS - Gap analysis
    intervals_file = os.path.join(session_path, 'intervals.csv')
    if os.path.exists(intervals_file):
        intervals = pd.read_csv(intervals_file)
        
        if 'driver_number' in intervals.columns and 'gap_to_leader' in intervals.columns:
            # Convert gap_to_leader to numeric (handles "+1 LAP" strings)
            intervals['gap_numeric'] = pd.to_numeric(intervals['gap_to_leader'], errors='coerce')
            
            # Average gap to leader
            avg_gap = intervals.groupby('driver_number')['gap_numeric'].mean()
            features['avg_gap_to_leader'] = avg_gap.to_dict()
            
            # Catching up? (negative trend = getting closer)
            gap_trend = intervals.groupby('driver_number')['gap_numeric'].apply(
                lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 and not x.isna().all() else 0
            )
            features['gap_trend'] = gap_trend.to_dict()
    
    # 3. STINTS - Tire strategy
    stints_file = os.path.join(session_path, 'stints.csv')
    if os.path.exists(stints_file):
        stints = pd.read_csv(stints_file)
        
        if 'driver_number' in stints.columns:
            # Number of pit stops
            pit_stops = stints.groupby('driver_number').size() - 1  # -1 because first stint isn't a stop
            features['num_pit_stops'] = pit_stops.to_dict()
            
            # Tire compounds used
            if 'compound' in stints.columns:
                compounds_used = stints.groupby('driver_number')['compound'].apply(list)
                features['tire_compounds'] = compounds_used.to_dict()
    
    # 4. OVERTAKES - Aggression score
    overtakes_file = os.path.join(session_path, 'overtakes.csv')
    if os.path.exists(overtakes_file):
        overtakes = pd.read_csv(overtakes_file)
        
        if 'driver_number' in overtakes.columns:
            # Overtakes made
            overtakes_made = overtakes.groupby('driver_number').size()
            features['overtakes_made'] = overtakes_made.to_dict()
    
    # 5. POSITION - Position changes
    position_file = os.path.join(session_path, 'position.csv')
    if os.path.exists(position_file):
        positions = pd.read_csv(position_file)
        
        if 'driver_number' in positions.columns and 'position' in positions.columns:
            # Position gained (start vs finish)
            for driver in positions['driver_number'].unique():
                driver_positions = positions[positions['driver_number'] == driver]['position']
                if len(driver_positions) > 1:
                    if 'positions_gained' not in features:
                        features['positions_gained'] = {}
                    features['positions_gained'][driver] = driver_positions.iloc[0] - driver_positions.iloc[-1]
    
    # 6. TEAM RADIO - Issue detection
    radio_file = os.path.join(session_path, 'team_radio.csv')
    if os.path.exists(radio_file):
        radio = pd.read_csv(radio_file)
        
        if 'driver_number' in radio.columns:
            # Count of radio messages (more = more issues?)
            radio_count = radio.groupby('driver_number').size()
            features['radio_messages'] = radio_count.to_dict()
    
    # 7. RACE CONTROL - Safety car laps
    race_control_file = os.path.join(session_path, 'race_control.csv')
    if os.path.exists(race_control_file):
        race_control = pd.read_csv(race_control_file)
        
        if 'category' in race_control.columns:
            # Count safety car periods
            safety_cars = race_control[race_control['category'].str.contains('SafetyCar', case=False, na=False)]
            features['safety_car_count'] = len(safety_cars)
    
    # 8. WEATHER
    weather_file = os.path.join(session_path, 'weather.csv')
    if os.path.exists(weather_file):
        weather = pd.read_csv(weather_file)
        
        if len(weather) > 0:
            # Average weather conditions
            if 'air_temperature' in weather.columns:
                features['air_temp'] = weather['air_temperature'].mean()
            if 'track_temperature' in weather.columns:
                features['track_temp'] = weather['track_temperature'].mean()
            if 'rainfall' in weather.columns:
                features['rainfall'] = weather['rainfall'].any()
    
    return features

# Extract features from all sessions
print("\n🔧 Extracting features from OpenF1 sessions...")

all_features = []
for idx, session in enumerate(openf1_sessions):
    print(f"   Processing session {session['session_key']} ({session['year']})...", end=' ')
    
    try:
        features = extract_features_from_session(session['path'])
        features['session_key'] = session['session_key']
        features['year'] = session['year']
        all_features.append(features)
        print("✅")
    except Exception as e:
        print(f"❌ {str(e)[:50]}")
    
    if (idx + 1) % 10 == 0:
        print(f"   Progress: {idx+1}/{len(openf1_sessions)}")

print(f"\n✅ Extracted features from {len(all_features)} sessions")

# Convert to DataFrame
print("\n📊 Creating features DataFrame...")
features_df = pd.DataFrame(all_features)
print(f"✅ Features DataFrame: {len(features_df)} rows × {len(features_df.columns)} columns")

# Save intermediate features
features_output = 'E:/Shivam/F1/f1-ai-predictor/data/openf1_features.csv'
features_df.to_csv(features_output, index=False)
print(f"💾 Saved features to: {features_output}")

print("\n" + "="*80)
print("✅ FEATURE EXTRACTION COMPLETE!")
print("="*80)
print(f"\nNext step: Merge with historical data ({HISTORICAL_DATA})")
print(f"Output will be: {OUTPUT_FILE}")
print("="*80)
