import requests

print("Testing OpenF1 data availability (2018-2025):")
print("="*60)

for year in range(2018, 2026):
    r = requests.get(f'https://api.openf1.org/v1/meetings?year={year}')
    data = r.json()
    
    if len(data) > 0:
        print(f"✅ {year}: {len(data)} races")
    else:
        print(f"❌ {year}: No data")

print("\n" + "="*60)
print("Summary: OpenF1 has data from which years?")
