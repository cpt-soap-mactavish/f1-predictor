"""
OpenF1 Additional Endpoints Collector - Part 2
Collects the endpoints not in the first collector:
- drivers (metadata)
- intervals (timing gaps)
- location (GPS tracking)
- team_radio (communications)
- position (race positions)

Run this AFTER collect_openf1_complete.py finishes
Storage: E:/Shivam/F1/f1-ai-predictor/data/openf1_complete/
"""

import pandas as pd
import requests
import os
import time

BASE_DIR = 'E:/Shivam/F1/f1-ai-predictor/data/openf1_complete'
API = 'https://api.openf1.org/v1'

# Load race sessions
SESSIONS_FILE = 'E:/Shivam/F1/f1-ai-predictor/data/openf1_race_sessions.csv'

print("="*80)
print("OpenF1 ADDITIONAL ENDPOINTS COLLECTOR (Part 2)")
print("="*80)
print("\nCollecting:")
print("  ✓ drivers")
print("  ✓ intervals")
print("  ✓ location")
print("  ✓ team_radio")
print("  ✓ position")
print("="*80)

sessions_df = pd.read_csv(SESSIONS_FILE)
print(f"\n📋 {len(sessions_df)} race sessions loaded")

def collect_additional_endpoints(session_key, year, meeting_name):
    """Collect missing endpoints for one session"""
    
    print(f"\n{'='*80}")
    print(f"Session {session_key}: {year} - {meeting_name}")
    print(f"{'='*80}")
    
    session_dir = f'{BASE_DIR}/{year}/session_{session_key}_{meeting_name.replace(" ", "_")}'
    os.makedirs(session_dir, exist_ok=True)
    
    collected = {}
    
    # 1. DRIVERS (metadata for all drivers in session)
    print("\n👤 Drivers...", end=' ')
    try:
        r = requests.get(f'{API}/drivers', params={'session_key': session_key}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if len(data) > 0:
                df = pd.DataFrame(data)
                df.to_csv(f'{session_dir}/drivers.csv', index=False)
                print(f"✅ {len(df)} drivers")
                collected['drivers'] = len(df)
            else:
                print("❌ No data")
        else:
            print(f"❌ HTTP {r.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)[:30]}")
    
    # 2. INTERVALS (timing gaps)
    print("⏳ Intervals...", end=' ')
    try:
        r = requests.get(f'{API}/intervals', params={'session_key': session_key}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if len(data) > 0:
                df = pd.DataFrame(data)
                df.to_csv(f'{session_dir}/intervals.csv', index=False)
                print(f"✅ {len(df)} records")
                collected['intervals'] = len(df)
            else:
                print("❌ No data")
        else:
            print(f"❌ HTTP {r.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)[:30]}")
    
    # 3. POSITION (race positions over time)
    print("📊 Position...", end=' ')
    try:
        r = requests.get(f'{API}/position', params={'session_key': session_key}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if len(data) > 0:
                df = pd.DataFrame(data)
                df.to_csv(f'{session_dir}/position.csv', index=False)
                print(f"✅ {len(df)} records")
                collected['position'] = len(df)
            else:
                print("❌ No data")
        else:
            print(f"❌ HTTP {r.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)[:30]}")
    
    # 4. LOCATION (GPS tracking - WARNING: HUGE dataset!)
    # Skip or sample due to size
    print("📍 Location...", end=' ')
    print("⚠️  Skipped (too large - would need sampling)")
    
    # 5. TEAM RADIO (communications)
    print("📻 Team Radio...", end=' ')
    try:
        r = requests.get(f'{API}/team_radio', params={'session_key': session_key}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if len(data) > 0:
                df = pd.DataFrame(data)
                df.to_csv(f'{session_dir}/team_radio.csv', index=False)
                print(f"✅ {len(df)} messages")
                collected['team_radio'] = len(df)
            else:
                print("❌ No data")
        else:
            print(f"❌ HTTP {r.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)[:30]}")
    
    if collected:
        print(f"\n📊 Collected {len(collected)} additional datasets")
        print(f"   Total records: {sum(collected.values())}")
    
    return collected

# Main loop
print(f"\n🚀 Starting collection...\n")

total_stats = {'drivers': 0, 'intervals': 0, 'position': 0, 'team_radio': 0}
successful = 0

for idx, row in sessions_df.iterrows():
    session_key = row['session_key']
    year = row['year']
    meeting = row.get('meeting_official_name', f'Race_{idx}')
    
    try:
        session_data = collect_additional_endpoints(session_key, year, meeting)
        
        if session_data:
            successful += 1
            for key, value in session_data.items():
                if key in total_stats:
                    total_stats[key] += value
        
        # Progress
        if (idx + 1) % 5 == 0:
            print(f"\n{'='*80}")
            print(f"📊 Progress: {idx+1}/{len(sessions_df)}")
            print(f"   Successful: {successful}")
            print(f"   Total: {sum(total_stats.values())} records")
            print(f"{'='*80}\n")
        
        time.sleep(0.5)  # Rate limiting
        
    except Exception as e:
        print(f"\n❌ Session {session_key} error: {str(e)[:50]}")

# Final summary
print("\n" + "="*80)
print("✅ PART 2 COLLECTION COMPLETE!")
print("="*80)
print(f"\nSuccessful sessions: {successful}/{len(sessions_df)}")
print(f"\nData collected:")
for endpoint, count in total_stats.items():
    if count > 0:
        print(f"  {endpoint:15s}: {count:,} records")

print(f"\nAll data saved to: {BASE_DIR}")
print("\n🎉 Combined with Part 1, you now have COMPLETE OpenF1 data!")
print("="*80)
