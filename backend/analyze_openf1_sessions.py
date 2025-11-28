"""
Step 1: Analyze OpenF1 Sessions Data Properly
Download and understand the full sessions structure
"""

import requests
import pandas as pd
import json

print("="*80)
print("OpenF1 SESSIONS ANALYSIS")
print("="*80)

# Get all sessions
print("\n📋 Downloading all sessions...")
response = requests.get('https://api.openf1.org/v1/sessions')
sessions = response.json()

# Convert to DataFrame
df = pd.DataFrame(sessions)

print(f"✅ Retrieved {len(df)} sessions")
print(f"\nColumns available: {list(df.columns)}")

# Save raw data
df.to_csv('E:/Shivam/F1/f1-ai-predictor/data/openf1_sessions.csv', index=False)
print(f"\n💾 Saved to: E:/Shivam/F1/f1-ai-predictor/data/openf1_sessions.csv")

# Analyze structure
print("\n" + "="*80)
print("SESSIONS BREAKDOWN")
print("="*80)

print("\n1. BY YEAR:")
print(df.groupby('year').size())

print("\n2. BY SESSION TYPE:")
print(df.groupby('session_name').size())

print("\n3. BY YEAR AND SESSION TYPE:")
breakdown = df.groupby(['year', 'session_name']).size().reset_index(name='count')
for year in sorted(df['year'].unique()):
    year_data = breakdown[breakdown['year'] == year]
    print(f"\n{year}:")
    for _, row in year_data.iterrows():
        print(f"  {row['session_name']:20s}: {row['count']:3d} sessions")

# Sample session details
print("\n" + "="*80)
print("SAMPLE SESSION DETAILS")
print("="*80)

sample = df.iloc[0]
print("\nFirst session structure:")
for col in df.columns:
    value = sample[col]
    if pd.notna(value):
        print(f"  {col:30s}: {value}")

# Find race sessions with useful info
races = df[df['session_name'] == 'Race'].copy()

print("\n" + "="*80)
print(f"RACE SESSIONS ({len(races)} total)")
print("="*80)

print("\nFirst 5 races:")
display_cols = ['session_key', 'year', 'meeting_official_name', 'session_name', 'date_start']
available_cols = [col for col in display_cols if col in races.columns]
print(races[available_cols].head().to_string(index=False))

# Save race sessions separately
races.to_csv('E:/Shivam/F1/f1-ai-predictor/data/openf1_race_sessions.csv', index=False)
print(f"\n💾 Saved race sessions to: E:/Shivam/F1/f1-ai-predictor/data/openf1_race_sessions.csv")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print(f"\nTotal sessions: {len(df)}")
print(f"Race sessions: {len(races)}")
print(f"Years covered: {sorted(df['year'].unique())}")
print("\nReady for targeted car_data collection!")
