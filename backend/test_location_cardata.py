"""
Test location and full car_data collection
Checks if these endpoints work and how much data they return
"""

import requests
import pandas as pd

API = 'https://api.openf1.org/v1'

# Test with session 9159 (Singapore 2023 - we know it has data)
test_session = 9159
test_driver = 55

print("="*80)
print("TESTING LOCATION & FULL CAR_DATA")
print("="*80)

# 1. Test Location
print("\n📍 Testing Location endpoint...")
print(f"   Session: {test_session}, Driver: {test_driver}")

r = requests.get(
    f'{API}/location',
    params={'session_key': test_session, 'driver_number': test_driver},
    timeout=30
)

if r.status_code == 200:
    data = r.json()
    print(f"   ✅ Status 200: {len(data)} location points")
    
    if len(data) > 0:
        df = pd.DataFrame(data)
        print(f"   Columns: {list(df.columns)}")
        print(f"\n   Sample:")
        print(df.head(3))
        
        # Estimate full size
        size_mb = len(data) * 150 / 1_000_000  # Rough estimate
        print(f"\n   Estimated size for one driver: {size_mb:.1f} MB")
        print(f"   For 20 drivers: {size_mb * 20:.1f} MB per race")
        print(f"   For 68 races: {size_mb * 20 * 68:.1f} MB total")
    else:
        print("   ❌ No data returned")
else:
    print(f"   ❌ HTTP {r.status_code}: {r.text[:100]}")

# 2. Test full car_data for ALL drivers
print("\n\n🏎️  Testing FULL car_data collection...")

# Get all driver numbers that have data
print("   Finding all active drivers...")
active_drivers = []

for num in range(1, 100):
    r = requests.get(
        f'{API}/car_data',
        params={'session_key': test_session, 'driver_number': num},
        timeout=5
    )
    
    if r.status_code == 200:
        data = r.json()
        if len(data) > 0:
            active_drivers.append((num, len(data)))
            print(f"   ✓ Driver {num}: {len(data):,} points")

print(f"\n   ✅ Found {len(active_drivers)} active drivers")

total_car_data = sum(count for _, count in active_drivers)
print(f"   Total car_data points: {total_car_data:,}")
print(f"   Estimated size: {total_car_data * 100 / 1_000_000:.1f} MB")

# 3. Recommendation
print("\n" + "="*80)
print("RECOMMENDATIONS:")
print("="*80)

if total_car_data > 0:
    print(f"\n✅ Car Data:")
    print(f"   - DOABLE: {total_car_data:,} points per race")
    print(f"   - For 68 races: ~{total_car_data * 68 / 1_000_000:.1f}M points")
    print(f"   - Storage: ~{total_car_data * 68 * 100 / (1024**3):.2f} GB")
    print(f"   - Time: ~{len(active_drivers) * 68 * 0.1 / 60:.1f} minutes")

if len(r.json() if r.status_code == 200 else []) > 0:
    location_count = len(r.json())
    print(f"\n⚠️  Location Data:")
    print(f"   - HUGE: {location_count:,} points per driver")
    print(f"   - For 20 drivers × 68 races: ~{location_count * 20 * 68 / 1_000_000:.1f}M points")
    print(f"   - Storage: ~{location_count * 20 * 68 * 150 / (1024**3):.2f} GB")
    print(f"   - Recommendation: SKIP or sample (1% of points)")

print("\n" + "="*80)
