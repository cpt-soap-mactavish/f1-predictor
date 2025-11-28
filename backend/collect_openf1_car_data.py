"""
OpenF1 Car Data Collector - Robust Version
Tests each session first, then collects only what's available
Storage: E:/Shivam/F1/f1-ai-predictor/data/openf1_car_data/
"""

import requests
import pandas as pd
import os
import time
from tqdm import tqdm

# E DRIVE STORAGE
OUTPUT_DIR = 'E:/Shivam/F1/f1-ai-predictor/data/openf1_car_data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

API_BASE = 'https://api.openf1.org/v1'

def get_all_sessions():
    """Get all sessions from OpenF1"""
    print("📋 Fetching all sessions...")
    r = requests.get(f'{API_BASE}/sessions')
    if r.status_code == 200:
        sessions = pd.DataFrame(r.json())
        print(f"✅ Found {len(sessions)} total sessions")
        print(f"   Years: {sorted(sessions['year'].unique())}")
        return sessions
    else:
        print(f"❌ Failed to get sessions: {r.status_code}")
        return None

def test_session_has_car_data(session_key):
    """Test if a session has car_data available"""
    # Try with driver 1 (common number)
    url = f'{API_BASE}/car_data'
    params = {
        'session_key': session_key,
        'driver_number': 1
    }
    
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return len(data) > 0
        return False
    except:
        return False

def get_drivers_in_session(session_key):
    """Get list of driver numbers that have car_data for this session"""
    drivers_with_data = []
    
    # Test common driver numbers (F1 uses 1-99)
    test_numbers = list(range(1, 100))
    
    for num in test_numbers:
        url = f'{API_BASE}/car_data'
        params = {
            'session_key': session_key,
            'driver_number': num
        }
        
        try:
            r = requests.get(url, params=params, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 0:
                    drivers_with_data.append(num)
            
            time.sleep(0.05)  # Rate limiting
            
        except:
            continue
    
    return drivers_with_data

def collect_car_data_for_session(session_key, session_info):
    """Collect all car_data for a session"""
    year = session_info['year']
    session_name = session_info['session_name']
    meeting_name = session_info.get('meeting_official_name', 'Unknown')
    
    print(f"\n🏎️  {year} - {meeting_name} - {session_name} (session {session_key})")
    
    # Find drivers with data
    print("   Finding drivers with data...", end=' ')
    drivers = get_drivers_in_session(session_key)
    
    if len(drivers) == 0:
        print("❌ No car_data available")
        return 0
    
    print(f"✅ Found {len(drivers)} drivers")
    
    # Collect data for each driver
    all_data = []
    
    for driver_num in drivers:
        url = f'{API_BASE}/car_data'
        params = {
            'session_key': session_key,
            'driver_number': driver_num
        }
        
        try:
            r = requests.get(url, params=params, timeout=30)
            if r.status_code == 200:
                data = r.json()
                all_data.extend(data)
                print(f"   ✓ Driver {driver_num}: {len(data)} points")
            
            time.sleep(0.1)
        except Exception as e:
            print(f"   ✗ Driver {driver_num}: Error - {str(e)[:30]}")
    
    # Save to CSV
    if len(all_data) > 0:
        df = pd.DataFrame(all_data)
        
        # Create year directory
        year_dir = f'{OUTPUT_DIR}/{year}'
        os.makedirs(year_dir, exist_ok=True)
        
        # Clean filename
        clean_meeting = meeting_name.replace(' ', '_').replace('/', '_')
        filename = f'{year_dir}/{clean_meeting}_{session_name}_session_{session_key}.csv'
        
        df.to_csv(filename, index=False)
        
        file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
        print(f"   💾 Saved: {len(df):,} records ({file_size:.1f} MB)")
        print(f"   📁 {filename}")
        
        return len(df)
    
    return 0

def main():
    print("="*80)
    print("OpenF1 CAR DATA COLLECTOR - Robust Version")
    print("="*80)
    print(f"Output directory: {OUTPUT_DIR}")
    print("="*80)
    
    # Step 1: Get all sessions
    sessions_df = get_all_sessions()
    if sessions_df is None:
        return
    
    # Step 2: Filter for Race sessions (most important)
    # You can change to include 'Qualifying', 'Practice 1', etc.
    race_sessions = sessions_df[sessions_df['session_name'] == 'Race'].copy()
    
    print(f"\n🏁 Collecting car_data for {len(race_sessions)} Race sessions")
    print(f"Years: {sorted(race_sessions['year'].unique())}\n")
    
    # Step 3: Test first session
    print("🧪 Testing first session for car_data availability...")
    test_session = race_sessions.iloc[0]
    has_data = test_session_has_car_data(test_session['session_key'])
    
    if not has_data:
        print(f"\n⚠️  WARNING: Test session has no car_data!")
        print("   Trying a few more sessions to find one that works...")
        
        # Try first 5 sessions
        for i in range(min(5, len(race_sessions))):
            test = race_sessions.iloc[i]
            if test_session_has_car_data(test['session_key']):
                print(f"   ✅ Found working session: {test['meeting_official_name']}")
                break
        else:
            print("\n❌ No sessions found with car_data available")
            print("   OpenF1 may not have telemetry data yet")
            return
    else:
        print("✅ Car data confirmed available!\n")
    
    # Step 4: Collect all data
    total_records = 0
    successful = 0
    failed = 0
    
    for idx, row in race_sessions.iterrows():
        session_key = row['session_key']
        
        try:
            records = collect_car_data_for_session(session_key, row)
            
            if records > 0:
                total_records += records
                successful += 1
            else:
                failed += 1
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")
            failed += 1
        
        # Progress update every 5 sessions
        if (idx + 1) % 5 == 0:
            print(f"\n📊 Progress: {idx+1}/{len(race_sessions)}")
            print(f"   Records: {total_records:,}")
            print(f"   Successful: {successful}, Failed: {failed}\n")
    
    # Final summary
    print("\n" + "="*80)
    print("✅ COLLECTION COMPLETE!")
    print("="*80)
    print(f"Total records: {total_records:,}")
    print(f"Successful sessions: {successful}")
    print(f"Failed sessions: {failed}")
    print(f"Success rate: {successful/(successful+failed)*100:.1f}%")
    print(f"\nData saved to: {OUTPUT_DIR}")
    print("="*80)
    
    # Show what was collected
    for year in sorted(race_sessions['year'].unique()):
        year_dir = f'{OUTPUT_DIR}/{year}'
        if os.path.exists(year_dir):
            files = os.listdir(year_dir)
            if files:
                total_size = sum(os.path.getsize(f'{year_dir}/{f}') for f in files)
                print(f"{year}: {len(files)} files, {total_size/(1024*1024):.1f} MB")

if __name__ == "__main__":
    main()
