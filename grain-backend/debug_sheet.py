"""Quick debug script to test Google Sheet access."""
import json
from google.oauth2.service_account import Credentials
import gspread

CREDS_FILE = "credentials.json"
SHEET_ID = "1zqxt1ztx9DYuWSRrMp7AOsgvl9-kKi1QGDdro0bVrgA"
TAB_NAME = "Sheet1"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

print("=" * 50)
print("GOOGLE SHEET DEBUG")
print("=" * 50)

# Step 1: Load credentials
print("\n1. Loading credentials.json...")
try:
    with open(CREDS_FILE) as f:
        cred_data = json.load(f)
    print(f"   ✅ Project ID: {cred_data.get('project_id')}")
    print(f"   ✅ Client Email: {cred_data.get('client_email')}")
    print(f"   ✅ Type: {cred_data.get('type')}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Step 2: Authenticate
print("\n2. Authenticating with Google...")
try:
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    print("   ✅ Authentication successful")
except Exception as e:
    print(f"   ❌ Auth failed: {e}")
    exit(1)

# Step 3: Try to open the sheet
print(f"\n3. Opening sheet ID: {SHEET_ID}...")
try:
    spreadsheet = client.open_by_key(SHEET_ID)
    print(f"   ✅ Sheet opened: '{spreadsheet.title}'")
except gspread.exceptions.APIError as e:
    error_info = e.args[0] if e.args else {}
    code = error_info.get('code', 'unknown')
    message = error_info.get('message', str(e))
    print(f"   ❌ API Error (code {code}): {message}")
    if code == 403:
        print(f"\n   FIX: Share the sheet with this email:")
        print(f"   {cred_data.get('client_email')}")
        print(f"\n   Also check that Google Sheets API & Drive API are enabled")
        print(f"   in project: {cred_data.get('project_id')}")
    exit(1)
except PermissionError as e:
    print(f"   ❌ Permission denied!")
    print(f"\n   FIX: Share the sheet with: {cred_data.get('client_email')}")
    print(f"   Also check APIs are enabled in project: {cred_data.get('project_id')}")
    exit(1)
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")
    exit(1)

# Step 4: Try to access the tab
print(f"\n4. Accessing tab '{TAB_NAME}'...")
try:
    worksheet = spreadsheet.worksheet(TAB_NAME)
    print(f"   ✅ Tab found: '{worksheet.title}' ({worksheet.row_count} rows x {worksheet.col_count} cols)")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"   Available tabs: {[ws.title for ws in spreadsheet.worksheets()]}")
    exit(1)

# Step 5: Read Row 4 (headers)
print(f"\n5. Reading Row 4 (headers)...")
try:
    row4 = worksheet.row_values(4)
    print(f"   ✅ Found {len(row4)} columns in Row 4")
    print(f"   First 10 headers: {row4[:10]}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Step 6: Read a data row
print(f"\n6. Reading Row 5 (first data row)...")
try:
    row5 = worksheet.row_values(5)
    print(f"   ✅ Found {len(row5)} values in Row 5")
    print(f"   First 5 values: {row5[:5]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print(f"\n{'=' * 50}")
print("ALL CHECKS PASSED! ✅ Sheet access is working.")
print(f"{'=' * 50}")
