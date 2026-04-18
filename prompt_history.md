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

## 2026-04-18T20:50:00Z

- Goal: isolate posting engine that converts business events into balanced journal entries
- Prompt summary: implement posting service with clean interface, journal line generation, unsupported-event handling, service-level logging, workflow tests, and brief design note
- Result accepted:
  - refactored posting engine into `PostingService`
  - added single `post(event)` interface with explicit handlers for supported event types
  - kept per-event posting methods for readability and extension
  - made unsupported event types fail with explicit domain exception
  - updated service orchestration to call posting engine directly
  - added posting-engine tests for supported events and unsupported-event rejection
  - documented posting-engine choice in `docs/decisions.md`
- Validation:
  - `python3 -m compileall src tests app.py`
  - `.venv/bin/pytest -q`
- Rejected / changed:
  - preserved compatibility alias `PostingRules = PostingService` to avoid unnecessary breakage while refactoring

## 2026-04-18T21:00:00Z

- Goal: add simple production-minded persistence layer for partners, business documents, and journal entries
- Prompt summary: use SQLite, keep repository abstractions clean, add explicit bootstrap/schema, seed fixed accounts, add repository logging and tests
- Result accepted:
  - split persistence into `SQLiteDatabase`, `PartnerRepository`, `BusinessDocumentRepository`, `JournalEntryRepository`
  - kept `SQLiteRepository` as thin compatibility facade for existing app/service flow
  - added explicit schema for accounts, partners, business documents, journal entries, posting lines
  - seeded fixed chart of accounts during bootstrap
  - service now persists business documents alongside journal entries
  - added repository tests and shared fixtures
- Validation:
  - `python3 -m compileall src tests app.py`
  - `.venv/bin/pytest -q`
- Rejected / changed:
  - did not add heavy ORM or migration tool; kept raw sqlite3 for clarity and low setup cost

## 2026-04-18T21:15:00Z

- Goal: implement application services that orchestrate main user flows
- Prompt summary: split service layer into partner, sales, purchase, and cash services; add transaction-like consistency, logging, and service workflow tests
- Result accepted:
  - added explicit service commands/DTOs and `ServiceResult`
  - split orchestration into `PartnerService`, `SalesService`, `PurchaseService`, `CashService`
  - added shared `ServiceWorkflow` for transactional save of partner + business document + journal entry
  - updated repositories to support shared connection use inside one transaction
  - kept `AccountingService` as thin compatibility facade for current UI
  - added service workflow tests for success, validation failure, rollback, and logging
- Validation:
  - `python3 -m compileall src tests app.py`
  - `.venv/bin/pytest -q`
- Rejected / changed:
  - did not wire UI directly to new services yet; preserved current facade to keep change small and reviewable

## 2026-04-18T21:30:00Z

- Goal: implement reporting layer for simplified Profit and Loss and partner ledger
- Prompt summary: add report services, report DTOs/view models, supporting repository query methods, report tests, and keep logic separate from Streamlit
- Result accepted:
  - added `ProfitAndLossReport` and `PartnerLedgerReport`
  - added reporting DTOs in `src/reporting/models.py`
  - added flattened journal-entry query helper for report use
  - kept small DataFrame adapter functions for current Streamlit rendering compatibility
  - added tests for revenue/expense aggregation, customer and vendor ledger balances, and empty-state reporting
- Validation:
  - `python3 -m compileall src tests app.py`
  - `.venv/bin/pytest -q`
- Rejected / changed:
  - avoided pushing complex SQL into repositories; report computations remain explicit in Python for reviewability

## 2026-04-18T21:40:00Z

- Goal: create clean and simple Streamlit UI shell for accounting app
- Prompt summary: use official Streamlit docs for non-trivial APIs, add app shell with navigation for partners, transactions, and reports, keep UI thin, add helpers, notifications, empty states, and smoke coverage
- Result accepted:
  - added `src/ui/helpers.py` for notifications, tables, empty states, and error rendering
  - added `src/ui/app_state.py` for UI service wiring
  - refactored `src/ui/app_view.py` into sidebar navigation with sections for transactions, partners, and reports
  - kept forms thin and delegated writes to service layer
  - used report services for summaries and report sections
  - expanded UI smoke test to verify navigation labels
- Validation:
  - `python3 -m compileall src tests app.py`
  - `.venv/bin/pytest -q`
- Rejected / changed:
  - did not add flashy dashboard elements; kept layout intentionally plain and reviewer-friendly

## Entry Template

- Date/time:
- Goal:
- Prompt summary:
- Result:
- Accepted / changed / rejected:
- Validation:
