"""
Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


# ─── Column Metadata ─────────────────────────────────────────

class ColumnSchema(BaseModel):
    column_index: int
    column_letter: Optional[str] = None
    column_name: str
    is_auto_named: bool = False

    class Config:
        from_attributes = True


class ColumnsResponse(BaseModel):
    total: int
    columns: List[ColumnSchema]


# ─── Customer ────────────────────────────────────────────────

class CustomerSchema(BaseModel):
    id: int
    row_number: int
    data: Dict[str, Any]

    class Config:
        from_attributes = True


class CustomersListResponse(BaseModel):
    total: int
    columns: List[str]
    data: List[Dict[str, Any]]


class CustomerDetailResponse(BaseModel):
    columns: List[str]
    customer: Dict[str, Any]


# ─── Sync ─────────────────────────────────────────────────────

class SyncResponse(BaseModel):
    status: str
    message: str
    rows_synced: int = 0
    columns_synced: int = 0


class SyncLogSchema(BaseModel):
    id: int
    synced_at: datetime
    rows_synced: int
    columns_synced: int
    status: str
    message: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Health ───────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    database: str
    last_sync: Optional[datetime] = None
    total_customers: int = 0
    total_columns: int = 0
