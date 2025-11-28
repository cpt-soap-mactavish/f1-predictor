"""
Quick test: Which OpenF1 sessions actually HAVE car_data?
"""
import requests
import pandas as pd

print("Testing which sessions have car_data available...\n")

# Get all sessions
sessions = requests.get('https://api.openf1.org/v1/sessions').json()
df = pd.DataFrame(sessions)

# Test a sample from each year
years = sorted(df['year'].unique())

for year in years:
    print(f"\n{'='*60}")
    print(f"Year: {year}")
    print('='*60)
    
    year_sessions = df[df['year'] == year]
    
    # Test first 3 race sessions
    races = year_sessions[year_sessions['session_name'] == 'Race'].head(3)
    
    for _, session in races.iterrows():
        session_key = session['session_key']
        meeting = session.get('meeting_official_name', 'Unknown')
        
        # Try to get car_data
        r = requests.get(
            'https://api.openf1.org/v1/car_data',
            params={'session_key': session_key, 'driver_number': 1}
        )
        
        if r.status_code == 200:
            data = r.json()
            if len(data) > 0:
                print(f"✅ {meeting}: {len(data)} car_data points")
            else:
                print(f"❌ {meeting}: No car_data")
        else:
            print(f"⚠️  {meeting}: API error {r.status_code}")

print("\n" + "="*60)
print("CONCLUSION:")
print("Which years have car_data available?")
print("="*60)
