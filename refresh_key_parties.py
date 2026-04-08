import sqlite3
from pathlib import Path

print("🔄 Updating key secured parties from file...")

file_path = Path("key_secured_parties.txt")
if not file_path.exists():
    print("❌ File 'key_secured_parties.txt' not found!")
    exit()

parties = [line.strip() for line in file_path.read_text().splitlines() if line.strip()]
if not parties:
    print("❌ No names found in key_secured_parties.txt")
    exit()

print(f"✅ Loaded {len(parties)} key secured parties")

conn = sqlite3.connect("ucc_secureds.db")

# Drop old view
conn.execute("DROP VIEW IF EXISTS ucc_filings_key")

# Build the list of names safely
names_list = "', '".join(parties)
sql = f"""
CREATE VIEW ucc_filings_key AS
SELECT * FROM ucc_filings
WHERE SecName IN ('{names_list}')
"""

conn.execute(sql)
conn.commit()
conn.close()

print("🎉 SUCCESS! Database VIEW updated.")
print(f"Your app now ONLY shows filings from these {len(parties)} institutions.")