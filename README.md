# DealerOS Reconciliation

A small Django + React application that imports two ledger CSVs and highlights disagreements while keeping organization data scoped by tenant.

## Stack
- Django + Django REST Framework-style JSON endpoints (plain Django views)
- SQLite
- React + Vite
- Python `Decimal` for money

## Requirements
- Python 3.11+
- Node.js 18+
- Git

## Run from a clean clone

### 1. Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py import_data
python manage.py runserver
```

### 2. Frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

### 3. Tests
```bash
cd backend
source .venv/bin/activate
pytest
```

## API
- `GET /api/orgs/`
- `GET /api/disagreements/?org=ORG-A`
- Optional: `reason=MISSING_IN_B`, `sort=value` or `sort=-value`

## What is implemented
- Imports every row from all CSV files and is idempotent.
- Keeps raw B references and values while storing cleaned values.
- Compares System B value to System A `total_value`.
- Detects missing, orphan, duplicate, value, location and date disagreements.
- Treats a multi-entry split as reconciled when its amounts sum exactly to A's total.
- Blank values are `NULL`, not zero.
- Organization filtering occurs in database queries before comparison.
- Frontend reason filter and value sort.

## Deliberate scope cuts
- No authentication: org selection is a demo control, not a production security boundary.
- No pagination, Docker, deployment, or extensive styling.
- No user/role management.

## Decisions
See `DECISIONS.md`.

## Agent reflection (edit these in your own words before submission)
### a. One thing the AI agent got wrong and how I noticed
Replace this with a real example from your own review/testing session. Do not claim an error you did not personally observe.

### b. Least confident part
I am least confident about the tenant boundary for cross-location records and the interpretation of VOIDED records. I would validate the intended business policy with the reviewer.

### c. If I had a second day
I would add authenticated organization membership and make the API derive the organization from the logged-in user instead of trusting the query parameter.
