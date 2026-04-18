# Architecture Notes

## Layers

- `core`: settings and logging
- `domain`: fixed accounts, partner types, business event types, posting lines, balanced journal entry
- `repositories`: explicit SQLite schema and data mapping
- `services`: business-event orchestration and posting generation
- `reporting`: simplified Profit and Loss and partner ledger
- `ui`: Streamlit rendering only

## Simplified Accounting Flow

1. User enters one of four business events.
2. Service validates input and partner data.
3. Service maps event into double-entry postings using fixed chart of accounts.
4. Repository stores partner and balanced journal entry in SQLite.
5. Reporting layer derives Profit and Loss and partner ledger from persisted postings.

## Fixed Posting Rules

- Sales invoice: Dr `1100`, Cr `4000`
- Expense bill: Dr `5000`, Cr `2000`
- Cash receipt: Dr `1000`, Cr `1100`
- Cash payment: Dr `2000`, Cr `1000`
