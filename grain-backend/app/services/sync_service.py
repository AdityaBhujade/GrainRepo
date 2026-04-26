"""
Sync service — orchestrates data flow from Google Sheet → SQL Server.

Called by the cron job scheduler and the manual /sync endpoint.
"""

import json
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import ColumnMetadata, Customer, SyncLog
from app.services.sheet_reader import read_sheet_data

logger = logging.getLogger(__name__)


def sync_sheet_to_db(db: Session) -> dict:
    """
    Full sync: read Google Sheet → update columns_metadata → update customers.
    
    Returns summary dict with status, row/column counts, and any error message.
    """
    try:
        logger.info("Starting sheet → DB sync...")

        # ── Step 1: Read from Google Sheet ─────────────────────
        columns, rows = read_sheet_data()

        if not columns:
            msg = "No columns found in sheet — sync aborted"
            logger.warning(msg)
            _log_sync(db, 0, 0, "error", msg)
            return {"status": "error", "message": msg, "rows_synced": 0, "columns_synced": 0}

        # ── Step 2: Update column metadata ─────────────────────
        # Clear existing column metadata and replace with fresh data
        db.query(ColumnMetadata).delete()

        for col in columns:
            db.add(ColumnMetadata(
                column_index=col["column_index"],
                column_letter=col["column_letter"],
                column_name=col["column_name"],
                is_auto_named=col["is_auto_named"],
                bg_color=col.get("bg_color"),
            ))

        logger.info(f"Updated {len(columns)} column definitions")

        # ── Step 3: Update customer data ───────────────────────
        # Clear existing customer rows and replace with fresh data
        db.query(Customer).delete()

        for row_data in rows:
            row_number = row_data.pop("_row_number", 0)
            db.add(Customer(
                row_number=row_number,
                data=json.dumps(row_data, ensure_ascii=False),
            ))

        logger.info(f"Updated {len(rows)} customer rows")

        # ── Step 4: Log the sync ───────────────────────────────
        _log_sync(db, len(rows), len(columns), "success", "Sync completed successfully")

        db.commit()

        result = {
            "status": "success",
            "message": f"Synced {len(rows)} rows with {len(columns)} columns",
            "rows_synced": len(rows),
            "columns_synced": len(columns),
        }
        logger.info(result["message"])
        return result

    except Exception as e:
        db.rollback()
        error_msg = f"Sync failed: {str(e)}"
        logger.error(error_msg, exc_info=True)

        try:
            _log_sync(db, 0, 0, "error", error_msg)
            db.commit()
        except Exception:
            pass  # Don't fail the error handler

        return {
            "status": "error",
            "message": error_msg,
            "rows_synced": 0,
            "columns_synced": 0,
        }


def _log_sync(db: Session, rows: int, cols: int, status: str, message: str):
    """Write a sync log entry."""
    db.add(SyncLog(
        rows_synced=rows,
        columns_synced=cols,
        status=status,
        message=message,
    ))
