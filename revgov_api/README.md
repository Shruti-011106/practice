# RevGov Governance Tracker — Backend API

Complete FastAPI backend for the EGT RevGov portal.

## Modules & Endpoints (all under `/api/v1`)

| Module | Endpoints |
|---|---|
| **HR** | `/employees`, `/learning-trackers`, `/linkedin-trackers`, `/job-openings`, `/interview-governance`, `/partner-trackers`, `/vendor-partner-hiring`, `/internship-statuses`, `/buddy-engagements`, `/employee-performances` |
| **Project Governance** | `/project-governances`, `/deliverable-trackers`, `/customer-satisfactions`, `/qa-trackers`, `/change-requests`, `/resource-utilizations`, `/raids` |
| **Customer Success** | `/qbr-trackers`, `/escalation-trackers`, `/revenue-trackers`, `/executive-connect-trackers` |
| **Finance** | `/po-trackers`, `/invoice-trackers`, `/budget-trackers` |
| **L&D** | `/reusable-assets`, `/knowledge-repos`, `/capability-buildings`, `/partnership-alliances`, `/tech-capabilities`, `/innovation-automations`, `/training-trackers` |
| **Marketing** | `/event-webinars`, `/content-brandings`, `/campaigns` |
| **Presales** | `/proposal-trackers`, `/rfp-trackers`, `/poc-trackers`, `/presales-bids`, `/presales-demos`, `/presales-governances` |
| **Sales** | `/lead-trackers`, `/sales-revenue-trackers`, `/sales-pipelines` |

Each endpoint supports:
- `GET /` — list all records
- `GET /{id}` — single record
- `POST /` — create
- `PUT /{id}` — full update
- `DELETE /{id}` — delete

## Setup & Run

### 1. Database
```bash
# PostgreSQL must be running. Create DB:
psql -U postgres -c "CREATE USER egt_user WITH PASSWORD 'StrongP@ssw0rd';"
psql -U postgres -c "CREATE DATABASE egt_db OWNER egt_user;"
```

### 2. Install dependencies
```bash
cd revgov_api
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env if your DB credentials are different
```

### 4. Run server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open interactive docs
- **Swagger UI** → http://localhost:8000/docs
- **ReDoc** → http://localhost:8000/redoc

Tables are auto-created on first startup via SQLAlchemy `create_all`.

## Project Structure
```
revgov_api/
├── main.py                        # FastAPI app + all router registrations
├── requirements.txt
├── .env.example
└── app/
    ├── db/
    │   ├── models.py              # SQLAlchemy models (your file)
    │   ├── schemas.py             # Pydantic schemas (your file)
    │   └── session.py             # DB engine + get_db (your file)
    └── api/
        ├── crud_factory.py        # Generic CRUD router (GET/POST/PUT/DELETE)
        └── routes/
            ├── hr.py
            ├── project.py
            ├── customer_success.py
            ├── finance.py
            ├── lnd.py
            ├── marketing.py
            ├── presales.py
            └── sales.py
```
