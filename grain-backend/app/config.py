"""
Application settings — loaded from .env file.
To switch databases later (e.g. SQL Server → PostgreSQL), just change DATABASE_URL.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ─── Database ──────────────────────────────────────────
    database_url: str = "mssql+pyodbc://localhost/GrainAppDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

    # ─── Google Sheets ─────────────────────────────────────
    google_sheet_id: str = ""
    google_sheet_tab: str = "Sheet2"
    google_credentials_file: str = "credentials.json"
    header_row: int = 4       # Row containing column headers (1-indexed)
    data_start_row: int = 5   # First row of actual data (1-indexed)

    # ─── Sync Schedule ─────────────────────────────────────
    sync_interval_minutes: int = 15

    # ─── Server ────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
