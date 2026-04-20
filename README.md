# Minimal Accounting App

Small reviewable accounting assignment in Python with Streamlit and SQLite.

## Overview

This repository implements a deliberately small accounting web app. It lets a reviewer enter a few fixed business events, see the resulting balanced journal postings, and inspect the effect on a simplified Profit and Loss and partner ledger.

## Reviewer Flow

1. Start the app locally or with Docker.
2. Create a customer or vendor in the `Partners` section, or let transaction entry create one on demand.
3. Enter one or more transactions in `Transactions`.
4. Open `Reports` to verify Profit and Loss totals and partner ledger movements.

## Features In Scope

- fixed chart of accounts
- partner management for customers and vendors
- four business events:
  - sales invoice
  - expense bill
  - cash receipt from customer
  - cash payment to vendor
- transaction form auto-generates partner codes and document references
- transaction entry suggests existing partners by typed name
- app starts empty; reviewer can load sample records with `Seed Demo Data`
- double-entry journal postings
- SQLite persistence
- Streamlit UI
- logging via standard library
- Docker-ready setup
- pytest coverage for smoke, domain, service, repository, reporting, and integration flows

## Architecture Overview

The app uses a small layered structure so accounting rules stay outside the UI:

- `core`: config and logging
- `domain`: typed business events, partners, journal entities, and posting rules
- `repositories`: explicit SQLite schema, bootstrap, and data access
- `services`: orchestration for partner creation, transactions, and posting persistence
- `reporting`: simplified Profit and Loss and partner ledger read models
- `ui`: Streamlit forms, tables, and user-facing messages

Accounting flow:
1. A Streamlit form collects partner and business-event input.
2. Service layer validates input and orchestrates the workflow.
3. `PostingService` converts the event into a balanced journal entry.
4. SQLite repositories persist partner, business document, and journal entry data.
5. Reporting services read persisted postings to build Profit and Loss and partner ledger views.

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

Requirements:
- Python 3.11+
- Docker optional for container run

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

## Sample Usage

Try this small end-to-end flow after startup:

1. Create customer `Acme` in `Partners`.
2. In `Transactions`, create a sales invoice for `100.00`.
3. Create a customer cash receipt for `60.00`.
4. Switch to `Reports`:
   - Profit and Loss should show revenue `100.00`
   - partner ledger should show invoice and receipt movements for `Acme`

## Testing

```bash
pytest -q
```

Coverage includes:
- app smoke startup
- balanced journal validation
- posting rules for all four event types
- repository persistence behavior
- service workflow behavior
- reporting correctness
- integration flow coverage across services and reporting

## Docker

```bash
docker build -t minimal-accounting .
docker run --rm -p 8501:8501 -v minimal_accounting_data:/app/data minimal-accounting
```

App available at `http://localhost:8501`

Container includes lightweight healthcheck against local Streamlit port.

## Docker Compose

```bash
docker compose up --build
```

SQLite lives inside app container and persists through named volume `sqlite_data`.

Compose also exposes the app at `http://localhost:8501`.

For quick verification after startup:
- check container health with `docker ps`
- inspect app logs with `docker logs <container-name>`

## Product Decisions

- keep scope to four fixed business events only
- keep the chart of accounts fixed and not user-editable
- keep reports simple and reviewer-friendly rather than general-ledger complete
- keep partner handling minimal with customer/vendor types only

## Technical Decisions

- use `sqlite3` from the standard library with an explicit schema
- keep accounting rules in the domain and service layers, not in Streamlit callbacks
- use a dedicated posting service to generate balanced journal entries
- keep reporting logic separate from UI rendering
- keep Docker runtime single-container and simple

## Limitations / Non-Goals

- fixed chart of accounts only
- no tax, reconciliation, inventory, payroll, or multi-currency
- no auth or advanced audit trail
- simple SQLite persistence, no migrations framework
- not intended as a full ERP or multi-user accounting system
