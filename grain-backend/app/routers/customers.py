"""
Customer & Column API endpoints.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas import (
    CustomersListResponse,
    CustomerDetailResponse,
    CustomerUpdateRequest,
    ColumnsResponse,
    ColumnSchema,
    SyncResponse,
    HealthResponse,
    SyncLogSchema,
)
from app.services.sheet_reader import read_sheet_data
from app.services.sheet_writer import update_customer_in_sheet

logger = logging.getLogger(__name__)

router = APIRouter()

_sync_logs: List[SyncLogSchema] = []
_last_sync: Optional[datetime] = None


def _record_sync(status: str, message: str, rows_synced: int, columns_synced: int) -> None:
    global _last_sync
    now = datetime.utcnow()
    _last_sync = now
    _sync_logs.insert(
        0,
        SyncLogSchema(
            id=len(_sync_logs) + 1,
            synced_at=now,
            rows_synced=rows_synced,
            columns_synced=columns_synced,
            status=status,
            message=message,
        ),
    )
    if len(_sync_logs) > 100:
        _sync_logs.pop()


# ─── GET /customers ──────────────────────────────────────────

@router.get("/customers", response_model=CustomersListResponse)
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(2000, ge=1, le=5000),
    search: Optional[str] = Query(None, description="Search across all columns"),
):
    """List all customers directly from Google Sheets."""
    columns, rows = read_sheet_data()
    col_schemas = [ColumnSchema.model_validate(c) for c in columns]

    filtered_rows = rows
    if search:
        search_lower = search.lower()
        filtered_rows = []
        for row in rows:
            if any(
                search_lower in str(v).lower()
                for k, v in row.items()
                if k != "_row_number"
                if v is not None
            ):
                filtered_rows.append(row)

    total = len(filtered_rows)
    start = (page - 1) * page_size
    paginated = filtered_rows[start : start + page_size]

    data = []
    for row in paginated:
        row_number = row.get("_row_number")
        payload = {k: v for k, v in row.items() if k != "_row_number"}
        payload["id"] = row_number
        payload["row_number"] = row_number
        data.append(payload)

    return CustomersListResponse(total=total, columns=col_schemas, data=data)


# ─── GET /customers/{id} ────────────────────────────────────

@router.get("/customers/{row_number}", response_model=CustomerDetailResponse)
def get_customer(row_number: int):
    """Get a single customer by row_number from Google Sheets."""
    columns, rows = read_sheet_data()
    col_schemas = [ColumnSchema.model_validate(c) for c in columns]

    for row in rows:
        if row.get("_row_number") == row_number:
            payload = {k: v for k, v in row.items() if k != "_row_number"}
            payload["id"] = row_number
            payload["row_number"] = row_number
            return CustomerDetailResponse(columns=col_schemas, customer=payload)

    raise HTTPException(status_code=404, detail="Customer not found")


# ─── PATCH /customers/{row_number} ──────────────────────────

@router.patch("/customers/{row_number}", response_model=CustomerDetailResponse)
def update_customer(row_number: int, request: CustomerUpdateRequest):
    """Update a customer's specific fields directly in Google Sheets."""
    try:
        updated_data = update_customer_in_sheet(row_number, request.updates)
        columns, _ = read_sheet_data()
        col_schemas = [ColumnSchema.model_validate(c) for c in columns]
        return CustomerDetailResponse(columns=col_schemas, customer=updated_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update customer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while updating sheet.")


# ─── GET /columns ────────────────────────────────────────────

@router.get("/columns", response_model=ColumnsResponse)
def get_columns():
    """Get all column metadata from the spreadsheet."""
    columns, _ = read_sheet_data()
    return ColumnsResponse(
        total=len(columns),
        columns=[ColumnSchema.model_validate(c) for c in columns],
    )


# ─── POST /sync ─────────────────────────────────────────────

@router.post("/sync", response_model=SyncResponse)
def manual_sync():
    """Validate current Google Sheet accessibility and shape."""
    try:
        columns, rows = read_sheet_data()
        message = f"Loaded {len(rows)} rows with {len(columns)} columns from Google Sheets"
        _record_sync("success", message, len(rows), len(columns))
        return SyncResponse(
            status="success",
            message=message,
            rows_synced=len(rows),
            columns_synced=len(columns),
        )
    except Exception as e:
        message = f"Sheet load failed: {str(e)}"
        _record_sync("error", message, 0, 0)
        return SyncResponse(
            status="error",
            message=message,
            rows_synced=0,
            columns_synced=0,
        )


# ─── GET /sync/logs ──────────────────────────────────────────

@router.get("/sync/logs", response_model=List[SyncLogSchema])
def get_sync_logs(
    limit: int = Query(10, ge=1, le=50),
):
    """Get recent in-memory sheet sync checks."""
    return _sync_logs[:limit]


# ─── GET /health ─────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check for Google Sheets mode (no database)."""
    try:
        columns, rows = read_sheet_data()

        return HealthResponse(
            status="healthy",
            database="disabled_google_sheet_mode",
            last_sync=_last_sync,
            total_customers=len(rows),
            total_columns=len(columns),
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            database=f"sheet_error: {str(e)}",
        )
