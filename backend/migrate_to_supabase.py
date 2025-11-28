import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# 1. Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
CSV_PATH = "../data/f1_race_data_unified_v5.csv"

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL must be set in .env")
    print("Example: postgresql://postgres:password@db.supabase.co:5432/postgres")
    exit(1)

# 2. Initialize DB Connection
try:
    engine = create_engine(DATABASE_URL)
    print("✅ Connected to Database")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    exit(1)

def migrate_data():
    print(f"📂 Reading data from {CSV_PATH}...")
    try:
        df = pd.read_csv(CSV_PATH)
        
        # Clean column names (Postgres doesn't like spaces or special chars usually, but pandas handles quoting)
        # We'll ensure they are lower case for consistency
        df.columns = [c.lower().replace(' ', '_') for c in df.columns]
        
        total_records = len(df)
        print(f"📊 Found {total_records} rows with {len(df.columns)} columns.")

        print("🚀 Uploading data (Creating table 'race_data')...")
        
        # if_exists='replace' will DROP the table and CREATE it with correct columns
        df.to_sql('race_data', engine, if_exists='replace', index=False, method='multi', chunksize=500)
            
        print("✅ Migration Complete! Table 'race_data' created and populated.")
        
    except Exception as e:
        print(f"❌ Migration Failed: {e}")

if __name__ == "__main__":
    print("ℹ️  Starting Migration...")
    migrate_data()
