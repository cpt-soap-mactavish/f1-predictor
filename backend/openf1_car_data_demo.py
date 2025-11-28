"""
OpenF1 Car Data Deep Dive
Shows exactly what telemetry data is available
"""

import requests
import pandas as pd

print("="*80)
print("OpenF1 CAR DATA - COMPLETE ANALYSIS")
print("="*80)

# Example: Sainz (55) in 2023 Singapore qualifying (session_key=9159)
url = "https://api.openf1.org/v1/car_data"
params = {
    'driver_number': 55,
    'session_key': 9159,
    'speed>=': 315  # High-speed moments
}

response = requests.get(url, params=params)
data = response.json()

if len(data) > 0:
    df = pd.DataFrame(data)
    
    print(f"\n✅ Retrieved {len(df)} car data records")
    print(f"\nColumns available:")
    for col in df.columns:
        print(f"  • {col}: {df[col].dtype}")
    
    print("\n" + "="*80)
    print("SAMPLE CAR DATA (Top speed moments):")
    print("="*80)
    print(df.to_string(index=False))
    
    print("\n" + "="*80)
    print("DATA SUMMARY:")
    print("="*80)
    print(df.describe())
    
    print("\n" + "="*80)
    print("WHAT THIS TELLS US:")
    print("="*80)
    print(f"""
- Date: Timestamp of each data point
- Session: {df['session_key'].iloc[0]} (Singapore 2023 Qualifying)
- Driver: {df['driver_number'].iloc[0]} (Sainz)
- Meeting: {df['meeting_key'].iloc[0]}

TELEMETRY DATA:
- n_gear: {df['n_gear'].min()}-{df['n_gear'].max()} (gears used)
- speed: {df['speed'].min():.1f}-{df['speed'].max():.1f} km/h
- RPM: {df['rpm'].min()}-{df['rpm'].max()} (engine speed)
- Throttle: {df['throttle'].min()}-{df['throttle'].max()}% (0-100)
- Brake: {df['brake'].astype(bool).sum()}/{len(df)} (True/False)
- DRS: {df['drs'].sum()} open / {len(df)} total

🎯 USE CASES FOR PREDICTIONS:
1. Top Speed: Identify fastest car on straights (overtaking ability)
2. Throttle Application: Confidence/traction level
3. DRS Efficiency: How often can they use DRS
4. RPM Management: Engine mode (qualifying vs race)
    """)

# Now let's get MORE data  
print("\n" + "="*80)
print("COLLECTING COMPREHENSIVE CAR DATA...")
print("="*80)

# Get all car data for one lap (more manageable)
# Session 9159 = Singapore 2023 Quali
# Driver 55 = Sainz
# No speed filter = ALL data points

params_full = {
    'session_key': 9159,
    'driver_number': 55
}

print("\nFetching ALL car data for Sainz in Singapore 2023 Quali...")
response_full = requests.get(url, params=params_full)
data_full = response_full.json()

if len(data_full) > 0:
    print(f"✅ Total data points: {len(data_full)}")
    df_full = pd.DataFrame(data_full)
    
    print(f"\nSpeed stats:")
    print(f"  Max speed: {df_full['speed'].max():.1f} km/h")
    print(f"  Avg speed: {df_full['speed'].mean():.1f} km/h")
    print(f"  Min speed: {df_full['speed'].min():.1f} km/h")
    
    print(f"\nThrottle stats:")
    print(f"  Full throttle: {(df_full['throttle'] == 100).sum()} points")
    print(f"  Part throttle: {((df_full['throttle'] > 0) & (df_full['throttle'] < 100)).sum()} points")
    print(f"  No throttle: {(df_full['throttle'] == 0).sum()} points")
    
    # DRS zones
    drs_points = df_full[df_full['drs'] > 0]
    print(f"\nDRS:")
    print(f"  DRS open: {len(drs_points)} data points")
    print(f"  DRS efficiency: {len(drs_points)/len(df_full)*100:.1f}%")
    
    # Save a sample to CSV
    sample = df_full.head(100)
    sample.to_csv('E:/Shivam/F1/f1-ai-predictor/data/openf1_car_data_sample.csv', index=False)
    print(f"\n💾 Saved sample to: E:/Shivam/F1/f1-ai-predictor/data/openf1_car_data_sample.csv")

print("\n" + "="*80)
print("AVAILABLE FILTERS:")
print("="*80)
print("""
You can filter car_data by:
✅ session_key (which race/session)
✅ driver_number (specific driver)
✅ speed>=X (only high-speed moments)
✅ speed<=X (only low-speed corners)
✅ throttle>=90 (full throttle zones)
✅ drs>0 (when DRS is open)
✅ rpm>=12000 (high RPM)
✅ n_gear=8 (top gear only)

Example queries:
1. Fastest speed: speed>=300
2. DRS zones: drs>0
3. Braking zones: brake=True
4. Top gear: n_gear=8
""")
