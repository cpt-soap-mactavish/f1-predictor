"""
F1 Telemetry Data Collection - Comprehensive Script
Uses FastF1 to collect practice times, tire data, and race pace
ALL DATA STORED ON E DRIVE
Target: Improve model accuracy from 55% to 70%
"""

import fastf1
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

# E DRIVE STORAGE PATHS
BASE_DIR = 'E:/Shivam/F1/f1-ai-predictor'
DATA_DIR = f'{BASE_DIR}/data'
CACHE_DIR = f'{DATA_DIR}/fastf1_telemetry_cache'
OUTPUT_DIR = f'{DATA_DIR}/telemetry_features'

# Create directories if they don't exist
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Enable FastF1 cache (on E drive)
fastf1.Cache.enable_cache(CACHE_DIR)

print("="*80)
print("F1 TELEMETRY DATA COLLECTION")
print("="*80)
print(f"Storage: E Drive")
print(f"Cache: {CACHE_DIR}")
print(f"Output: {OUTPUT_DIR}")
print("="*80)

def collect_practice_pace(year, round_num, event_name):
    """
    Extract practice session long-run race pace
    This shows TRUE race speed before qualifying
    """
    try:
        # Load FP3 (final practice, closest to race conditions)
        fp3 = fastf1.get_session(year, round_num, 'FP3')
        fp3.load()
        
        # Get long-run pace (exclude first 3 laps - warm up)
        laps = fp3.laps[fp3.laps['LapNumber'] > 3].copy()
        
        # Calculate average race pace per driver
        race_pace = laps.groupby('Driver').agg({
            'LapTime': lambda x: x.dt.total_seconds().mean(),
            'Compound': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'UNKNOWN'
        }).reset_index()
        
        race_pace.columns = ['driver_code', 'fp3_avg_laptime', 'fp3_compound']
        race_pace['season'] = year
        race_pace['round'] = round_num
        race_pace['event_name'] = event_name
        
        return race_pace
        
    except Exception as e:
        print(f"   ⚠️  FP3 data unavailable: {str(e)[:50]}")
        return None

def collect_tire_degradation(year, round_num, event_name):
    """
    Calculate tire degradation rates from race
    Shows who can make tires last longer (strategic advantage)
    """
    try:
        # Load race session
        race = fastf1.get_session(year, round_num, 'R')
        race.load()
        
        laps = race.laps
        
        # Calculate degradation per driver per compound
        deg_data = []
        
        for driver in laps['Driver'].unique():
            driver_laps = laps[laps['Driver'] == driver]
            
            for compound in driver_laps['Compound'].unique():
                if pd.isna(compound):
                    continue
                
                compound_laps = driver_laps[driver_laps['Compound'] == compound].copy()
                
                if len(compound_laps) < 5:  # Need at least 5 laps
                    continue
                
                # Calculate lap time increase per lap (degradation)
                compound_laps = compound_laps.sort_values('LapNumber')
                compound_laps['laptime_seconds'] = compound_laps['LapTime'].dt.total_seconds()
                
                # Linear regression: laptime vs tire age
                tire_life = compound_laps['TyreLife'].values
                lap_times = compound_laps['laptime_seconds'].values
                
                # Remove outliers (SC laps, etc.)
                valid = ~np.isnan(lap_times)
                if valid.sum() < 5:
                    continue
                
                tire_life = tire_life[valid]
                lap_times = lap_times[valid]
                
                # Calculate degradation rate (seconds per lap)
                if len(lap_times) > 1:
                    deg_rate = np.polyfit(tire_life, lap_times, 1)[0]
                else:
                    deg_rate = 0
                
                deg_data.append({
                    'season': year,
                    'round': round_num,
                    'event_name': event_name,
                    'driver_code': driver,
                    'compound': compound,
                    'deg_rate_sec_per_lap': deg_rate,
                    'num_laps': len(compound_laps)
                })
        
        return pd.DataFrame(deg_data)
        
    except Exception as e:
        print(f"   ⚠️  Tire data unavailable: {str(e)[:50]}")
        return None

def collect_qualifying_vs_race_pace(year, round_num, event_name):
    """
    Compare qualifying pace vs race pace
    Identifies drivers who are faster/slower in race vs quali
    """
    try:
        # Load qualifying
        quali = fastf1.get_session(year, round_num, 'Q')
        quali.load()
        
        # Get Q3 best laps (top 10 qualifiers)
        q3_laps = quali.laps[quali.laps['Q3'].notna()]
        quali_pace = q3_laps.groupby('Driver')['Q3'].min()
        
        # Load race
        race = fastf1.get_session(year, round_num, 'R')
        race.load()
        
        # Get race pace (first 10 laps, clean air)
        race_laps = race.laps[
            (race.laps['LapNumber'] >= 5) & 
            (race.laps['LapNumber'] <= 15)
        ]
        race_pace = race_laps.groupby('Driver')['LapTime'].min()
        
        # Compare
        comparison = pd.DataFrame({
            'quali_best': quali_pace,
            'race_best': race_pace
        })
        
        comparison['quali_sec'] = comparison['quali_best'].dt.total_seconds()
        comparison['race_sec'] = comparison['race_best'].dt.total_seconds()
        comparison['race_vs_quali_delta'] = comparison['race_sec'] - comparison['quali_sec']
        
        comparison = comparison.reset_index()
        comparison.columns = ['driver_code', 'quali_best', 'race_best', 'quali_sec', 'race_sec', 'race_vs_quali_delta']
        comparison['season'] = year
        comparison['round'] = round_num
        comparison['event_name'] = event_name
        
        return comparison[['season', 'round', 'event_name', 'driver_code', 'race_vs_quali_delta']]
        
    except Exception as e:
        print(f"   ⚠️  Quali vs race comparison unavailable: {str(e)[:50]}")
        return None

def collect_season_telemetry(year):
    """Collect all telemetry for a season"""
    print(f"\n📅 Season {year}")
    print("-"*80)
    
    # Get season schedule
    try:
        schedule = fastf1.get_event_schedule(year)
    except:
        print(f"   ❌ Schedule unavailable for {year}")
        return None, None, None
    
    practice_data = []
    tire_data = []
    pace_comparison = []
    
    for idx, event in schedule.iterrows():
        round_num = event['RoundNumber']
        event_name = event['EventName']
        
        # Skip testing
        if 'Test' in event_name or 'Testing' in event_name:
            continue
        
        print(f"   R{round_num:02d} {event_name:30s} ", end='')
        
        # Collect practice pace
        fp3_data = collect_practice_pace(year, round_num, event_name)
        if fp3_data is not None:
            practice_data.append(fp3_data)
            print("✅ FP3 ", end='')
        else:
            print("❌ FP3 ", end='')
        
        # Collect tire degradation
        tire_deg = collect_tire_degradation(year, round_num, event_name)
        if tire_deg is not None:
            tire_data.append(tire_deg)
            print("✅ Tires ", end='')
        else:
            print("❌ Tires ", end='')
        
        # Collect quali vs race
        pace_comp = collect_qualifying_vs_race_pace(year, round_num, event_name)
        if pace_comp is not None:
            pace_comparison.append(pace_comp)
            print("✅ Pace")
        else:
            print("❌ Pace")
    
    # Combine data
    practice_df = pd.concat(practice_data, ignore_index=True) if practice_data else None
    tire_df = pd.concat(tire_data, ignore_index=True) if tire_data else None
    pace_df = pd.concat(pace_comparison, ignore_index=True) if pace_comparison else None
    
    return practice_df, tire_df, pace_df

def save_telemetry_data(practice_df, tire_df, pace_df, year):
    """Save collected data to E drive"""
    year_dir = f'{OUTPUT_DIR}/{year}'
    os.makedirs(year_dir, exist_ok=True)
    
    if practice_df is not None:
        practice_df.to_csv(f'{year_dir}/practice_pace.csv', index=False)
        print(f"   💾 Saved practice pace: {len(practice_df)} records")
    
    if tire_df is not None:
        tire_df.to_csv(f'{year_dir}/tire_degradation.csv', index=False)
        print(f"   💾 Saved tire data: {len(tire_df)} records")
    
    if pace_df is not None:
        pace_df.to_csv(f'{year_dir}/pace_comparison.csv', index=False)
        print(f"   💾 Saved pace comparison: {len(pace_df)} records")

if __name__ == "__main__":
    print("\n🚀 Starting telemetry collection (2018-2024)")
    print(f"⚠️  This will take 2-3 hours and use ~5GB on E drive")
    print(f"📁 All data will be saved to: {OUTPUT_DIR}\n")
    
    # Collect data year by year
    for year in range(2018, 2025):
        practice_df, tire_df, pace_df = collect_season_telemetry(year)
        
        if practice_df is not None or tire_df is not None or pace_df is not None:
            save_telemetry_data(practice_df, tire_df, pace_df, year)
        else:
            print(f"   ❌ No data collected for {year}")
    
    print("\n" + "="*80)
    print("✅ TELEMETRY COLLECTION COMPLETE!")
    print("="*80)
    print(f"\nData saved to E drive:")
    print(f"  {OUTPUT_DIR}")
    print(f"\nNext steps:")
    print("  1. Merge telemetry with existing race data")
    print("  2. Retrain model with new features")
    print("  3. Validate on 2024 races")
    print("="*80)
