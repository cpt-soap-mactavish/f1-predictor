"""
Collect F1 Historical Data using FastF1 Library
Gathers: Weather conditions, Tire compounds, Safety car occurrences
Coverage: 2018-2025 (FastF1 has full data from 2018+)
"""

import fastf1
import pandas as pd
import numpy as np
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Enable FastF1 cache for faster subsequent runs
fastf1.Cache.enable_cache('../data/fastf1_cache')

def collect_race_data_fast(year_start=2018, year_end=2025):
    """
    Collect comprehensive race data using FastF1
    Returns DataFrame with weather, tires, and safety car info
    """
    print(f"🏎️  Collecting F1 Data from FastF1 ({year_start}-{year_end})")
    print("=" * 80)
    
    all_race_data = []
    
    for year in range(year_start, year_end + 1):
        print(f"\n📅 Season {year}")
        print("-" * 80)
        
        try:
            # Get season schedule
            schedule = fastf1.get_event_schedule(year)
            
            for idx, event in schedule.iterrows():
                event_name = event['EventName']
                round_num = event['RoundNumber']
                
                # Skip testing sessions
                if 'Test' in event_name or 'Testing' in event_name:
                    continue
                
                print(f"   R{round_num:02d} {event_name:30s} ", end='')
                
                try:
                    # Load race session
                    session = fastf1.get_session(year, round_num, 'R')
                    session.load()
                    
                    # 1. WEATHER DATA
                    weather_data = session.weather_data
                    if len(weather_data) > 0:
                        # Get average conditions during race
                        avg_air_temp = weather_data['AirTemp'].mean()
                        avg_track_temp = weather_data['TrackTemp'].mean()
                        avg_humidity = weather_data['Humidity'].mean()
                        rainfall = weather_data['Rainfall'].any()
                    else:
                        avg_air_temp = avg_track_temp = avg_humidity = None
                        rainfall = False
                    
                    # 2. TIRE COMPOUNDS
                    # Get most common starting tire
                    laps = session.laps
                    if len(laps) > 0:
                        starting_compounds = laps[laps['LapNumber'] == 1]['Compound'].value_counts()
                        most_common_start_tire = starting_compounds.index[0] if len(starting_compounds) > 0 else 'UNKNOWN'
                    else:
                        most_common_start_tire = 'UNKNOWN'
                    
                    # 3. SAFETY CAR
                    # Check if safety car was deployed
                    safety_car_laps = 0
                    if hasattr(session, 'laps') and len(session.laps) > 0:
                        # Safety car indicated by slower lap times across field
                        # Or we can check session messages
                        try:
                            messages = session.session_status
                            if messages is not None and len(messages) > 0:
                                # Check for safety car in session status
                                sc_messages = messages[messages['Status'].str.contains('SafetyCar|SC', case=False, na=False)]
                                safety_car_occurred = len(sc_messages) > 0
                            else:
                                safety_car_occurred = False
                        except:
                            safety_car_occurred = False
                    else:
                        safety_car_occurred = False
                    
                    # 4. RACE INFO
                    circuit_name = event['Location']
                    
                    race_info = {
                        'season': year,
                        'round': round_num,
                        'race_name': event_name,
                        'circuit': circuit_name,
                        'date': event['EventDate'].strftime('%Y-%m-%d') if pd.notnull(event['EventDate']) else None,
                        
                        # Weather
                        'air_temp': avg_air_temp,
                        'track_temp': avg_track_temp,
                        'humidity': avg_humidity,
                        'rainfall': rainfall,
                        'weather_condition': 'Wet' if rainfall else 'Dry',
                        
                        # Strategy
                        'common_start_tire': most_common_start_tire,
                        'safety_car_occurred': safety_car_occurred,
                        
                        # Meta
                        'data_source': 'FastF1'
                    }
                    
                    all_race_data.append(race_info)
                    
                    # Display summary
                    weather_icon = '🌧️' if rainfall else '☀️'
                    sc_icon = '🚨' if safety_car_occurred else '  '
                    print(f"{weather_icon} {avg_air_temp:.1f}°C | {most_common_start_tire:6s} | {sc_icon}")
                    
                except Exception as e:
                    print(f"❌ Error: {str(e)[:50]}")
                    continue
                
        except Exception as e:
            print(f"   ❌ Season error: {e}")
            continue
    
    # Create DataFrame
    df = pd.DataFrame(all_race_data)
    
    print("\n" + "=" * 80)
    print(f"✅ Data collection complete!")
    print(f"   Total races: {len(df)}")
    print(f"   Wet races: {df['rainfall'].sum()} ({df['rainfall'].sum()/len(df)*100:.1f}%)")
    print(f"   Safety cars: {df['safety_car_occurred'].sum()} ({df['safety_car_occurred'].sum()/len(df)*100:.1f}%)")
    
    return df

def save_collected_data(df, output_path='../data/f1_fastf1_data.csv'):
    """Save collected data"""
    df.to_csv(output_path, index=False)
    print(f"\n💾 Saved to: {output_path}")
    
    # Display statistics
    print("\n📊 Data Summary:")
    print(f"   Seasons: {df['season'].min()}-{df['season'].max()}")
    print(f"   Races: {len(df)}")
    print(f"   Avg Air Temp: {df['air_temp'].mean():.1f}°C")
    print(f"   Avg Track Temp: {df['track_temp'].mean():.1f}°C")
    print(f"   Avg Humidity: {df['humidity'].mean():.1f}%")
    print(f"\n   Tire Distribution:")
    print(df['common_start_tire'].value_counts())
    
    return output_path

if __name__ == "__main__":
    print("🚀 Starting F1 Data Collection with FastF1...")
    print("   This may take 10-20 minutes for full dataset\n")
    
    # Collect data (2018-2025 only - FastF1 has complete data from 2018)
    df = collect_race_data_fast(year_start=2018, year_end=2024)
    
    # Save
    output_file = save_collected_data(df)
    
    print(f"\n🎉 Complete! Next steps:")
    print(f"   1. Merge {output_file} with existing f1_race_data.csv")
    print(f"   2. Add weather/tire/SC columns to prepared dataset")
    print(f"   3. Retrain model with new features")
