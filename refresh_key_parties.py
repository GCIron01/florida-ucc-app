import sqlite3
from pathlib import Path

print("🔄 Updating key secured parties from file...")

# Read the list
file_path = Path("key_secured_parties.txt")
if not file_path.exists():
    print("❌ File 'key_secured_parties.txt' not found!")
    exit()

parties = [line.strip() for line in file_path.read_text().splitlines() if line.strip()]
if not parties:
    print("❌ No names found in key_secured_parties.txt")
    exit()

print(f"✅ Loaded {len(parties)} key secured parties")

# Connect and recreate the VIEW
conn = sqlite3.connect("ucc_secureds.db")

sql = f"""
DROP VIEW IF EXISTS ucc_filings_key;
CREATE VIEW ucc_filings_key AS
SELECT * FROM ucc_filings
WHERE SecName IN ({','.join(['?'] * len(parties))})
"""

conn.execute(sql, parties)
conn.commit()
conn.close()

print("🎉 SUCCESS! Database VIEW updated.")
print("Your app now only shows filings from these key secured parties.")