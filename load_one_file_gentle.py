import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import sys
import time

if len(sys.argv) < 2:
    print("Usage: python3 load_one_file_gentle.py <filename>")
    sys.exit(1)

file_path = sys.argv[1]
filename = file_path.split('/')[-1]

print(f"🚀 Loading ONE file (GENTLE mode): {filename}")
print("→ 2,000-row chunks + 1.2 second pause")

DB_URL = "postgresql://postgres.kffjahvpapxekbjfhinm:!Lift1000o7@aws-1-us-east-2.pooler.supabase.com:5432/postgres"

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

if "debtors_full" in filename:
    target_table = "debtor_filings"
else:
    target_table = "secured_filings"

print(f"→ Target table: {target_table}")

chunks = pd.read_csv(file_path, sep="|", on_bad_lines="skip", low_memory=False, chunksize=2000)

total = 0
for chunk in chunks:
    chunk["source_file"] = filename
    
    raw_columns = [
        "Ucc1FilingNumber", "DebName", "DebNameFormat", "DebAddressLine1", "DebAddressLine2",
        "DebCity", "DebState", "DebZipCode", "DebCountry", "DebRefNumber",
        "SecName", "SecNameFormat", "SecAddressLine1", "SecAddressLine2", "SecCity",
        "SecStateProvince", "SecZipCode", "SecCountry", "SecRefNumber", "source_file"
    ]
    columns = [col for col in raw_columns if col in chunk.columns]
    quoted_columns = [f'"{col}"' for col in columns]
    
    data = [tuple(row) for row in chunk[columns].values]
    
    insert_sql = f"""
        INSERT INTO {target_table} ({", ".join(quoted_columns)})
        VALUES %s
    """
    execute_values(cur, insert_sql, data, page_size=1000)
    conn.commit()
    
    total += len(chunk)
    print(f"   → {total:,} records added from this chunk")
    
    time.sleep(1.2)   # gentle pause

print(f"\n✅ Finished loading {filename} — {total:,} records added")
cur.close()
conn.close()
