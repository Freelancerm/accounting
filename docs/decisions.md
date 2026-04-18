# Decisions

## Product Decisions

- Keep scope to four business events only.
- Use fixed chart of accounts with codes `1000`, `1100`, `2000`, `4000`, `5000`.
- Create partners on demand from event entry instead of separate CRUD UI.

## Technical Decisions

- Use SQLite with explicit schema through `sqlite3` from standard library.
- Keep domain logic in dataclasses and service layer.
- Keep Streamlit UI limited to stable primitives: `st.form`, `st.tabs`, `st.dataframe`, `st.metric`, `st.selectbox`, `st.date_input`, `st.number_input`, `st.text_input`.

## Simplifications

- No migrations framework.
- No authentication.
- No advanced audit trail.
- No separate event table; journal entry stores enough event metadata for review.

## Tradeoffs

- SQLite keeps setup low-friction but not multi-user production grade.
- On-demand partner creation reduces UI clutter but skips master-data workflows.
- Reporting stays simple and readable instead of fully general ledger-grade.
