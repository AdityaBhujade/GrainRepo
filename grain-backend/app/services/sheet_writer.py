"""
Service for writing data back to Google Sheets and the local DB.
"""

import json
import logging
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import ColumnMetadata, Customer
from app.services.sheet_reader import get_sheet_client

logger = logging.getLogger(__name__)

def update_customer_in_sheet(db: Session, row_number: int, updates: Dict[str, Any]) -> dict:
    """
    Updates the customer in the Google Sheet and the local database.
    
    updates: A dictionary of { "Column Name": "New Value" }
    """
    settings = get_settings()
    
    # 1. Fetch column metadata to map names to letters
    columns_db = db.query(ColumnMetadata).all()
    col_map = {c.column_name: c.column_letter for c in columns_db if c.column_letter}
    
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
    
    # 4. Update the local database
    customer = db.query(Customer).filter(Customer.row_number == row_number).first()
    if customer:
        current_data = json.loads(customer.data)
        # Apply updates
        for k, v in valid_updates.items():
            current_data[k] = v
        # Save back to DB
        customer.data = json.dumps(current_data, ensure_ascii=False)
        db.commit()
        db.refresh(customer)
        
        updated_data = json.loads(customer.data)
        updated_data["id"] = customer.id
        updated_data["row_number"] = customer.row_number
        return updated_data
    else:
        raise ValueError(f"Customer with row_number {row_number} not found in database.")
