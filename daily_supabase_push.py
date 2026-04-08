import pandas as pd
import os
from datetime import datetime
from sqlalchemy import create_engine
import shutil

# === UPDATED SUPABASE CONNECTION (your password is already filled in) ===
DB_URL = "postgresql://postgres:!Lift1000o7@db.kffjahvpapxekbjfhinm.supabase.co:5432/postgres"
engine = create_engine(DB_URL)

os.makedirs("archive", exist_ok=True)

# Find the newest secured and debtors files
csv_files = [f for f in os.listdir('.') if f.lower().endswith('.csv')]
secured_file = max([f for f in csv_files if "secured" in f.lower()], key=os.path.getctime, default=None)
debtors_file = max([f for f in csv_files if "debtor" in f.lower()], key=os.path.getctime, default=None)

if not secured_file or not debtors_file:
    print("❌ Drop BOTH secureds_XXXXXX.csv and debtors_XXXXXX.csv (same date) in this folder!")
    exit()

print(f"✅ Processing {secured_file} + {debtors_file}")

df_sec = pd.read_csv(secured_file, sep="|", low_memory=False)
df_deb = pd.read_csv(debtors_file, sep="|", low_memory=False)

merged = pd.merge(df_sec, df_deb, on="Ucc1FilingNumber", how="left", suffixes=("_sec", "_deb"))

# === NEW: Automatically add source_file column ===
merged['source_file'] = secured_file

# Push to Supabase
merged.to_sql("ucc_filings", engine, if_exists="replace", index=False)
print(f"✅ Pushed {len(merged):,} filings to Supabase! (source_file column added)")

# Archive the CSVs
shutil.move(secured_file, f"archive/{secured_file}")
shutil.move(debtors_file, f"archive/{debtors_file}")
print("   CSVs archived")