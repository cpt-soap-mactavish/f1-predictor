"""
Collect F1 Historical Data using OpenF1 API
Official F1 live timing data API - FREE and comprehensive
Coverage: 2023-2024 (full data)
API Docs: https://openf1.org/
"""

import requests
import pandas as pd
import time
from datetime import datetime
import json

OPENF1_API_BASE = "https://api.openf1.org/v1"

def get_sessions(year=2024):
    """Get all sessions for a given year"""
    url = f"{OPENF1_API_BASE}/sessions"
    params = {'year': year}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return []

def get_weather_for_session(session_key):
    """Get weather data for a specific session"""
    url = f"{OPENF1_API_BASE}/weather"
    params = {'session_key': session_key}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            # Get average conditions during race
            df = pd.DataFrame(data)
            return {
                'air_temp': df['air_temperature'].mean(),
                'track_temp': df['track_temperature'].mean(),
                'humidity': df['humidity'].mean(),
                'rainfall': df['rainfall'].any() if 'rainfall' in df.columns else False,
                'wind_speed': df['wind_speed'].mean() if 'wind_speed' in df.columns else None
            }
    return None

def get_stints_for_session(session_key):
    """Get tire stint data for a session"""
    url = f"{OPENF1_API_BASE}/stints"
    params = {'session_key': session_key}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            df = pd.DataFrame(data)
            # Get most common starting tire (lap 1)
            starting_stints = df[df['lap_start'] <= 2]
            if len(starting_stints) > 0:
                compound_counts = starting_stints['compound'].value_counts()
                return compound_counts.index[0] if len(compound_counts) > 0 else 'UNKNOWN'
    return 'UNKNOWN'

def collect_openf1_data(years=[2023, 2024]):
    """
    Collect race data using OpenF1 API
    """
    print("🏎️  Collecting F1 Data from OpenF1 API")
    print("=" * 80)
    
    all_race_data = []
    
    for year in years:
        print(f"\n📅 Season {year}")
        print("-" * 80)
        
        # Get all sessions for the year
        sessions = get_sessions(year)
        
        # Filter for race sessions only
        race_sessions = [s for s in sessions if s.get('session_name') == 'Race']
        
        print(f"   Found {len(race_sessions)} races")
        
        for session in race_sessions:
            session_key = session['session_key']
            meeting_name = session.get('meeting_official_name', 'Unknown')
            location = session.get('location', 'Unknown')
            date = session.get('date_start', '')[:10]
            
            print(f"   📍 {meeting_name:40s} ", end='')
            
            # Get weather
            weather = get_weather_for_session(session_key)
            
            # Get tire data
            start_tire = get_stints_for_session(session_key)
            
            if weather:
                race_info = {
                    'season': year,
                    'race_name': meeting_name,
                    'location': location,
                    'date': date,
                    'session_key': session_key,
                    
                    # Weather
                    'air_temp': weather['air_temp'],
                    'track_temp': weather['track_temp'],
                    'humidity': weather['humidity'],
                    'rainfall': weather['rainfall'],
                    'wind_speed': weather['wind_speed'],
                    'weather_condition': 'Wet' if weather['rainfall'] else 'Dry',
                    
                    # Strategy
                    'common_start_tire': start_tire,
                    
                    # Meta
                    'data_source': 'OpenF1'
                }
                
                all_race_data.append(race_info)
                
                # Display
                weather_icon = '🌧️' if weather['rainfall'] else '☀️'
                print(f"{weather_icon} {weather['air_temp']:.1f}°C | {start_tire:6s}")
            else:
                print("❌ No weather data")
            
            # Rate limiting
            time.sleep(0.2)
    
    df = pd.DataFrame(all_race_data)
    
    print("\n" + "=" * 80)
    print(f"✅ Data collection complete!")
    print(f"   Total races: {len(df)}")
    print(f"   Wet races: {df['rainfall'].sum()} ({df['rainfall'].sum()/len(df)*100:.1f}%)")
    
    return df

def save_data(df, output_path='../data/f1_openf1_data.csv'):
    """Save collected data"""
    df.to_csv(output_path, index=False)
    print(f"\n💾 Saved to: {output_path}")
    
    print("\n📊 Data Summary:")
    print(f"   Seasons: {df['season'].min()}-{df['season'].max()}")
    print(f"   Races: {len(df)}")
    print(f"   Avg Air Temp: {df['air_temp'].mean():.1f}°C")
    print(f"   Avg Track Temp: {df['track_temp'].mean():.1f}°C")
    print(f"   Avg Humidity: {df['humidity'].mean():.1f}%")
    print(f"\n   Tire Distribution:")
    print(df['common_start_tire'].value_counts())
    
    return output_path

if __name__ == "__main__":
    print("🚀 Starting F1 Data Collection with OpenF1 API...")
    print("   Coverage: 2023-2024 (OpenF1 has complete data)\n")
    
    # Collect data
    df = collect_openf1_data(years=[2023, 2024])
    
    # Save
    output_file = save_data(df)
    
    print(f"\n🎉 Complete!")
    print(f"\n📝 Note: OpenF1 has data from 2023 onwards.")
    print(f"   For 2010-2022, we'll use Ergast API or manual sources.")
