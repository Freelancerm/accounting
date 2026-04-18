# Minimal Accounting App

Small reviewable accounting assignment in Python with Streamlit and SQLite.

## Overview

App shows minimal accounting flow:
- enter business event
- generate balanced journal postings automatically
- view simplified Profit and Loss
- view partner ledger movements

## Features In Scope

- fixed chart of accounts
- partner master data created on demand
- four business events:
  - sales invoice
  - expense bill
  - cash receipt from customer
  - cash payment to vendor
- double-entry journal postings
- SQLite persistence
- Streamlit UI
- logging via standard library
- Docker-ready setup
- pytest coverage for startup, posting rules, validation, and reports

## Architecture Summary

- `core`: config and logging
- `domain`: partners, business events, journal entities, posting rules primitives
- `repositories`: explicit SQLite schema and persistence
- `services`: business-event orchestration and posting generation
- `reporting`: Profit and Loss and partner ledger read models
- `ui`: Streamlit forms, tables, and user-facing messages

## Project Structure

```text
.
├── app.py
├── src/
│   ├── core/
│   ├── domain/
│   ├── repositories/
│   ├── reporting/
│   ├── services/
│   └── ui/
├── tests/
├── docs/
├── Dockerfile
├── README.md
├── prompt_history.md
└── requirements.txt
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Local Run

```bash
streamlit run app.py
```

Default database path: `data/accounting.db`

## Testing

```bash
pytest -q
```

## Docker

```bash
docker build -t minimal-accounting .
docker run --rm -p 8501:8501 minimal-accounting
```

## Docker Compose

```bash
docker compose up --build
```

SQLite lives inside app container and persists through named volume `sqlite_data`.

## Limitations / Non-Goals

- fixed chart of accounts only
- no tax, reconciliation, inventory, payroll, or multi-currency
- no auth or advanced audit trail
- simple SQLite persistence, no migrations framework
