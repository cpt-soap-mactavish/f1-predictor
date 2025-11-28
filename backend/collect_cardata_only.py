"""
OpenF1 Car Data Collector - Focused & Fast
Collects ONLY car_data (telemetry) for sessions that already have other data
Uses existing session directories to avoid re-checking everything
"""

import pandas as pd
import requests
import os
import time

BASE_DIR = 'E:/Shivam/F1/f1-ai-predictor/data/openf1_final'
API = 'https://api.openf1.org/v1'

print("="*80)
print("OpenF1 CAR DATA COLLECTOR (Focused)")
print("="*80)

# Find all existing sessions (where we already collected other data)
existing_sessions = []

for year in ['2023', '2024', '2025']:
    year_path = os.path.join(BASE_DIR, year)
    if os.path.exists(year_path):
        for session_dir in os.listdir(year_path):
            if session_dir.startswith('session_'):
                session_key = session_dir.split('_')[1]
                existing_sessions.append({
                    'session_key': int(session_key),
                    'year': year,
                    'path': os.path.join(year_path, session_dir)
                })

print(f"\n📋 Found {len(existing_sessions)} existing sessions")
print("   Will collect car_data for each\n")

def find_drivers_fast(session_key):
    """Quick driver search using common numbers first"""
    # Common F1 driver numbers
    common_numbers = [1, 2, 4, 10, 11, 14, 16, 18, 20, 22, 23, 24, 27, 31, 40, 44, 55, 63, 77, 81]
    
    drivers = []
    for num in common_numbers:
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

total_records = 0
successful = 0

for idx, session in enumerate(existing_sessions):
    session_key = session['session_key']
    year = session['year']
    session_path = session['path']
    
    # Skip if car_data already exists
    if os.path.exists(os.path.join(session_path, 'car_data.csv')):
        print(f"⏭️  Session {session_key} already has car_data")
        continue
    
    print(f"\n🏎️  Session {session_key} ({year})")
    
    # Find drivers
    print("   Finding drivers...", end=' ', flush=True)
    drivers = find_drivers_fast(session_key)
    
    if not drivers:
        print("❌ No drivers found")
        continue
    
    print(f"✅ {len(drivers)} drivers")
    
    # Collect car_data
    all_data = []
    for driver_num in drivers:
        try:
            r = requests.get(f'{API}/car_data',
                           params={'session_key': session_key, 'driver_number': driver_num},
                           timeout=30)
            
            if r.status_code == 200:
                data = r.json()
                if len(data) > 0:
                    all_data.extend(data)
                    print(f"   ✓ Driver {driver_num}: {len(data):,}", flush=True)
            
            time.sleep(0.1)
        except Exception as e:
            print(f"   ✗ Driver {driver_num}: {str(e)[:20]}", flush=True)
    
    # Save
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(os.path.join(session_path, 'car_data.csv'), index=False)
        total_records += len(df)
        successful += 1
        
        size_mb = len(df) * 100 / (1024 * 1024)
        print(f"   💾 {len(df):,} records ({size_mb:.1f} MB)")
    
    # Progress
    if (idx + 1) % 5 == 0:
        print(f"\n📊 Progress: {idx+1}/{len(existing_sessions)}")
        print(f"   Collected: {successful} sessions")
        print(f"   Total records: {total_records:,}\n")

print("\n" + "="*80)
print("✅ CAR DATA COLLECTION COMPLETE!")
print("="*80)
print(f"Sessions with car_data: {successful}/{len(existing_sessions)}")
print(f"Total telemetry records: {total_records:,}")
print(f"Estimated size: ~{total_records * 100 / (1024**3):.2f} GB")
print("="*80)
