from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
from dotenv import load_dotenv
from live_predictor import LiveRacePredictor
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

app = FastAPI(title="F1 Prediction API V5")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor
predictor = LiveRacePredictor()

# Circuit Coordinates
CIRCUIT_LOCATIONS = {
    'bahrain': {'lat': 26.0325, 'lon': 50.5106},
    'jeddah': {'lat': 21.6319, 'lon': 39.1044},
    'melbourne': {'lat': -37.8497, 'lon': 144.968},
    'suzuka': {'lat': 34.8431, 'lon': 136.541},
    'shanghai': {'lat': 31.3389, 'lon': 121.221},
    'miami': {'lat': 25.9581, 'lon': -80.2389},
    'imola': {'lat': 44.3439, 'lon': 11.7167},
    'monaco': {'lat': 43.7347, 'lon': 7.4206},
    'montreal': {'lat': 45.5017, 'lon': -73.5673},
    'barcelona': {'lat': 41.57, 'lon': 2.2611},
    'spielberg': {'lat': 47.2197, 'lon': 14.7647},
    'silverstone': {'lat': 52.0786, 'lon': -1.0169},
    'hungaroring': {'lat': 47.5789, 'lon': 19.2486},
    'spa': {'lat': 50.4372, 'lon': 5.9714},
    'zandvoort': {'lat': 52.3888, 'lon': 4.5409},
    'monza': {'lat': 45.6156, 'lon': 9.2811},
    'baku': {'lat': 40.3725, 'lon': 49.8533},
    'singapore': {'lat': 1.2914, 'lon': 103.864},
    'austin': {'lat': 30.1328, 'lon': -97.6411},
    'mexico': {'lat': 19.4042, 'lon': -99.0907},
    'interlagos': {'lat': -23.7036, 'lon': -46.6997},
    'vegas': {'lat': 36.1147, 'lon': -115.173},
    'lusail': {'lat': 25.4888, 'lon': 51.4542},
    'abudhabi': {'lat': 24.4672, 'lon': 54.6031}
}

# Pydantic models
class SimulationRequest(BaseModel):
    circuit: str
    air_temp: float
    track_temp: float
    rain_prob: float
    humidity: float
    tire: str
    pit_stops: int
    safety_car: str

class PredictionItem(BaseModel):
    position: int
    driver_id: str
    constructor_id: str
    win_probability: float
    podium_probability: float
    confidence: float

class PredictionResponse(BaseModel):
    predictions: List[PredictionItem]
    circuit: str
    conditions: dict

# 2025 Constructor Mapping
def get_constructor_2025(driver_id):
    mapping = {
        'max_verstappen': 'red_bull', 'tsunoda': 'red_bull',
        'hamilton': 'ferrari', 'leclerc': 'ferrari',
        'norris': 'mclaren', 'piastri': 'mclaren',
        'russell': 'mercedes', 'antonelli': 'mercedes',
        'alonso': 'aston_martin', 'stroll': 'aston_martin',
        'gasly': 'alpine', 'colapinto': 'alpine',
        'albon': 'williams', 'sainz': 'williams',
        'lawson': 'rb', 'hadjar': 'rb',
        'ocon': 'haas', 'bearman': 'haas',
        'hulkenberg': 'sauber', 'bortoleto': 'sauber'
    }
    return mapping.get(driver_id, 'unknown')

def fetch_forecast_weather(circuit_key, race_date_str):
    """
    Fetch 5-day forecast from OpenWeather API if race is upcoming.
    race_date_str format: "DD Mon YYYY" (e.g. "30 Nov 2025")
    """
    api_key = os.getenv("OPENWEATHER")
    if not api_key:
        return None
        
    coords = CIRCUIT_LOCATIONS.get(circuit_key)
    if not coords:
        return None
        
    try:
        # Parse Race Date
        race_date = datetime.strptime(race_date_str, "%d %b %Y")
        now = datetime.now()
        
        # Check if race is within next 5 days (OpenWeather Free Limit)
        delta = (race_date - now).days
        
        if 0 <= delta <= 5:
            print(f"🌤️ Fetching FORECAST for {circuit_key} on {race_date_str}...")
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={coords['lat']}&lon={coords['lon']}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                
                # Find forecast closest to 14:00 on race day
                target_date = race_date.strftime("%Y-%m-%d")
                best_match = None
                
                for item in data['list']:
                    dt_txt = item['dt_txt'] # "2025-11-30 15:00:00"
                    if target_date in dt_txt and "15:00" in dt_txt:
                        best_match = item
                        break
                
                # Fallback to any time on that day
                if not best_match:
                    for item in data['list']:
                        if target_date in dt_txt:
                            best_match = item
                            break
                            
                if best_match:
                    temp = best_match['main']['temp']
                    humidity = best_match['main']['humidity']
                    clouds = best_match['clouds']['all']
                    
                    # Estimate Rain
                    rain_prob = 0
                    if 'rain' in best_match:
                        rain_prob = 80
                    elif clouds > 70:
                        rain_prob = 30
                    elif clouds > 90:
                        rain_prob = 50
                        
                    summary = best_match['weather'][0]['description'].title()
                    
                    print(f"✅ Forecast found: {temp}°C, {summary}")
                    
                    return {
                        'air_temp': round(temp, 1),
                        'track_temp': round(temp + 10, 1),
                        'rain_prob': rain_prob,
                        'humidity': humidity,
                        'weather_summary': f"{summary} (Forecast)"
                    }
        else:
            print(f"ℹ️ Race date {race_date_str} is not within 5-day forecast range.")
            
    except Exception as e:
        print(f"❌ Weather Forecast Error: {e}")
        
    return None

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting F1 Prediction API (Model V5)...")
    if predictor.load_resources():
        print("✅ Live Predictor V5 ready!")

@app.get("/")
async def root():
    return {"message": "F1 Prediction API V5 (Live)", "status": "running"}

@app.post("/predict", response_model=PredictionResponse)
async def predict_race(request: SimulationRequest):
    try:
        simulation_params = {
            'circuit': request.circuit,
            'air_temp': request.air_temp,
            'track_temp': request.track_temp,
            'rain_prob': request.rain_prob,
            'humidity': request.humidity,
            'tire': request.tire,
            'pit_stops': request.pit_stops,
            'safety_car': request.safety_car
        }
        
        results_df = predictor.predict_simulation(simulation_params)
        
        predictions = []
        for _, row in results_df.iterrows():
            predictions.append(PredictionItem(
                position=int(row['predicted_position']),
                driver_id=row['driver_id'],
                constructor_id=get_constructor_2025(row['driver_id']),
                win_probability=float(row['win_prob']),
                podium_probability=float(row['podium_prob']),
                confidence=float(row['score'])
            ))
        
        return PredictionResponse(
            predictions=predictions,
            circuit=request.circuit,
            conditions=simulation_params
        )
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/defaults/{circuit}")
async def get_circuit_defaults(circuit: str):
    # Comprehensive Circuit Data (Laps & Dates based on 2025 calendar)
    circuit_defaults = {
        'bahrain': {'laps': 57, 'date': '02 Mar 2025', 'weather_summary': 'Clear Night', 'air_temp': 26, 'track_temp': 32, 'rain_prob': 0, 'humidity': 45, 'tire': 'hard', 'pit_stops': 2, 'safety_car': 'low'},
        'jeddah': {'laps': 50, 'date': '09 Mar 2025', 'weather_summary': 'Hot & Humid', 'air_temp': 28, 'track_temp': 35, 'rain_prob': 0, 'humidity': 60, 'tire': 'medium', 'pit_stops': 1, 'safety_car': 'high'},
        'melbourne': {'laps': 58, 'date': '16 Mar 2025', 'weather_summary': 'Partly Cloudy', 'air_temp': 22, 'track_temp': 35, 'rain_prob': 10, 'humidity': 55, 'tire': 'soft', 'pit_stops': 2, 'safety_car': 'high'},
        'suzuka': {'laps': 53, 'date': '06 Apr 2025', 'weather_summary': 'Cool & Overcast', 'air_temp': 18, 'track_temp': 28, 'rain_prob': 30, 'humidity': 65, 'tire': 'hard', 'pit_stops': 2, 'safety_car': 'medium'},
        'shanghai': {'laps': 56, 'date': '23 Mar 2025', 'weather_summary': 'Hazy Sunshine', 'air_temp': 20, 'track_temp': 30, 'rain_prob': 40, 'humidity': 70, 'tire': 'medium', 'pit_stops': 2, 'safety_car': 'medium'},
        'miami': {'laps': 57, 'date': '04 May 2025', 'weather_summary': 'Sunny & Hot', 'air_temp': 29, 'track_temp': 45, 'rain_prob': 20, 'humidity': 60, 'tire': 'medium', 'pit_stops': 1, 'safety_car': 'medium'},
        'imola': {'laps': 63, 'date': '18 May 2025', 'weather_summary': 'Chance of Rain', 'air_temp': 22, 'track_temp': 35, 'rain_prob': 30, 'humidity': 60, 'tire': 'medium', 'pit_stops': 1, 'safety_car': 'high'},
        'monaco': {'laps': 78, 'date': '25 May 2025', 'weather_summary': 'Sunny Intervals', 'air_temp': 23, 'track_temp': 40, 'rain_prob': 10, 'humidity': 65, 'tire': 'soft', 'pit_stops': 1, 'safety_car': 'high'},
        'montreal': {'laps': 70, 'date': '15 Jun 2025', 'weather_summary': 'Windy', 'air_temp': 20, 'track_temp': 30, 'rain_prob': 40, 'humidity': 55, 'tire': 'medium', 'pit_stops': 2, 'safety_car': 'high'},
        'barcelona': {'laps': 66, 'date': '01 Jun 2025', 'weather_summary': 'Sunny', 'air_temp': 26, 'track_temp': 42, 'rain_prob': 5, 'humidity': 50, 'tire': 'hard', 'pit_stops': 2, 'safety_car': 'low'},
        'spielberg': {'laps': 71, 'date': '29 Jun 2025', 'weather_summary': 'Mountain Weather', 'air_temp': 24, 'track_temp': 40, 'rain_prob': 30, 'humidity': 50, 'tire': 'medium', 'pit_stops': 2, 'safety_car': 'medium'},
        'silverstone': {'laps': 52, 'date': '06 Jul 2025', 'weather_summary': 'Typical British Summer', 'air_temp': 19, 'track_temp': 30, 'rain_prob': 45, 'humidity': 70, 'tire': 'hard', 'pit_stops': 2, 'safety_car': 'medium'},
        'hungaroring': {'laps': 70, 'date': '03 Aug 2025', 'weather_summary': 'Scorching Heat', 'air_temp': 28, 'track_temp': 45, 'rain_prob': 20, 'humidity': 45, 'tire': 'medium', 'pit_stops': 2, 'safety_car': 'low'},
        'spa': {'laps': 44, 'date': '27 Jul 2025', 'weather_summary': 'Mixed Conditions', 'air_temp': 18, 'track_temp': 28, 'rain_prob': 45, 'humidity': 70, 'tire': 'medium', 'pit_stops': 2, 'safety_car': 'medium'},
        'zandvoort': {'laps': 72, 'date': '31 Aug 2025', 'weather_summary': 'Coastal Winds', 'air_temp': 19, 'track_temp': 30, 'rain_prob': 35, 'humidity': 75, 'tire': 'medium', 'pit_stops': 2, 'safety_car': 'low'},
        'monza': {'laps': 53, 'date': '07 Sep 2025', 'weather_summary': 'Warm & Dry', 'air_temp': 26, 'track_temp': 42, 'rain_prob': 15, 'humidity': 55, 'tire': 'medium', 'pit_stops': 1, 'safety_car': 'low'},
        'baku': {'laps': 51, 'date': '21 Sep 2025', 'weather_summary': 'Clear Skies', 'air_temp': 25, 'track_temp': 38, 'rain_prob': 10, 'humidity': 50, 'tire': 'medium', 'pit_stops': 2, 'safety_car': 'high'},
        'singapore': {'laps': 62, 'date': '05 Oct 2025', 'weather_summary': 'Tropical Heat', 'air_temp': 30, 'track_temp': 35, 'rain_prob': 60, 'humidity': 85, 'tire': 'soft', 'pit_stops': 2, 'safety_car': 'high'},
        'austin': {'laps': 56, 'date': '19 Oct 2025', 'weather_summary': 'Sunny', 'air_temp': 27, 'track_temp': 40, 'rain_prob': 10, 'humidity': 40, 'tire': 'medium', 'pit_stops': 2, 'safety_car': 'medium'},
        'mexico': {'laps': 71, 'date': '26 Oct 2025', 'weather_summary': 'High Altitude Sun', 'air_temp': 22, 'track_temp': 35, 'rain_prob': 15, 'humidity': 40, 'tire': 'soft', 'pit_stops': 2, 'safety_car': 'medium'},
        'interlagos': {'laps': 71, 'date': '09 Nov 2025', 'weather_summary': 'Unpredictable', 'air_temp': 24, 'track_temp': 40, 'rain_prob': 40, 'humidity': 60, 'tire': 'soft', 'pit_stops': 2, 'safety_car': 'high'},
        'vegas': {'laps': 50, 'date': '22 Nov 2025', 'weather_summary': 'Cold Desert Night', 'air_temp': 15, 'track_temp': 20, 'rain_prob': 0, 'humidity': 30, 'tire': 'medium', 'pit_stops': 1, 'safety_car': 'high'},
        'lusail': {'laps': 57, 'date': '30 Nov 2025', 'weather_summary': 'Warm Night', 'air_temp': 28, 'track_temp': 35, 'rain_prob': 0, 'humidity': 60, 'tire': 'hard', 'pit_stops': 3, 'safety_car': 'medium'},
        'abudhabi': {'laps': 58, 'date': '07 Dec 2025', 'weather_summary': 'Twilight Clear', 'air_temp': 25, 'track_temp': 32, 'rain_prob': 0, 'humidity': 50, 'tire': 'medium', 'pit_stops': 2, 'safety_car': 'low'}
    }
    
    circuit_key = circuit.lower()
    if 'saudi' in circuit_key: circuit_key = 'jeddah'
    if 'albert' in circuit_key: circuit_key = 'melbourne'
    if 'red bull' in circuit_key: circuit_key = 'spielberg'
    if 'mexico' in circuit_key: circuit_key = 'mexico'
    if 'brazil' in circuit_key: circuit_key = 'interlagos'
    
    defaults = circuit_defaults.get(circuit_key, {
        'laps': 55, 'date': 'TBD', 'weather_summary': 'Unknown',
        'air_temp': 25, 'track_temp': 35, 'rain_prob': 20, 'humidity': 50,
        'tire': 'medium', 'pit_stops': 2, 'safety_car': 'low'
    })
    
    # Try to fetch FORECAST weather (if race is upcoming)
    if defaults['date'] != 'TBD':
        forecast = fetch_forecast_weather(circuit_key, defaults['date'])
        if forecast:
            defaults.update(forecast)
        
    return defaults

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)