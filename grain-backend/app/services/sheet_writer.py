"""
Service for writing data back to Google Sheets.
"""

import logging
from typing import Dict, Any

from app.config import get_settings
from app.services.sheet_reader import get_sheet_client, read_sheet_data

logger = logging.getLogger(__name__)

def update_customer_in_sheet(row_number: int, updates: Dict[str, Any]) -> dict:
    """
    Updates the customer directly in the Google Sheet.
    
    updates: A dictionary of { "Column Name": "New Value" }
    """
    settings = get_settings()
    
    # 1. Read current headers to map names to letters
    columns, _ = read_sheet_data()
    col_map = {c["column_name"]: c["column_letter"] for c in columns if c.get("column_letter")}
    
    # 2. Prepare the batch update payload for Google Sheets
    batch_data = []
    valid_updates = {}
    
    for col_name, new_val in updates.items():
        if col_name in col_map:
            col_letter = col_map[col_name]
            a1_range = f"{col_letter}{row_number}"
            # Values must be a 2D array: [[val]]
            batch_data.append({
                'range': a1_range,
                'values': [[str(new_val) if new_val is not None else ""]]
            })
            valid_updates[col_name] = new_val
        else:
            logger.warning(f"Column '{col_name}' not found in metadata. Skipping sheet update.")

    if not batch_data:
        raise ValueError("No valid columns to update.")

    # 3. Update the Google Sheet
    logger.info(f"Writing updates to sheet for row {row_number}: {valid_updates}")
    client = get_sheet_client()
    spreadsheet = client.open_by_key(settings.google_sheet_id)
    worksheet = spreadsheet.worksheet(settings.google_sheet_tab)
    
    # gspread batch_update uses the valueInputOption='USER_ENTERED' by default
    worksheet.batch_update(batch_data, value_input_option='USER_ENTERED')

    # 4. Return updated row by reading current sheet values
    refreshed_columns, refreshed_rows = read_sheet_data()
    for row in refreshed_rows:
        if row.get("_row_number") == row_number:
            updated_data = {k: v for k, v in row.items() if k != "_row_number"}
            updated_data["id"] = row_number
            updated_data["row_number"] = row_number
            return updated_data

    raise ValueError(f"Customer with row_number {row_number} not found in sheet.")
