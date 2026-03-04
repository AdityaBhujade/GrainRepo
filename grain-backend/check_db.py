"""Quick diagnostic: check what columns and customer data are in the DB."""
import pyodbc
import json

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=GrainAppDB;"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()

# 1) Check column metadata
print("=" * 60)
print("COLUMNS IN DB (columns_metadata table)")
print("=" * 60)
cursor.execute("SELECT column_index, column_letter, column_name, is_auto_named FROM columns_metadata ORDER BY column_index")
cols = cursor.fetchall()
print(f"Total columns: {len(cols)}")
for c in cols:
    auto = " [AUTO]" if c[3] else ""
    print(f"  [{c[0]:2d}] {c[1]:>3s} = '{c[2]}'{auto}")

# 2) Check a sample customer
print("\n" + "=" * 60)
print("FIRST CUSTOMER DATA (customers table)")
print("=" * 60)
cursor.execute("SELECT TOP 1 id, row_number, data FROM customers ORDER BY row_number")
row = cursor.fetchone()
if row:
    print(f"ID: {row[0]}, Row: {row[1]}")
    data = json.loads(row[2])
    for key, val in data.items():
        display_val = str(val)[:60] if val else "NULL"
        print(f"  '{key}' = {display_val}")
else:
    print("  NO CUSTOMERS FOUND!")

# 3) Total count
cursor.execute("SELECT COUNT(*) FROM customers")
total = cursor.fetchone()[0]
print(f"\nTotal customers in DB: {total}")

# 4) Check specific columns
print("\n" + "=" * 60)
print("CHECKING TARGET COLUMNS")
print("=" * 60)
target_cols = ['कार्ड धारकांचे नाव', 'ब आहेर मारते']
for tc in target_cols:
    cursor.execute("SELECT COUNT(*) FROM columns_metadata WHERE column_name = ?", (tc,))
    count = cursor.fetchone()[0]
    print(f"  Column '{tc}': {'FOUND' if count > 0 else 'NOT FOUND'} in metadata")

# 5) Check if data JSON contains these keys
cursor.execute("SELECT TOP 1 data FROM customers ORDER BY row_number")
row = cursor.fetchone()
if row:
    data = json.loads(row[0])
    for tc in target_cols:
        if tc in data:
            print(f"  Key '{tc}' in customer data: '{data[tc]}'")
        else:
            # Check for similar keys
            similar = [k for k in data.keys() if any(part in k for part in tc.split())]
            if similar:
                print(f"  Key '{tc}' NOT FOUND, but similar: {similar}")
            else:
                print(f"  Key '{tc}' NOT FOUND in customer data")

conn.close()
