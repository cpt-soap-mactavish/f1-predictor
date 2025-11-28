"""
OpenF1 Car Data Collector - WORKING VERSION
Key insight: MUST filter by session_key + driver_number
Cannot query all data at once
Storage: E:/Shivam/F1/f1-ai-predictor/data/openf1_car_data/
"""

import requests
import pandas as pd
import os
import time

OUTPUT_DIR = 'E:/Shivam/F1/f1-ai-predictor/data/openf1_car_data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

API = 'https://api.openf1.org/v1'

print("="*80)
print("OpenF1 CAR DATA COLLECTOR - Working Version")
print("="*80)

# Step 1: Get all sessions
print("\n📋 Fetching sessions...")
sessions =pd.DataFrame(requests.get(f'{API}/sessions').json())
print(f"✅ {len(sessions)} sessions found")
print(f"   Years: {sorted(sessions['year'].unique())}")

# Step 2: Filter for Races only
races = sessions[sessions['session_name'] == 'Race'].copy()
print(f"\n🏁 {len(races)} Race sessions to collect")

# Step 3: Get driver numbers from first race as template
print("\n🧪 Testing with first race...")
test_race = races.iloc[0]
session_key = test_race['session_key']

# Find active drivers (test numbers 1-99)
print(f"   Finding drivers in session {session_key}...")
active_drivers = []

for num in range(1, 100):
    r = requests.get(f'{API}/car_data', params={'session_key': session_key, 'driver_number': num}, timeout=5)
    if r.status_code == 200 and len(r.json()) > 0:
        active_drivers.append(num)
        print(f"   ✓ Driver {num}", end=' ', flush=True)
    time.sleep(0.05)

print(f"\n✅ Found {len(active_drivers)} active drivers: {active_drivers}")

# Step 4: Collect all data
print(f"\n📥 Starting collection for {len(races)} races...\n")

total_records = 0
for idx, race in races.iterrows():
    session_key = race['session_key']
    year = race['year']
    meeting = race.get('meeting_official_name', f'Race_{idx}')
    
    print(f"{year} - {meeting} (session {session_key})")
    
    race_data = []
    
    for driver_num in active_drivers:  # Use same drivers as template
        try:
            r = requests.get(
                f'{API}/car_data',
                params={'session_key': session_key, 'driver_number': driver_num},
                timeout=30
            )
            
            if r.status_code == 200:
                data = r.json()
                if len(data) > 0:
                    race_data.extend(data)
                    print(f"  ✓ Driver {driver_num}: {len(data)}", end=' ', flush=True)
            
            time.sleep(0.1)  # Rate limit
            
        except Exception as e:
            print(f"  ✗ D{driver_num}: {str(e)[:20]}", end=' ', flush=True)
    
    # Save race data
    if race_data:
        df = pd.DataFrame(race_data)
        
        year_dir = f'{OUTPUT_DIR}/{year}'
        os.makedirs(year_dir, exist_ok=True)
        
        filename = f'{year_dir}/{meeting.replace(" ", "_")}_session_{session_key}.csv'
        df.to_csv(filename, index=False)
        
        size_mb = len(df) * 100 / 1_000_000  # Rough estimate
        total_records += len(df)
        
        print(f"\n  💾 {len(df):,} records ({size_mb:.1f}MB)")
    else:
        print("\n  ❌ No data")
    
    # Progress
    if (idx + 1) % 5 == 0:
        print(f"\n📊 Progress: {idx+1}/{len(races)} | Total: {total_records:,} records\n")

print("\n" + "="*80)
print(f"✅ COMPLETE! Collected {total_records:,} telemetry records")
print(f"📁 Saved to: {OUTPUT_DIR}")
print("="*80)
