import psycopg2
from datetime import datetime

# === FIXED CONNECTION STRING ===
DB_URL = "postgresql://postgres.kffjahvpapxekbjfhinm:%21Lift1000o7@aws-1-us-east-2.pooler.supabase.com:5432/postgres"

print(f"🧹 Starting cleanup of construction_equipment_filings at {datetime.now()}")

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# Step 1: Create a clean version (keep only ONE row per Ucc1FilingNumber)
print("   Creating clean table (deduplicating on Ucc1FilingNumber)...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS construction_equipment_filings_new AS
    SELECT DISTINCT ON ("Ucc1FilingNumber") *
    FROM construction_equipment_filings
    ORDER BY "Ucc1FilingNumber";
""")

# Step 2: Drop the old table/view (handles both cases)
print("   Dropping old duplicate table/view...")
cur.execute("DROP TABLE IF EXISTS construction_equipment_filings;")
cur.execute("DROP VIEW IF EXISTS construction_equipment_filings;")

# Step 3: Rename the clean table
print("   Renaming clean table to original name...")
cur.execute("ALTER TABLE construction_equipment_filings_new RENAME TO construction_equipment_filings;")

# Step 4: Add index for fast app loading
print("   Adding index for fast app loading...")
cur.execute('CREATE INDEX IF NOT EXISTS idx_construction_ucc ON construction_equipment_filings ("Ucc1FilingNumber");')

conn.commit()
cur.close()
conn.close()

print("🎉 Cleanup COMPLETE! Duplicates removed.")
print("   The construction_equipment_filings table is now clean and ready for the app.")
print(f"   Finished at {datetime.now()}")
