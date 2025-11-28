"""
Historical Weather Data Collection for F1 Races (2010-2025)
Uses OpenWeather Historical API to get actual race day weather conditions
"""

import pandas as pd
import requests
import time
from datetime import datetime
import json

# OpenWeather API Key
WEATHER_API_KEY = '87e5ba753df3d9e4f6fc96f167f6a7a6'

# Circuit GPS Coordinates
CIRCUIT_COORDS = {
    'albert_park': (-37.8497, 144.9680),
    'americas': (30.1328, -97.6411),
    'bahrain': (26.0325, 50.5106),
    'baku': (40.3725, 49.8533),
    'catalunya': (41.5700, 2.2611),
    'hungaroring': (47.5789, 19.2486),
    'imola': (44.3439, 11.7167),
    'interlagos': (-23.7036, -46.6997),
    'jeddah': (21.6319, 39.1044),
    'losail': (25.4900, 51.4542),
    'marina_bay': (1.2914, 103.8644),
    'miami': (25.9581, -80.2389),
    'monaco': (43.7347, 7.4206),
    'monza': (45.6156, 9.2811),
    'red_bull_ring': (47.2197, 14.7647),
    'ricard': (43.2506, 5.7919),
    'rodriguez': (19.4042, -99.0907),
    'shanghai': (31.3389, 121.2197),
    'silverstone': (52.0786, -1.0169),
    'sochi': (43.4057, 39.9578),
    'spa': (50.4372, 5.9714),
    'suzuka': (34.8431, 136.5408),
    'vegas': (36.1147, -115.1728),
    'villeneuve': (45.5042, -73.5278),
    'yas_marina': (24.4672, 54.6031),
    'zandvoort': (52.3888, 4.5409),
    # Alternate names
    'albert_park_circuit': (-37.8497, 144.9680),
    'circuit_gilles_villeneuve': (45.5042, -73.5278),
    'circuit_de_barcelona-catalunya': (41.5700, 2.2611),
    'circuit_de_spa-francorchamps': (50.4372, 5.9714),
    'autodromo_nazionale_di_monza': (45.6156, 9.2811),
    'marina_bay_street_circuit': (1.2914, 103.8644),
    'yas_marina_circuit': (24.4672, 54.6031),
}

def get_historical_weather(lat, lon, date_str):
    """
    Fetch historical weather for a specific location and date
    Using OpenWeather History API (free tier: 1000 calls/day)
    """
    # Convert date string to timestamp
    try:
        race_date = datetime.strptime(date_str, '%Y-%m-%d')
        timestamp = int(race_date.timestamp())
        
        # OpenWeather Historical API endpoint
        url = f"http://api.openweathermap.org/data/2.5/onecall/timemachine"
        params = {
            'lat': lat,
            'lon': lon,
            'dt': timestamp,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            hourly = data.get('hourly', [{}])[0]  # Get first hour (race typically starts around 14:00)
            
            return {
                'temperature': hourly.get('temp', None),
                'humidity': hourly.get('humidity', None),
                'weather_condition': hourly.get('weather', [{}])[0].get('main', 'Unknown'),
                'weather_description': hourly.get('weather', [{}])[0].get('description', ''),
                'rain': hourly.get('rain', {}).get('1h', 0),  # Rain in last hour (mm)
                'clouds': hourly.get('clouds', 0)
            }
        else:
            print(f"   ⚠️  API Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def collect_weather_data(input_csv='../data/f1_race_data.csv', output_csv='../data/race_weather.csv'):
    """
    Collect weather data for all unique races in the database
    """
    print("🌤️  Starting Historical Weather Data Collection...")
    print("=" * 80)
    
    # Load race data
    df = pd.read_csv(input_csv)
    
    # Filter for 2010+ only (modern era with better data)
    df = df[df['season'] >= 2010].copy()
    
    # Get unique races (season + round + circuit)
    unique_races = df.groupby(['season', 'round', 'circuit_id', 'date']).size().reset_index()[['season', 'round', 'circuit_id', 'date']]
    
    print(f"📊 Found {len(unique_races)} unique races (2010-2025)")
    print(f"🔑 Using API key: ...{WEATHER_API_KEY[-8:]}")
    print()
    
    # Collect weather data
    weather_records = []
    success_count = 0
    failed_count = 0
    
    for idx, race in unique_races.iterrows():
        season = race['season']
        round_num = race['round']
        circuit = race['circuit_id']
        date = race['date']
        
        # Get circuit coordinates
        coords = CIRCUIT_COORDS.get(circuit)
        if not coords:
            print(f"⚠️  {season} R{round_num:02d} {circuit:20s} - No coordinates available")
            failed_count += 1
            continue
        
        lat, lon = coords
        
        print(f"🔍 {season} R{round_num:02d} {circuit:20s} ({date}) ", end='')
        
        # Fetch weather
        weather = get_historical_weather(lat, lon, date)
        
        if weather:
            weather_records.append({
                'season': season,
                'round': round_num,
                'circuit_id': circuit,
                'date': date,
                'air_temp': weather['temperature'],
                'humidity': weather['humidity'],
                'weather_condition': weather['weather_condition'],
                'weather_description': weather['weather_description'],
                'rain_mm': weather['rain'],
                'clouds_percent': weather['clouds']
            })
            
            # Determine if wet race
            is_wet = weather['rain'] > 0 or weather['weather_condition'] in ['Rain', 'Drizzle', 'Thunderstorm']
            condition_emoji = '🌧️' if is_wet else '☀️'
            
            print(f"{condition_emoji} {weather['temperature']:.1f}°C, {weather['weather_description']}")
            success_count += 1
        else:
            print(f"❌ Failed")
            failed_count += 1
        
        # Rate limiting (1000 calls/day = ~40 calls/hour)
        time.sleep(0.5)  # Wait 0.5 seconds between requests
        
        # Save progress every 50 races
        if (idx + 1) % 50 == 0:
            temp_df = pd.DataFrame(weather_records)
            temp_df.to_csv(output_csv.replace('.csv', '_temp.csv'), index=False)
            print(f"\n💾 Progress saved: {len(weather_records)} races collected\n")
    
    # Save final results
    weather_df = pd.DataFrame(weather_records)
    weather_df.to_csv(output_csv, index=False)
    
    print()
    print("=" * 80)
    print(f"✅ Weather data collection complete!")
    print(f"   Success: {success_count}/{len(unique_races)} races")
    print(f"   Failed:  {failed_count}/{len(unique_races)} races")
    print(f"   Saved to: {output_csv}")
    
    # Summary statistics
    print("\n📈 Weather Summary:")
    print(f"   Average temperature: {weather_df['air_temp'].mean():.1f}°C")
    print(f"   Wet races: {(weather_df['rain_mm'] > 0).sum()} ({(weather_df['rain_mm'] > 0).sum()/len(weather_df)*100:.1f}%)")
    print(f"   Dry races: {(weather_df['rain_mm'] == 0).sum()} ({(weather_df['rain_mm'] == 0).sum()/len(weather_df)*100:.1f}%)")
    
    return weather_df

if __name__ == "__main__":
    # Collect weather data
    weather_df = collect_weather_data()
    
    print("\n🎉 Complete! Next steps:")
    print("   1. Merge race_weather.csv with f1_race_data_prepared.csv")
    print("   2. Retrain model with weather features")
    print("   3. Update predictor to use real weather data")
