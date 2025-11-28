"""
OpenF1 Comprehensive Data Collector
Uses analyzed sessions CSV to fetch ALL available data properly
Collects: car_data, weather, laps, stints, pit, intervals, overtakes, race_control
Storage: E:/Shivam/F1/f1-ai-predictor/data/openf1_complete/
"""

import pandas as pd
import requests
import os
import time
from datetime import datetime

# E DRIVE STORAGE
BASE_DIR = 'E:/Shivam/F1/f1-ai-predictor/data/openf1_complete'
os.makedirs(BASE_DIR, exist_ok=True)

API = 'https://api.openf1.org/v1'

# Load analyzed sessions
SESSIONS_FILE = 'E:/Shivam/F1/f1-ai-predictor/data/openf1_race_sessions.csv'

print("="*80)
print("OpenF1 COMPREHENSIVE DATA COLLECTOR")
print("="*80)

# Load race sessions
print(f"\n📋 Loading sessions from: {SESSIONS_FILE}")
sessions_df = pd.read_csv(SESSIONS_FILE)

print(f"✅ Loaded {len(sessions_df)} race sessions")
print(f"   Years: {sorted(sessions_df['year'].unique())}")

# Endpoints to collect
ENDPOINTS = {
    'car_data': True,      # Requires driver_number
    'weather': True,       # Session-level
    'laps': True,          # Session-level  
    'stints': True,        # Session-level
    'pit': True,           # Session-level
    'intervals': False,    # Skip for now (large dataset)
    'overtakes': True,     # Session-level (beta)
    'race_control': True,  # Session-level
}

def collect_session_data(session_key, year, meeting_name):
    """Collect all available data for one session"""
    
    print(f"\n{'='*80}")
    print(f"Session {session_key}: {year} - {meeting_name}")
    print(f"{'='*80}")
    
    session_dir = f'{BASE_DIR}/{year}/session_{session_key}_{meeting_name.replace(" ", "_")}'
    os.makedirs(session_dir, exist_ok=True)
    
    collected_data = {}
    
    # 1. Weather (simple session-level data)
    if ENDPOINTS['weather']:
        print("\n🌤️  Weather...", end=' ')
        try:
            r = requests.get(f'{API}/weather', params={'session_key': session_key}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 0:
                    df = pd.DataFrame(data)
                    df.to_csv(f'{session_dir}/weather.csv', index=False)
                    print(f"✅ {len(df)} records")
                    collected_data['weather'] = len(df)
                else:
                    print("❌ No data")
        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}")
    
    # 2. Laps
    if ENDPOINTS['laps']:
        print("⏱️  Laps...", end=' ')
        try:
            r = requests.get(f'{API}/laps', params={'session_key': session_key}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 0:
                    df = pd.DataFrame(data)
                    df.to_csv(f'{session_dir}/laps.csv', index=False)
                    print(f"✅ {len(df)} records")
                    collected_data['laps'] = len(df)
                else:
                    print("❌ No data")
        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}")
    
    # 3. Stints
    if ENDPOINTS['stints']:
        print("🛞 Stints...", end=' ')
        try:
            r = requests.get(f'{API}/stints', params={'session_key': session_key}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 0:
                    df = pd.DataFrame(data)
                    df.to_csv(f'{session_dir}/stints.csv', index=False)
                    print(f"✅ {len(df)} records")
                    collected_data['stints'] = len(df)
                else:
                    print("❌ No data")
        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}")
    
    # 4. Pit stops
    if ENDPOINTS['pit']:
        print("🔧 Pit stops...", end=' ')
        try:
            r = requests.get(f'{API}/pit', params={'session_key': session_key}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 0:
                    df = pd.DataFrame(data)
                    df.to_csv(f'{session_dir}/pit.csv', index=False)
                    print(f"✅ {len(df)} records")
                    collected_data['pit'] = len(df)
                else:
                    print("❌ No data")
        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}")
    
    # 5. Race control (safety cars, flags, etc.)
    if ENDPOINTS['race_control']:
        print("🚨 Race control...", end=' ')
        try:
            r = requests.get(f'{API}/race_control', params={'session_key': session_key}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 0:
                    df = pd.DataFrame(data)
                    df.to_csv(f'{session_dir}/race_control.csv', index=False)
                    print(f"✅ {len(df)} records")
                    collected_data['race_control'] = len(df)
                else:
                    print("❌ No data")
        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}")
    
    # 6. Overtakes (beta)
    if ENDPOINTS['overtakes']:
        print("🏁 Overtakes...", end=' ')
        try:
            r = requests.get(f'{API}/overtakes', params={'session_key': session_key}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 0:
                    df = pd.DataFrame(data)
                    df.to_csv(f'{session_dir}/overtakes.csv', index=False)
                    print(f"✅ {len(df)} records")
                    collected_data['overtakes'] = len(df)
                else:
                    print("❌ No data")
        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}")
    
    # 7. Car data (requires driver numbers - collect sample)
    if ENDPOINTS['car_data']:
        print("\n🏎️  Car data (sampling drivers)...", end=' ')
        
        # Test first 10 driver numbers as sample (full collect would take too long)
        test_drivers = [1, 4, 11, 16, 44, 55, 63, 77, 81, 99]
        car_data_all = []
        
        for driver_num in test_drivers:
            try:
                r = requests.get(
                    f'{API}/car_data',
                    params={'session_key': session_key, 'driver_number': driver_num},
                    timeout=10
                )
                
                if r.status_code == 200:
                    data = r.json()
                    if len(data) > 0:
                        car_data_all.extend(data)
                
                time.sleep(0.05)  # Rate limit
            except:
                continue
        
        if len(car_data_all) > 0:
            df = pd.DataFrame(car_data_all)
            df.to_csv(f'{session_dir}/car_data_sample.csv', index=False)
            print(f"✅ {len(df)} records (sample)")
            collected_data['car_data'] = len(df)
        else:
            print("❌ No data")
    
    # Summary
    if collected_data:
        print(f"\n📊 Collected {len(collected_data)} datasets for this session")
        print(f"   Total records: {sum(collected_data.values())}")
        print(f"   Saved to: {session_dir}")
    else:
        print(f"\n❌ No data collected for this session")
    
    return collected_data

# Main collection loop
print(f"\n🚀 Starting collection for {len(sessions_df)} races...\n")

total_stats = {endpoint: 0 for endpoint in ENDPOINTS if ENDPOINTS[endpoint]}
successful_sessions = 0

for idx, row in sessions_df.iterrows():
    session_key = row['session_key']
    year = row['year']
    meeting = row.get('meeting_official_name', f'Race_{idx}')
    
    try:
        session_data = collect_session_data(session_key, year, meeting)
        
        if session_data:
            successful_sessions += 1
            for key, value in session_data.items():
                total_stats[key] += value
        
        # Progress every 5 sessions
        if (idx + 1) % 5 == 0:
            print(f"\n{'='*80}")
            print(f"📊 Progress: {idx+1}/{len(sessions_df)} sessions")
            print(f"   Successful: {successful_sessions}")
            print(f"   Total records: {sum(total_stats.values())}")
            print(f"{'='*80}\n")
        
        time.sleep(0.5)  # Rate limiting between sessions
        
    except Exception as e:
        print(f"\n❌ Session {session_key} error: {str(e)[:50]}")

# Final summary
print("\n" + "="*80)
print("✅ COLLECTION COMPLETE!")
print("="*80)
print(f"\nSuccessful sessions: {successful_sessions}/{len(sessions_df)}")
print(f"\nData collected by type:")
for endpoint, count in total_stats.items():
    if count > 0:
        print(f"  {endpoint:15s}: {count:,} records")

print(f"\nAll data saved to: {BASE_DIR}")
print("="*80)
