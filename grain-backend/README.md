# Grain App — FastAPI Backend

Backend service that syncs customer data from a Google Sheet into SQL Server and serves it via REST API.

## Prerequisites

- **Python 3.9+**
- **SQL Server** with Windows Authentication (or configure SQL Auth in `.env`)
- **ODBC Driver 17** for SQL Server
- **Google Service Account** with Sheets API access

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database in SQL Server Management Studio
#    Run: CREATE DATABASE GrainAppDB

# 4. Place your Google service account credentials.json in this folder

# 5. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

| Method | Endpoint           | Description                         |
|--------|--------------------|-------------------------------------|
| GET    | `/customers`       | List all customers (with search)    |
| GET    | `/customers/{id}`  | Single customer detail              |
| GET    | `/columns`         | Column metadata from Row 4          |
| POST   | `/sync`            | Manually trigger sheet sync         |
| GET    | `/sync/logs`       | View sync history                   |
| GET    | `/health`          | Health check + stats                |
| GET    | `/docs`            | Swagger API docs (auto-generated)   |

## Configuration (.env)

```env
DATABASE_URL=mssql+pyodbc://localhost/GrainAppDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SHEET_TAB=Sheet2
HEADER_ROW=4
DATA_START_ROW=5
SYNC_INTERVAL_MINUTES=15
```

## Switching to PostgreSQL

Just change `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql://user:password@host:5432/grainapp
```
And install the driver: `pip install psycopg2-binary`

## Google Sheet Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable **Google Sheets API** and **Google Drive API**
3. Create a **Service Account** → Download JSON key as `credentials.json`
4. Share your Google Sheet with the service account email (as Viewer)
