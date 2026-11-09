# LeadFlow

Real-time Meta Lead Ads integration with FastAPI, PostgreSQL, WebSockets, and React Native.

## Overview

LeadFlow captures lead submissions from Meta Lead Ads, processes and stores them in a backend, and delivers new leads to a React Native application in real time.

## Architecture

```
Meta Lead Ads
    |
    v
Meta Webhooks
    |
    v
FastAPI Backend
    |
    v
Meta Graph API
    |
    v
PostgreSQL
    |
    v
WebSocket Connection
    |
    v
React Native Application
```

## Tech Stack

- Backend: Python, FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Real-time communication: WebSockets
- Mobile: React Native
- Integration: Meta Graph API and Webhooks

## Project Structure

- `backend/` — FastAPI backend
- `mobile/` — React Native application
- `docs/` — Architecture and technical documentation

## Database

LeadFlow uses PostgreSQL with SQLAlchemy's asynchronous engine.

### Using Docker Compose (recommended)

From the repository root:

```bash
docker compose up -d
```

This starts PostgreSQL on `localhost:5432` with database `leadflow`, user `leadflow`, and the password from `POSTGRES_PASSWORD`.

Check it is running:

```bash
docker compose ps
```

Stop it:

```bash
docker compose down
```

Database data persists in the `postgres_data` named volume. Do not run `docker compose down -v` unless you want to delete that volume.

### Configuration

Create a local `.env` file inside `backend/`:

```env
DATABASE_URL=postgresql+psycopg://leadflow:your_password@localhost:5432/leadflow
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
```

Do not commit this file.

### Health checks

- `/api/v1/health` — API liveness
- `/api/v1/ready` — database readiness

### Lead Management API

LeadFlow supports creating, retrieving, and listing leads.

#### Create a lead

POST `/api/v1/leads`

Example request:

```json
{
  "meta_lead_id": "meta-demo-001",
  "page_id": "page-demo",
  "form_id": "form-demo",
  "ad_id": "ad-demo",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone_number": "+911234567890"
}
```

#### List leads

GET `/api/v1/leads?page=1&page_size=20`

#### Retrieve a lead

GET `/api/v1/leads/{lead_id}`

#### Idempotency

The Meta lead ID is unique. Repeated ingestion of the same Meta lead returns the existing record instead of creating a duplicate.

#### Database migrations

Run from `backend/`:

```
alembic revision --autogenerate -m "describe schema change"
alembic upgrade head
```

## Local Backend Setup

From the repository root:

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r backend/requirements.txt

cd backend
uvicorn app.main:app --reload
```

## API Documentation

Once the backend is running:

- Swagger UI: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/v1/health

## Running Tests

From the `backend` directory:

```bash
python -m pytest -v
```

## Current Status

Milestone 3: Lead Management API.
