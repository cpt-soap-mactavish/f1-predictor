"""
OpenF1 FINAL COMPREHENSIVE COLLECTOR
Collects ALL endpoints for complete dataset:
- car_data (full telemetry for all drivers)
- drivers (metadata)
- intervals (timing gaps)
- location (GPS tracking)
- laps (lap times)
- stints (tire strategy)
- pit (pit stops)
- position (race positions)
- team_radio (communications)
- weather (conditions)
- overtakes (passes)
- race_control (safety cars, flags)

Storage: E:/Shivam/F1/f1-ai-predictor/data/openf1_final/
"""

import pandas as pd
import requests
import os
import time

BASE_DIR = 'E:/Shivam/F1/f1-ai-predictor/data/openf1_final'
os.makedirs(BASE_DIR, exist_ok=True)

API = 'https://api.openf1.org/v1'

# Load sessions
SESSIONS_FILE = 'E:/Shivam/F1/f1-ai-predictor/data/openf1_race_sessions.csv'

print("="*80)
print("OpenF1 FINAL COMPREHENSIVE DATA COLLECTOR")
print("="*80)
print("\nCollecting ALL endpoints:")
print("  ✓ car_data (FULL - all drivers)")
print("  ✓ drivers")
print("  ✓ intervals")
print("  ✓ location (GPS)")
print("  ✓ laps")
print("  ✓ stints")
print("  ✓ pit")
print("  ✓ position")
print("  ✓ team_radio")
print("  ✓ weather")
print("  ✓ overtakes")
print("  ✓ race_control")
print("="*80)

sessions_df = pd.read_csv(SESSIONS_FILE)
print(f"\n📋 {len(sessions_df)} race sessions to process")

def find_active_drivers(session_key):
    """Find all drivers with data in this session"""
    drivers = []
    for num in range(1, 100):
        try:
            r = requests.get(f'{API}/car_data', 
                           params={'session_key': session_key, 'driver_number': num}, 
                           timeout=3)
            if r.status_code == 200 and len(r.json()) > 0:
                drivers.append(num)
            time.sleep(0.02)
        except:
            continue
    return drivers

def collect_all_data(session_key, year, meeting_name):
    """Collect complete dataset for one session"""
    
    print(f"\n{'='*80}")
    print(f"📍 {year} - {meeting_name} (Session {session_key})")
    print(f"{'='*80}")
    
    session_dir = f'{BASE_DIR}/{year}/session_{session_key}'
    os.makedirs(session_dir, exist_ok=True)
    
    stats = {}
    
    # 1. DRIVERS
    print("👤 Drivers...", end=' ', flush=True)
    try:
        r = requests.get(f'{API}/drivers', params={'session_key': session_key}, timeout=10)
        if r.status_code == 200 and len(r.json()) > 0:
            pd.DataFrame(r.json()).to_csv(f'{session_dir}/drivers.csv', index=False)
            stats['drivers'] = len(r.json())
            print(f"✅ {stats['drivers']}")
        else:
            print("❌")
    except Exception as e:
        print(f"❌ {str(e)[:20]}")
    
    # 2. WEATHER
    print("🌤️  Weather...", end=' ', flush=True)
    try:
        r = requests.get(f'{API}/weather', params={'session_key': session_key}, timeout=10)
        if r.status_code == 200 and len(r.json()) > 0:
            pd.DataFrame(r.json()).to_csv(f'{session_dir}/weather.csv', index=False)
            stats['weather'] = len(r.json())
            print(f"✅ {stats['weather']}")
        else:
            print("❌")
    except Exception as e:
        print(f"❌ {str(e)[:20]}")
    
    # 3. LAPS
    print("⏱️  Laps...", end=' ', flush=True)
    try:
        r = requests.get(f'{API}/laps', params={'session_key': session_key}, timeout=10)
        if r.status_code == 200 and len(r.json()) > 0:
            pd.DataFrame(r.json()).to_csv(f'{session_dir}/laps.csv', index=False)
            stats['laps'] = len(r.json())
            print(f"✅ {stats['laps']}")
        else:
            print("❌")
    except Exception as e:
        print(f"❌ {str(e)[:20]}")
    
    # 4. STINTS
    print("🛞 Stints...", end=' ', flush=True)
    try:
        r = requests.get(f'{API}/stints', params={'session_key': session_key}, timeout=10)
        if r.status_code == 200 and len(r.json()) > 0:
            pd.DataFrame(r.json()).to_csv(f'{session_dir}/stints.csv', index=False)
            stats['stints'] = len(r.json())
            print(f"✅ {stats['stints']}")
        else:
            print("❌")
    except Exception as e:
        print(f"❌ {str(e)[:20]}")
    
    # 5. PIT STOPS
    print("🔧 Pit...", end=' ', flush=True)
    try:
        r = requests.get(f'{API}/pit', params={'session_key': session_key}, timeout=10)
        if r.status_code == 200 and len(r.json()) > 0:
            pd.DataFrame(r.json()).to_csv(f'{session_dir}/pit.csv', index=False)
            stats['pit'] = len(r.json())
            print(f"✅ {stats['pit']}")
        else:
            print("❌")
    except Exception as e:
        print(f"❌ {str(e)[:20]}")
    
    # 6. OVERTAKES
    print("🏁 Overtakes...", end=' ', flush=True)
    try:
        r = requests.get(f'{API}/overtakes', params={'session_key': session_key}, timeout=10)
        if r.status_code == 200 and len(r.json()) > 0:
            pd.DataFrame(r.json()).to_csv(f'{session_dir}/overtakes.csv', index=False)
            stats['overtakes'] = len(r.json())
            print(f"✅ {stats['overtakes']}")
        else:
            print("❌")
    except Exception as e:
        print(f"❌ {str(e)[:20]}")
    
    # 7. RACE CONTROL
    print("🚨 Race Control...", end=' ', flush=True)
    try:
        r = requests.get(f'{API}/race_control', params={'session_key': session_key}, timeout=10)
        if r.status_code == 200 and len(r.json()) > 0:
            pd.DataFrame(r.json()).to_csv(f'{session_dir}/race_control.csv', index=False)
            stats['race_control'] = len(r.json())
            print(f"✅ {stats['race_control']}")
        else:
            print("❌")
    except Exception as e:
        print(f"❌ {str(e)[:20]}")
    
    # 8. INTERVALS
    print("⏳ Intervals...", end=' ', flush=True)
    try:
        r = requests.get(f'{API}/intervals', params={'session_key': session_key}, timeout=30)
        if r.status_code == 200 and len(r.json()) > 0:
            pd.DataFrame(r.json()).to_csv(f'{session_dir}/intervals.csv', index=False)
            stats['intervals'] = len(r.json())
            print(f"✅ {stats['intervals']}")
        else:
            print("❌")
    except Exception as e:
        print(f"❌ {str(e)[:20]}")
    
    # 9. POSITION
    print("📊 Position...", end=' ', flush=True)
    try:
        r = requests.get(f'{API}/position', params={'session_key': session_key}, timeout=30)
        if r.status_code == 200 and len(r.json()) > 0:
            pd.DataFrame(r.json()).to_csv(f'{session_dir}/position.csv', index=False)
            stats['position'] = len(r.json())
            print(f"✅ {stats['position']}")
        else:
            print("❌")
    except Exception as e:
        print(f"❌ {str(e)[:20]}")
    
    # 10. TEAM RADIO
    print("📻 Team Radio...", end=' ', flush=True)
    try:
        r = requests.get(f'{API}/team_radio', params={'session_key': session_key}, timeout=10)
        if r.status_code == 200 and len(r.json()) > 0:
            pd.DataFrame(r.json()).to_csv(f'{session_dir}/team_radio.csv', index=False)
            stats['team_radio'] = len(r.json())
            print(f"✅ {stats['team_radio']}")
        else:
            print("❌")
    except Exception as e:
        print(f"❌ {str(e)[:20]}")
    
    # 11. CAR DATA (FULL - all drivers)
    print("\n🏎️  Car Data (FULL)...")
    drivers = find_active_drivers(session_key)
    print(f"   Found {len(drivers)} drivers")
    
    all_car_data = []
    for driver_num in drivers:
        try:
            r = requests.get(f'{API}/car_data',
                           params={'session_key': session_key, 'driver_number': driver_num},
                           timeout=30)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 0:
                    all_car_data.extend(data)
                    print(f"   ✓ Driver {driver_num}: {len(data):,}", flush=True)
            time.sleep(0.1)
        except Exception as e:
            print(f"   ✗ Driver {driver_num}: {str(e)[:20]}", flush=True)
    
    if all_car_data:
        pd.DataFrame(all_car_data).to_csv(f'{session_dir}/car_data.csv', index=False)
        stats['car_data'] = len(all_car_data)
        print(f"   ✅ Total: {stats['car_data']:,} records")
    
    # 12. LOCATION (GPS - all drivers)
    print("\n📍 Location (GPS)...")
    all_location_data = []
    for driver_num in drivers:
        try:
            r = requests.get(f'{API}/location',
                           params={'session_key': session_key, 'driver_number': driver_num},
                           timeout=30)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 0:
                    all_location_data.extend(data)
                    print(f"   ✓ Driver {driver_num}: {len(data):,}", flush=True)
            time.sleep(0.1)
        except Exception as e:
            print(f"   ✗ Driver {driver_num}: {str(e)[:20]}", flush=True)
    
    if all_location_data:
        pd.DataFrame(all_location_data).to_csv(f'{session_dir}/location.csv', index=False)
        stats['location'] = len(all_location_data)
        print(f"   ✅ Total: {stats['location']:,} records")
    
    # Summary
    print(f"\n📊 Session Complete:")
    print(f"   Datasets: {len(stats)}/12")
    print(f"   Total Records: {sum(stats.values()):,}")
    
    return stats

# Main collection
print(f"\n🚀 Starting FINAL collection...\n")

total_stats = {}
successful = 0

for idx, row in sessions_df.iterrows():
    session_key = row['session_key']
    year = row['year']
    meeting = row.get('meeting_official_name', f'Race_{idx}')
    
    try:
        session_stats = collect_all_data(session_key, year, meeting)
        
        if session_stats:
            successful += 1
            for key, value in session_stats.items():
                total_stats[key] = total_stats.get(key, 0) + value
        
        # Progress
        if (idx + 1) % 5 == 0:
            print(f"\n{'='*80}")
            print(f"📊 PROGRESS: {idx+1}/{len(sessions_df)} sessions")
            print(f"   Successful: {successful}")
            print(f"   Total Records: {sum(total_stats.values()):,}")
            print(f"{'='*80}\n")
        
        time.sleep(1)  # Rate limiting
        
    except Exception as e:
        print(f"\n❌ Session {session_key} failed: {str(e)[:50]}")

# Final summary
print("\n" + "="*80)
print("🎉 FINAL COLLECTION COMPLETE!")
print("="*80)
print(f"\nSessions: {successful}/{len(sessions_df)}")
print(f"\nData by endpoint:")
for endpoint, count in sorted(total_stats.items()):
    print(f"  {endpoint:15s}: {count:>12,} records")

print(f"\nGRAND TOTAL: {sum(total_stats.values()):,} data points")
print(f"Saved to: {BASE_DIR}")
print("="*80)
