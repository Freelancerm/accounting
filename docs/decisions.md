# Decisions

## Product Decisions

- Keep scope to four business events only.
- Use fixed chart of accounts with codes `1000`, `1100`, `2000`, `4000`, `5000`.
- Create partners on demand from event entry instead of separate CRUD UI.

## Technical Decisions

- Use SQLite with explicit schema through `sqlite3` from standard library.
- Keep domain logic in dataclasses and service layer.
- Isolate posting engine in `PostingService` with one `post(event)` entrypoint and explicit per-event handlers.
- Split persistence into small repositories: `PartnerRepository`, `BusinessDocumentRepository`, `JournalEntryRepository`, backed by shared `SQLiteDatabase` bootstrap/helper.
- Keep Streamlit UI limited to stable primitives: `st.form`, `st.tabs`, `st.dataframe`, `st.metric`, `st.selectbox`, `st.date_input`, `st.number_input`, `st.text_input`.

## Simplifications

- No migrations framework.
- No authentication.
- No advanced audit trail.
- No separate event table; journal entry stores enough event metadata for review.
- Keep repository facade `SQLiteRepository` for app compatibility while real persistence lives in focused repositories.

## Tradeoffs

- SQLite keeps setup low-friction but not multi-user production grade.
- On-demand partner creation reduces UI clutter but skips master-data workflows.
- Type-dispatch posting engine keeps extension local, but unsupported events fail fast instead of being silently ignored.
- Shared DB helper plus small repositories keeps schema explicit and reviewable, but adds thin coordination layer instead of one-file persistence.
- Reporting stays simple and readable instead of fully general ledger-grade.
