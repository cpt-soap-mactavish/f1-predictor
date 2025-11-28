"""
Calculate Driver Performance Stats (Wet vs Dry)
Used to drive the simulation logic with REAL data instead of hardcoding.
"""

import pandas as pd
import json
import numpy as np

print("📊 Calculating Driver Stats...")

# Load OpenF1 data (contains rainfall and pace)
df = pd.read_csv('E:/Shivam/F1/f1-ai-predictor/data/openf1_features_expanded.csv')

# Clean columns
df.columns = df.columns.str.replace("'", "").str.strip()

# Driver Mapping (Number -> ID)
driver_map = {
    1: 'max_verstappen', 11: 'perez', 44: 'hamilton', 63: 'russell',
    16: 'leclerc', 55: 'sainz', 4: 'norris', 81: 'piastri',
    14: 'alonso', 18: 'stroll', 10: 'gasly', 31: 'ocon',
    23: 'albon', 2: 'sargeant', 22: 'tsunoda', 3: 'ricciardo',
    24: 'zhou', 77: 'bottas', 27: 'hulkenberg', 20: 'kevin_magnussen',
    40: 'lawson', 38: 'bearman', 43: 'colapinto'
}
df['driver_id'] = df['driver_number'].map(driver_map)

# Calculate Session Min Lap for Pace Ratio
session_min_laps = df.groupby('session_key')['avg_lap_time'].min().to_dict()
df['session_min_lap'] = df['session_key'].map(session_min_laps)
df['pace_ratio'] = df['avg_lap_time'] / df['session_min_lap']

# Define Wet/Dry
df['is_wet'] = df['rainfall'] > 0

# Calculate Stats
stats = {}

for driver_id in df['driver_id'].dropna().unique():
    driver_data = df[df['driver_id'] == driver_id]
    
    # Dry Pace
    dry_data = driver_data[~driver_data['is_wet']]
    dry_pace = dry_data['pace_ratio'].mean() if len(dry_data) > 0 else 1.02
    
    # Wet Pace
    wet_data = driver_data[driver_data['is_wet']]
    wet_pace = wet_data['pace_ratio'].mean() if len(wet_data) > 0 else 1.05
    
    # Wet Advantage (Negative means faster in wet relative to field)
    # Actually, pace_ratio is relative to session best.
    # So lower is always better.
    # We want to know: How does their pace_ratio change in wet?
    # But wet races have higher pace_ratios generally? No, it's a ratio to the best lap.
    # If Max is best in wet, his ratio is 1.0.
    # If he's 5th in dry, his ratio is 1.005.
    
    stats[driver_id] = {
        'dry_pace': float(dry_pace),
        'wet_pace': float(wet_pace),
        'wet_diff': float(wet_pace - dry_pace) # Lower (more negative) is better in rain
    }

# Save to JSON
output_file = 'E:/Shivam/F1/f1-ai-predictor/backend/models/driver_stats_v5.json'
with open(output_file, 'w') as f:
    json.dump(stats, f, indent=4)

print(f"✅ Saved stats for {len(stats)} drivers to {output_file}")

# Print Top 5 Rain Masters (Lowest Wet Pace Ratio)
print("\n🌧️  TOP 5 RAIN MASTERS (Data-Driven):")
sorted_wet = sorted(stats.items(), key=lambda x: x[1]['wet_pace'])
for i, (driver, data) in enumerate(sorted_wet[:5], 1):
    print(f"{i}. {driver}: {data['wet_pace']:.4f} (Dry: {data['dry_pace']:.4f})")
