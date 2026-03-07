"""
Google Sheet reader service.

Reads column headers from a configurable header row (default: Row 4)
and data from rows below it. Auto-names blank columns as "Column 1", "Column 2", etc.
"""

import logging
from typing import List, Dict, Any, Tuple

import gspread
from google.oauth2.service_account import Credentials

from app.config import get_settings

logger = logging.getLogger(__name__)

# Google Sheets API scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _col_index_to_letter(index: int) -> str:
    """Convert 0-based column index to Excel-style letter (0→A, 25→Z, 26→AA)."""
    result = ""
    idx = index
    while True:
        result = chr(idx % 26 + ord("A")) + result
        idx = idx // 26 - 1
        if idx < 0:
            break
    return result


# ─── Rename auto-named columns to meaningful names ──────────
# Add entries here to rename any auto-named "Column N" to a friendly name.
COLUMN_RENAMES = {
    "Column 20": "Mobile Number",
}


def _build_column_headers(raw_headers: List[str]) -> List[Dict[str, Any]]:
    """
    Process raw header values from Row 4.
    - Blank/empty headers → auto-named as "Column 1", "Column 2", etc.
    - Auto-named columns are then checked against COLUMN_RENAMES for friendly names.
    - Returns list of dicts with: column_index, column_letter, column_name, is_auto_named
    """
    columns = []
    auto_counter = 1

    for i, header in enumerate(raw_headers):
        header_clean = str(header).strip() if header is not None else ""

        if header_clean == "" or header_clean == "None":
            col_name = f"Column {auto_counter}"
            auto_counter += 1
            is_auto = True
            # Apply friendly rename if configured
            if col_name in COLUMN_RENAMES:
                col_name = COLUMN_RENAMES[col_name]
        else:
            col_name = header_clean
            is_auto = False

        columns.append({
            "column_index": i,
            "column_letter": _col_index_to_letter(i),
            "column_name": col_name,
            "is_auto_named": is_auto,
        })

    return columns


def get_sheet_client():
    """Create an authenticated gspread client using service account."""
    settings = get_settings()
    creds = Credentials.from_service_account_file(
        settings.google_credentials_file,
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def read_sheet_data() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Read the Google Sheet and return (columns, rows).
    
    Returns:
        columns: List of column metadata dicts from Row 4
        rows: List of dicts, each mapping column_name → cell value (Row 5+)
    """
    settings = get_settings()
    logger.info(f"Reading sheet {settings.google_sheet_id}, tab '{settings.google_sheet_tab}'")

    client = get_sheet_client()
    spreadsheet = client.open_by_key(settings.google_sheet_id)
    worksheet = spreadsheet.worksheet(settings.google_sheet_tab)

    # Get all values (returns list of lists)
    all_values = worksheet.get_all_values()

    if len(all_values) < settings.header_row:
        logger.warning(f"Sheet has fewer than {settings.header_row} rows — no headers found")
        return [], []

    # ── Extract headers from the configured row (1-indexed → 0-indexed)
    raw_headers = all_values[settings.header_row - 1]
    columns = _build_column_headers(raw_headers)
    col_names = [c["column_name"] for c in columns]

    logger.info(f"Found {len(columns)} columns from Row {settings.header_row}")

    # ── Extract data rows (from data_start_row onwards)
    data_rows = all_values[settings.data_start_row - 1:]
    rows = []

    for row_idx, row_values in enumerate(data_rows):
        row_data = {}
        for col_idx, col_name in enumerate(col_names):
            if col_idx < len(row_values):
                value = row_values[col_idx]
                # Convert empty strings to None for cleaner data
                row_data[col_name] = value if value != "" else None
            else:
                row_data[col_name] = None

        # Add the original row number (1-indexed, accounting for header offset)
        row_data["_row_number"] = settings.data_start_row + row_idx

        rows.append(row_data)

    logger.info(f"Read {len(rows)} data rows (Row {settings.data_start_row} onwards)")
    return columns, rows
