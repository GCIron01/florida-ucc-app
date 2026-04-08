import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
import glob
import time
from datetime import datetime

print("🚀 DAILY GENTLE PUSH (secured + debtors)")
print("→ Appends new filings only — safe for historical data\n")

# === CONFIG ===
DB_URL = "postgresql://postgres.kffjahvpapxekbjfhinm:!Lift1000o7@aws-1-us-east-2.pooler.supabase.com:5432/postgres"
CHUNK_SIZE = 2000
SLEEP_BETWEEN_CHUNKS = 1.2
# ==============

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# Find the newest secured and debtors files
secured_file = max(glob.glob("secureds_*.csv"), key=os.path.getctime, default=None)
debtors_file = max(glob.glob("debtors_*.csv"), key=os.path.getctime, default=None)

if not secured_file or not debtors_file:
    print("❌ Please drop BOTH secureds_XXXX.csv and debtors_XXXX.csv into this folder first!")
    exit()

print(f"✅ Found: {secured_file} + {debtors_file}\n")

def load_file(file_path, table_name):
    filename = os.path.basename(file_path)
    print(f"📂 Loading {filename} → {table_name}")
    
    chunks = pd.read_csv(file_path, sep="|", on_bad_lines="skip", low_memory=False, chunksize=CHUNK_SIZE)
    total_added = 0
    
    for i, chunk in enumerate(chunks):
        chunk["source_file"] = filename
        
        columns = [col for col in chunk.columns if col in [
            "Ucc1FilingNumber", "DebName", "DebNameFormat", "DebAddressLine1", "DebAddressLine2",
            "DebCity", "DebState", "DebZipCode", "DebCountry", "DebRefNumber",
            "SecName", "SecNameFormat", "SecAddressLine1", "SecAddressLine2", "SecCity",
            "SecStateProvince", "SecZipCode", "SecCountry", "SecRefNumber", "source_file"
        ]]
        
        data = [tuple(row) for row in chunk[columns].values]
        
        insert_sql = f"""
            INSERT INTO {table_name} ({", ".join(columns)})
            VALUES %s
            ON CONFLICT (Ucc1FilingNumber) DO NOTHING
        """
        
        execute_values(cur, insert_sql, data, page_size=800)
        conn.commit()
        
        added = len(chunk)
        total_added += added
        print(f"   Chunk {i+1}: {added:,} rows added | Total: {total_added:,}")
        time.sleep(SLEEP_BETWEEN_CHUNKS)
    
    print(f"✅ Finished {filename} — {total_added:,} rows added to {table_name}\n")
    return filename

# Load both files
load_file(secured_file, "secured_filings")
load_file(debtors_file, "debtor_filings")

# Archive
os.makedirs("archive", exist_ok=True)
os.rename(secured_file, f"archive/{secured_file}")
os.rename(debtors_file, f"archive/{debtors_file}")
print("📦 Both CSVs moved to archive/ folder")

print("\n🎉 DAILY PUSH COMPLETE — Supabase is now up-to-date!")
cur.close()
conn.close()
