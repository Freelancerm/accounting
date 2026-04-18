# Prompt History

## 2026-04-18T20:00:00Z

- Goal: initialize production-minded minimal accounting web app in Python with Streamlit
- Prompt summary: create clean project structure with Docker, pinned dependencies, logging, prompt history, simplified accounting flow, Profit and Loss, partner ledger, and tests
- Result accepted:
  - created layered `src/` structure plus `app.py`, `README.md`, `Dockerfile`, `.dockerignore`, `requirements.txt`, `tests/`, `docs/`
  - implemented SQLite-backed minimal accounting flow with four business events and fixed chart of accounts
  - added reporting for simplified Profit and Loss and partner ledger
  - added logging setup and pytest coverage
- Validation:
  - `python3 -m compileall app.py src tests`
  - `.venv/bin/pytest -q`
- Rejected / changed:
  - replaced initial generic in-memory ledger scaffold with assignment-specific double-entry and SQLite structure after reading `AGENTS.md`

## 2026-04-18T20:40:00Z

- Goal: design and implement clean core domain model and fixed accounting rules
- Prompt summary: add typed domain entities for partners, accounts, journal, four business events, explicit posting rules, domain exceptions, structured service-boundary logging, and tests for balanced postings and invalid cases
- Result accepted:
  - split domain into focused modules: `accounts`, `events`, `journal`, `posting_rules`, `errors`
  - added explicit entities: `Partner`, `Account`, `JournalEntry`, `JournalLine`, `SalesInvoice`, `ExpenseBill`, `CashReceipt`, `VendorPayment`
  - added fixed chart of accounts and explicit posting rules for all four business events
  - updated service layer to build domain events, call posting rules, and log at service boundary
  - expanded tests to verify balancing, all four posting scenarios, invalid input, and service boundary behavior
- Validation:
  - `python3 -m compileall src tests app.py`
  - `.venv/bin/pytest -q`
- Rejected / changed:
  - kept existing SQLite repository compatible with new domain model instead of adding new persistence abstraction for this step

## Entry Template

- Date/time:
- Goal:
- Prompt summary:
- Result:
- Accepted / changed / rejected:
- Validation:
