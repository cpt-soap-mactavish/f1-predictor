"""
Align and Merge Script
Maps OpenF1 data to Historical schema and creates a unified dataset
"""

import pandas as pd
import numpy as np

print("="*80)
print("UNIFIED DATA ALIGNMENT")
print("="*80)

# Load datasets
print("\n📁 Loading data...")
historical_df = pd.read_csv('E:/Shivam/F1/f1-ai-predictor/data/f1_race_data_prepared.csv')
openf1_df = pd.read_csv('E:/Shivam/F1/f1-ai-predictor/data/openf1_features_expanded.csv')

print(f"✅ Historical: {len(historical_df)} records")
print(f"✅ OpenF1: {len(openf1_df)} driver-session records")

# Clean column names (remove quotes and whitespace)
openf1_df.columns = openf1_df.columns.str.replace("'", "").str.strip()
print(f"Columns: {list(openf1_df.columns)}")

# Driver Mapping (Number -> ID)
# Based on 2023-2025 grid
driver_map = {
    1: 'verstappen',
    11: 'perez',
    44: 'hamilton',
    63: 'russell',
    16: 'leclerc',
    55: 'sainz',
    4: 'norris',
    81: 'piastri',
    14: 'alonso',
    18: 'stroll',
    10: 'gasly',
    31: 'ocon',
    23: 'albon',
    2: 'sargeant',
    22: 'tsunoda',
    3: 'ricciardo',
    24: 'zhou',
    77: 'bottas',
    27: 'hulkenberg',
    20: 'kevin_magnussen',
    40: 'lawson',
    38: 'bearman',
    43: 'colapinto',
    30: 'doohan', # Future?
    99: 'giovinazzi' # Just in case
}

print(f"\n🗺️  Mapping OpenF1 drivers to historical IDs...")
openf1_df['driver_id'] = openf1_df['driver_number'].map(driver_map)

# Check for unmapped drivers
unmapped = openf1_df[openf1_df['driver_id'].isna()]['driver_number'].unique()
if len(unmapped) > 0:
    print(f"⚠️  Unmapped driver numbers: {unmapped}")
else:
    print("✅ All drivers mapped")

# Transform OpenF1 features to match Historical scale
print("\n🔄 Transforming OpenF1 features...")

# 1. Pace Ratio (avg_lap_time / session_min)
# First, calculate session min
session_min_laps = openf1_df.groupby('session_key')['avg_lap_time'].min().to_dict()
openf1_df['session_min_lap'] = openf1_df['session_key'].map(session_min_laps)
openf1_df['pace_ratio_new'] = openf1_df['avg_lap_time'] / openf1_df['session_min_lap']

# 2. Lap Std (pace_consistency * 1000)
openf1_df['lap_std_ms_new'] = openf1_df['pace_consistency'] * 1000

# 3. Pit Stops (direct copy)
openf1_df['num_pit_stops_new'] = openf1_df['num_pit_stops']

# Merge Logic
print("\n🔗 Merging datasets...")

# We merge on Year + Driver_ID
# Note: Historical data has 'season', OpenF1 has 'year'
# Also need to match the race. Historical has 'round'. OpenF1 doesn't have round directly in features.
# But we can assume 1-to-1 match if we match on Year + Driver.
# Wait, a driver races multiple times a year. We need to match the RACE.
# Historical: season, round, date.
# OpenF1: year, session_key.
# We need to map session_key to round.

# Let's try to map by DATE if possible, or just assume sequential order?
# OpenF1 sessions are ordered by session_key.
# Historical rounds are ordered by round.
# Let's create a 'race_order' for OpenF1 per year.

openf1_df = openf1_df.sort_values(['year', 'session_key'])
openf1_df['round_approx'] = openf1_df.groupby('year').cumcount() // 20 + 1 # Rough guess? No.
# Better: rank session_keys within year
openf1_df['round_rank'] = openf1_df.groupby('year')['session_key'].rank(method='dense').astype(int)

# Now merge on season=year, round=round_rank, driver_id=driver_id
# This assumes OpenF1 data covers all rounds in order.
# Check max round
print(f"OpenF1 max round rank: {openf1_df['round_rank'].max()}")
print(f"Historical max round: {historical_df['round'].max()}")

# Merge
merged_df = pd.merge(
    historical_df,
    openf1_df[['year', 'round_rank', 'driver_id', 
               'pace_ratio_new', 'lap_std_ms_new', 'num_pit_stops_new',
               'gap_trend', 'overtakes_made', 'positions_gained', 'radio_messages', 'safety_car_count']],
    left_on=['season', 'round', 'driver_id'],
    right_on=['year', 'round_rank', 'driver_id'],
    how='left',
    suffixes=('', '_openf1')
)

print(f"✅ Merged dataset: {len(merged_df)} records")

# Update Historical columns with OpenF1 data where available
print("\n✨ Updating historical columns with high-res OpenF1 data...")

# Function to combine old and new
def combine_col(row, old_col, new_col):
    if pd.notna(row[new_col]):
        return row[new_col] # Use OpenF1 if available
    return row[old_col] # Else use Historical

merged_df['pace_ratio'] = merged_df.apply(lambda x: combine_col(x, 'pace_ratio', 'pace_ratio_new'), axis=1)
merged_df['lap_std_ms'] = merged_df.apply(lambda x: combine_col(x, 'lap_std_ms', 'lap_std_ms_new'), axis=1)
merged_df['num_pit_stops'] = merged_df.apply(lambda x: combine_col(x, 'num_pit_stops', 'num_pit_stops_new'), axis=1)

# Fill NaN in new columns with 0 or mean
new_cols = ['gap_trend', 'overtakes_made', 'positions_gained', 'radio_messages', 'safety_car_count']
for col in new_cols:
    merged_df[col] = merged_df[col].fillna(0)

# Save
output_file = 'E:/Shivam/F1/f1-ai-predictor/data/f1_race_data_unified_v5.csv'
merged_df.to_csv(output_file, index=False)
print(f"\n💾 Saved unified dataset to: {output_file}")
print("   Ready for Model V5 training!")
print("="*80)
