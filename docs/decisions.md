# Decisions

## Product Decisions

- Keep scope to four business events only.
- Use fixed chart of accounts with codes `1000`, `1100`, `2000`, `4000`, `5000`.
- Keep partner handling minimal with only customer and vendor types.
- Keep reports simple: Profit and Loss plus partner ledger, no broader financial statements.

## Technical Decisions

- Use SQLite with explicit schema through `sqlite3` from standard library.
- Keep domain concepts typed with dataclasses and explicit validation rules.
- Isolate posting logic in `PostingService` with one `post(event)` entrypoint and explicit per-event handlers.
- Split persistence into focused SQLite repositories backed by shared bootstrap/connection helpers.
- Split orchestration into thin application services with shared workflow support for transactional save + logging.
- Keep reporting in dedicated report services with simple DTO/view models.
- Keep Streamlit UI as a thin shell using stable primitives and delegating all business rules to services and reporting.
- Keep Docker runtime single-container and simple: install pinned requirements, copy project files directly, run `streamlit run app.py`, and use a lightweight TCP healthcheck on port `8501`.

## Simplifications

- No migrations framework.
- No authentication.
- No advanced audit trail.
- No separate event table; journal entry stores enough event metadata for review.
- Keep compatibility facades `SQLiteRepository` and `AccountingService` so the current UI wiring stays simple while internal code remains split by responsibility.

## Tradeoffs

- SQLite keeps setup low-friction but not multi-user production grade.
- Type-dispatch posting engine keeps extension local, but unsupported events fail fast instead of being silently ignored.
- Small repositories plus shared DB helper keep schema explicit and reviewable, but add a thin coordination layer.
- Compatibility facades keep the UI simple, but add a small amount of duplication at package edges.
- Reporting stays simple and readable instead of fully general-ledger grade.
