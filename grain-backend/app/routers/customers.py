"""
Customer & Column API endpoints.
"""

import json
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import Customer, ColumnMetadata, SyncLog
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
from app.services.sync_service import sync_sheet_to_db
from app.services.sheet_writer import update_customer_in_sheet

logger = logging.getLogger(__name__)

router = APIRouter()


# ─── GET /customers ──────────────────────────────────────────

@router.get("/customers", response_model=CustomersListResponse)
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(2000, ge=1, le=5000),
    search: Optional[str] = Query(None, description="Search across all columns"),
    db: Session = Depends(get_db),
):
    """List all customers with their dynamic column data."""
    columns_db = db.query(ColumnMetadata).order_by(ColumnMetadata.column_index).all()
    col_schemas = [ColumnSchema.model_validate(c) for c in columns_db]

    # Query customers
    query = db.query(Customer).order_by(Customer.row_number)

    # Optional search — filter rows where any column value contains the search term
    if search:
        search_lower = search.lower()
        all_customers = query.all()
        filtered = []
        for cust in all_customers:
            data = json.loads(cust.data)
            if any(
                search_lower in str(v).lower()
                for v in data.values()
                if v is not None
            ):
                filtered.append(cust)
        total = len(filtered)
        # Manual pagination
        start = (page - 1) * page_size
        paginated = filtered[start : start + page_size]
    else:
        total = query.count()
        paginated = query.offset((page - 1) * page_size).limit(page_size).all()

    # Build response data
    data = []
    for cust in paginated:
        row = json.loads(cust.data)
        row["id"] = cust.id
        row["row_number"] = cust.row_number
        data.append(row)

    return CustomersListResponse(total=total, columns=col_schemas, data=data)


# ─── GET /customers/{id} ────────────────────────────────────

@router.get("/customers/{row_number}", response_model=CustomerDetailResponse)
def get_customer(row_number: int, db: Session = Depends(get_db)):
    """Get a single customer by row_number (stable across syncs)."""
    customer = db.query(Customer).filter(Customer.row_number == row_number).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get column metadata
    columns_db = db.query(ColumnMetadata).order_by(ColumnMetadata.column_index).all()
    col_schemas = [ColumnSchema.model_validate(c) for c in columns_db]

    # Parse customer data
    data = json.loads(customer.data)
    data["id"] = customer.id
    data["row_number"] = customer.row_number

    return CustomerDetailResponse(columns=col_schemas, customer=data)


# ─── PATCH /customers/{row_number} ──────────────────────────

@router.patch("/customers/{row_number}", response_model=CustomerDetailResponse)
def update_customer(row_number: int, request: CustomerUpdateRequest, db: Session = Depends(get_db)):
    """Update a customer's specific fields in Google Sheets and local DB."""
    try:
        updated_data = update_customer_in_sheet(db, row_number, request.updates)
        
        # Get column metadata for response
        columns_db = db.query(ColumnMetadata).order_by(ColumnMetadata.column_index).all()
        col_schemas = [ColumnSchema.model_validate(c) for c in columns_db]
        
        return CustomerDetailResponse(columns=col_schemas, customer=updated_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update customer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while updating sheet.")


# ─── GET /columns ────────────────────────────────────────────

@router.get("/columns", response_model=ColumnsResponse)
def get_columns(db: Session = Depends(get_db)):
    """Get all column metadata from the spreadsheet."""
    columns = db.query(ColumnMetadata).order_by(ColumnMetadata.column_index).all()
    return ColumnsResponse(
        total=len(columns),
        columns=[ColumnSchema.model_validate(c) for c in columns],
    )


# ─── POST /sync ─────────────────────────────────────────────

@router.post("/sync", response_model=SyncResponse)
def manual_sync(db: Session = Depends(get_db)):
    """Manually trigger a Google Sheet → DB sync."""
    result = sync_sheet_to_db(db)
    return SyncResponse(**result)


# ─── GET /sync/logs ──────────────────────────────────────────

@router.get("/sync/logs", response_model=List[SyncLogSchema])
def get_sync_logs(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get recent sync log entries."""
    logs = (
        db.query(SyncLog)
        .order_by(desc(SyncLog.synced_at))
        .limit(limit)
        .all()
    )
    return [SyncLogSchema.model_validate(log) for log in logs]


# ─── GET /health ─────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check with database status."""
    try:
        total_customers = db.query(Customer).count()
        total_columns = db.query(ColumnMetadata).count()
        last_sync_log = (
            db.query(SyncLog)
            .order_by(desc(SyncLog.synced_at))
            .first()
        )

        return HealthResponse(
            status="healthy",
            database="connected",
            last_sync=last_sync_log.synced_at if last_sync_log else None,
            total_customers=total_customers,
            total_columns=total_columns,
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            database=f"error: {str(e)}",
        )
