# Grain App

This project now runs in **Google Sheets-only mode**.

- No SQL database is required to start the backend.
- Backend reads and writes customer data directly from Google Sheets.

## Project Structure

- `grain-backend/` -> FastAPI backend
- `grain-app/` -> Expo React Native frontend

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- Google Service Account JSON (`credentials.json`)

## Backend Setup (Google Sheets-Only)

Run from repo root:

```bash
cd grain-backend

# Create venv (first time only)
python -m venv ..\.venv

# Activate venv (Windows PowerShell)
..\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

Create/update `.env` in `grain-backend/`:

```env
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SHEET_TAB=Sheet1
GOOGLE_CREDENTIALS_FILE=credentials.json
HEADER_ROW=3
DATA_START_ROW=5
HOST=0.0.0.0
PORT=8000
```

Place `credentials.json` inside `grain-backend/`.

Start backend:

```bash
cd grain-backend
..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Check:

- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Frontend Setup (Expo)

In a new terminal:

```bash
cd grain-app
npm install
npm start
```

From Expo terminal:

- Press `w` for web
- Press `a` for Android emulator

## Frontend API Base URL

`grain-app/src/services/api.js` is configured as:

- Web -> `http://localhost:8000`
- Android emulator -> `http://10.0.2.2:8000`
- iOS simulator -> `http://localhost:8000`

For a physical device, replace host with your machine LAN IP.

## Start Both Services (Quick Commands)

Terminal 1 (backend):

```bash
cd grain-backend
..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (frontend):

```bash
cd grain-app
npm start
```

## Stop Services

- In each running terminal, press `Ctrl + C`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/customers` | List customers with optional search |
| GET | `/customers/{row_number}` | Get one customer by sheet row number |
| PATCH | `/customers/{row_number}` | Update selected fields in Google Sheet |
| GET | `/columns` | Get column metadata |
| POST | `/sync` | Validate/reload data from Google Sheet |
| GET | `/sync/logs` | Recent in-memory sync checks |
| GET | `/health` | Service and Google Sheet health |
