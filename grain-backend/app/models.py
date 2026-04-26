"""
SQLAlchemy models — portable across SQL Server, PostgreSQL, SQLite.
Uses Text/JSON columns to support dynamic spreadsheet columns.
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Unicode, UnicodeText, func
)
from app.database import Base


class ColumnMetadata(Base):
    """Stores column header definitions from Row 4 of the Google Sheet."""
    __tablename__ = "columns_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    column_index = Column(Integer, nullable=False)          # 0-based position (A=0, B=1...)
    column_letter = Column(Unicode(5), nullable=True)       # Excel letter (A, B, ... AU)
    column_name = Column(Unicode(255), nullable=False)      # Header text or auto "Column 1"
    is_auto_named = Column(Boolean, default=False)          # True if header was blank
    bg_color = Column(Unicode(50), nullable=True)           # Hex color code from Google Sheets
    last_synced = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ColumnMetadata {self.column_letter}={self.column_name}>"


class Customer(Base):
    """Stores one row of customer data (Row 5+ from the Google Sheet).
    
    All dynamic column values are stored as a JSON string in the `data` field.
    This makes it flexible when sheet columns change.
    """
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    row_number = Column(Integer, nullable=False)             # Original sheet row number
    data = Column(UnicodeText, nullable=False)               # JSON string of {col_name: value}
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Customer row={self.row_number}>"


class SyncLog(Base):
    """Tracks sync history for monitoring."""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    synced_at = Column(DateTime, server_default=func.now())
    rows_synced = Column(Integer, default=0)
    columns_synced = Column(Integer, default=0)
    status = Column(Unicode(20), default="success")         # success / error
    message = Column(UnicodeText, nullable=True)
