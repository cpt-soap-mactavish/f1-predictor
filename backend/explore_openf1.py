"""
OpenF1 API Data Explorer
Test what data is available from OpenF1 for our predictions
"""

import requests
import pandas as pd
import json

OPENF1_BASE = "https://api.openf1.org/v1"

def explore_endpoint(endpoint, params=None):
    """Test an OpenF1 endpoint"""
    url = f"{OPENF1_BASE}/{endpoint}"
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            df = pd.DataFrame(data)
            print(f"\n{'='*80}")
            print(f"✅ {endpoint.upper()}")
            print(f"{'='*80}")
            print(f"Records: {len(data)}")
            print(f"Columns: {list(df.columns)}")
            print(f"\nSample data:")
            print(df.head(3))
            return df
        else:
            print(f"❌ {endpoint}: No data")
    else:
        print(f"❌ {endpoint}: Error {response.status_code}")
    
    return None

print("="*80)
print("OpenF1 API - DATA EXPLORATION")
print("="*80)
print("Testing 2024 Abu Dhabi GP (latest race)")
print()

# Use 2024 Abu Dhabi GP as example
session_params = {'year': 2024, 'country_name': 'Abu Dhabi', 'session_name': 'Race'}

# 1. WEATHER DATA
print("\n🌤️  WEATHER DATA:")
weather = explore_endpoint('weather', {'session_key': 9603})  # Abu Dhabi 2024

# 2. CAR DATA (Telemetry!)
print("\n🏎️  CAR DATA (Telemetry):")
car = explore_endpoint('car_data', {'session_key': 9603, 'driver_number': 1})

# 3. LAPS
print("\n⏱️  LAP DATA:")
laps = explore_endpoint('laps', {'session_key': 9603, 'driver_number': 1})

# 4. STINTS (Tire Strategy!)
print("\n🛞 STINT DATA (Tires):")
stints = explore_endpoint('stints', {'session_key': 9603, 'driver_number': 1})

# 5. POSITION
print("\n📍 POSITION DATA:")
position = explore_endpoint('position', {'session_key': 9603, 'driver_number': 1})

# 6. PIT STOPS
print("\n🔧 PIT STOP DATA:")
pit = explore_endpoint('pit', {'session_key': 9603, 'driver_number': 1})

# 7. INTERVALS (Gap between drivers)
print("\n⏳ INTERVAL DATA:")
intervals = explore_endpoint('intervals', {'session_key': 9603, 'driver_number': 1})

# 8. OVERTAKES (Beta!)
print("\n🏁 OVERTAKE DATA:")
overtakes = explore_endpoint('overtakes', {'session_key': 9603})

# 9. RACE CONTROL (Safety cars, flags)
print("\n🚨 RACE CONTROL:")
race_control = explore_endpoint('race_control', {'session_key': 9603})

# 10. STARTING GRID
print("\n🏁 STARTING GRID:")
grid = explore_endpoint('starting_grid', {'session_key': 9603})

# 11. DRIVERS
print("\n👤 DRIVER DATA:")
drivers = explore_endpoint('drivers', {'session_key': 9603})

# 12. MEETINGS (Race events)
print("\n📅 MEETING DATA:")
meetings = explore_endpoint('meetings', {'year': 2024})

print("\n" + "="*80)
print("SUMMARY: OpenF1 provides EVERYTHING!")
print("="*80)
print("""
✅ Weather (temp, rain, humidity)
✅ Car telemetry (speed, RPM, throttle, brake, DRS)
✅ Lap times (sector times, compound, tire age)
✅ Tire strategy (stints, compounds, pit stops)
✅ Position tracking (real-time position changes)
✅ Pit stops (duration, tire changes)
✅ Intervals (gaps between drivers)
✅ Overtakes (who overtook whom, where)
✅ Race control (safety cars, flags, incidents)
✅ Starting grid (qualifying results)
✅ Driver info (numbers, team codes)
✅ Meeting schedule (all race dates)

💡 This is MORE than FastF1 for recent races (2023+)!
""")
