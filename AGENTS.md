# AGENTS.md

## Project mission

Build a minimal but coherent accounting web application in **Python** using **Streamlit** for the UI.

The application must demonstrate a small, understandable accounting flow:
- create basic business records
- convert them into balanced accounting postings
- show a simplified **Profit and Loss**
- show a simplified **partner ledger**

This repository is being built as a test assignment. The solution must be:
- runnable
- reviewable
- easy to start
- technically clean
- intentionally small in scope

---

## Non-negotiable assignment constraints

Always follow these rules:

- Use **Python**
- Use **Streamlit** for the web UI
- Do **not** use ready-made accounting libraries or accounting engines
- A **Dockerfile is mandatory**

---

## Primary product goal

Build a **minimal accounting app**, not a full ERP.

The product must clearly show:
1. how business events are entered
2. how those events generate accounting postings
3. how postings affect:
   - Profit and Loss
   - partner balances / movements

Keep the solution small and coherent.

---

## Scope boundaries

Stay intentionally narrow.

### In scope
- fixed chart of accounts
- partner management
- a small set of business events
- automatic journal posting
- simplified reporting
- Dockerized app
- tests
- logging
- readable code

### Out of scope
Do **not** build:
- full ERP features
- account management UI
- tax engine
- reconciliation engine
- multi-currency support
- advanced permissions
- production-grade audit trail
- inventory
- payroll
- bank integrations
- async event architecture unless absolutely necessary
- microservices
- heavy frontend framework patterns inside Streamlit

If unsure, choose the smaller solution.

---

## Engineering principles

Write **production-minded code**, but keep it pragmatic.

### Required qualities
- clean
- readable
- maintainable
- testable
- explicit
- small in scope
- easy to review

### Apply these principles
- **DRY**: avoid duplication, but do not over-abstract early
- **SOLID**: apply pragmatically, not ceremonially
- prefer small functions and classes with clear responsibility
- prefer explicit naming over cleverness
- prefer composition over deep inheritance
- keep domain logic out of UI
- keep reporting logic out of UI
- keep persistence logic out of domain models
- avoid god objects and giant files
- provide code with clean docstrings

### Avoid
- overengineering
- enterprise-style ceremony
- unnecessary factories/builders/managers
- dependency injection frameworks
- vague helper modules with mixed responsibilities
- hidden magic
- premature abstraction

---

## Required technology direction

Use this stack unless there is a very strong reason not to:

- Python 3.11 or 3.12
- Streamlit
- SQLite for persistence
- pytest for tests
- standard logging module
- Docker

Keep dependencies minimal and pinned.

---

## Current documentation policy

This project uses Streamlit, and Streamlit APIs may differ by version.

### Rules
- Do **not** rely on model memory for Streamlit APIs
- Before using non-trivial or version-sensitive Streamlit features, consult the **current official Streamlit docs**
- Prefer official docs via configured documentation tool Context7
- Follow the pinned Streamlit version in project dependencies
- If memory conflicts with docs, follow docs

### Streamlit guidance
Prefer simple and stable primitives:
- `st.form`
- `st.session_state`
- `st.dataframe`
- `st.tabs`
- `st.metric`
- `st.selectbox`
- `st.date_input`
- `st.number_input`
- `st.text_input`
- `st.warning`, `st.error`, `st.success`

Avoid flashy or exotic components unless there is a clear need.

---

## Product design rules

The app must remain easy to understand for a reviewer.

### UX rules
- simple navigation
- simple forms
- clear labels
- clean report views
- graceful empty states
- clear success/error messages
- avoid clutter
- avoid fancy UI for its own sake

### Reviewer-first mindset
Assume the reviewer wants to:
1. start the app quickly
2. create sample business events
3. see the resulting postings
4. verify reports
5. inspect code structure quickly

Design for that flow.

---

## Fixed accounting model

Use a **fixed chart of accounts** only.
Do not build account creation or account management UI.

### Fixed accounts
- `1000` — Cash
- `1100` — Accounts Receivable
- `2000` — Accounts Payable
- `4000` — Revenue
- `5000` — Expense

You may refine display names slightly if needed, but keep codes and meaning stable. :contentReference[oaicite:2]{index=2}

---

## Required business events

Support this minimal set of business events:

1. **Sales invoice**
2. **Expense bill**
3. **Cash receipt from customer**
4. **Cash payment to vendor**

These are enough to show:
- revenue
- expense
- customer balances
- vendor balances
- cash movement

Do not add many more event types unless they are absolutely necessary.

---

## Required posting rules

All postings must use **double-entry accounting**.
Every journal entry must balance exactly.

### Posting logic

#### 1. Sales invoice
Creates customer receivable and revenue:
- Dr `1100` Accounts Receivable
- Cr `4000` Revenue

#### 2. Expense bill
Creates vendor payable and expense:
- Dr `5000` Expense
- Cr `2000` Accounts Payable

#### 3. Cash receipt from customer
Settles receivable into cash:
- Dr `1000` Cash
- Cr `1100` Accounts Receivable

#### 4. Cash payment to vendor
Settles payable using cash:
- Dr `2000` Accounts Payable
- Cr `1000` Cash

### Validation rules
- no one-sided entries
- debits must equal credits
- amounts must be positive unless there is an explicit reason otherwise
- partner must be present where required
- invalid postings must fail clearly

---

## Partner model

Keep partner handling simple.

### Minimum requirements
A partner should support:
- unique identifier
- name
- type:
  - customer
  - vendor

Optional small additions are acceptable if clearly useful:
- note
- reference code

Do not turn this into a CRM.

---

## Reporting rules

The assignment requires two reports. :contentReference[oaicite:3]{index=3}

### 1. Profit and Loss
Must show simplified movement of:
- revenue
- expense
- net result

Keep it simple and understandable.

### 2. Partner ledger
Must show partner-level balances or movements for:
- customers
- vendors

A reasonable ledger view may include:
- date
- document/event type
- reference
- debit
- credit
- running balance or ending balance

Keep it understandable and consistent with your posting model.

---

## Recommended architecture

Use a small layered structure.

### Suggested layout
- `app.py`
- `src/`
  - `core/`
  - `domain/`
  - `services/`
  - `repositories/`
  - `reporting/`
  - `ui/`
- `tests/`
- `docs/`
- `prompt_history.md`
- `README.md`
- `Dockerfile`
- `requirements.txt`

### Responsibility split

#### `core/`
Cross-cutting basics:
- config
- logging
- shared exceptions
- bootstrap helpers

#### `domain/`
Pure business concepts:
- entities
- value objects
- enums
- journal logic
- posting rules
- domain validation

#### `services/`
Application orchestration:
- create partner
- create invoice
- create bill
- register receipt/payment
- call posting engine
- save results

#### `repositories/`
Persistence only:
- saving/loading partners
- documents
- journal entries
- report query helpers if needed

#### `reporting/`
Report generation only:
- P&L
- partner ledger
- report DTOs / read models

#### `ui/`
Streamlit-facing code only:
- page rendering
- forms
- tables
- user messages
- calling service layer

---

## Strict layering rules

Always keep these separations:

- UI must **not** contain business rules
- UI must **not** calculate postings
- UI must **not** calculate reports
- domain must **not** depend on Streamlit
- repositories must **not** contain business policy
- reporting must **not** depend on UI
- services may orchestrate domain + repositories + reporting access

If logic is reusable, it does not belong directly inside the Streamlit page code.

---

## Persistence rules

Prefer a simple SQLite-backed persistence layer.

### Requirements
- schema should be explicit and easy to review
- avoid unnecessary ORM complexity
- persistence must stay simple and reliable
- fixed chart of accounts may be represented as constants or seeded reference data
- database bootstrapping must be deterministic

### Avoid
- advanced migration frameworks unless clearly needed
- excessive table normalization
- persistence-driven design that distorts business logic

---

## Error handling and logging

Use `logging`, not print statements.

### Logging goals
- help debugging
- record service-level failures
- record repository failures
- capture unexpected exceptions with useful context

### Logging rules
- do not spam logs for normal happy-path actions
- log errors with enough context to investigate
- use warning level for recoverable issues
- use exception logging when catching unexpected failures
- keep messages readable

### Error handling rules
- fail clearly
- raise domain-specific exceptions where useful
- convert internal errors into user-friendly messages in UI
- never silently swallow important exceptions

---

## Testing policy

Tests are required after every finalized implementation step.

### General rules
- use `pytest`
- tests must be readable
- tests must focus on behavior
- keep fixtures/helpers clean
- avoid brittle tests that depend too much on implementation details

### Must-cover areas
- balanced journal validation
- posting logic for all business events
- invalid input cases
- service orchestration
- persistence basics
- reporting correctness
- smoke tests for app startup where reasonable

### Testing cadence
After each major step is finalized, add or update tests before moving on.

---

## Docker rules

Docker is mandatory. :contentReference[oaicite:4]{index=4}

### Requirements
- Dockerfile must exist
- build must be simple
- container must run the Streamlit app correctly
- README must include exact Docker commands
- `.dockerignore` should be present and sensible

### Goal
A reviewer should be able to build and run the project with low effort.

---

## Documentation rules

### README must include
- project overview
- features in scope
- architecture summary
- setup instructions
- local run instructions
- Docker run instructions
- testing instructions
- limitations / non-goals

### `docs/decisions.md` should include
- product decisions
- technical decisions
- simplifications taken
- tradeoffs

### `prompt_history.md`
This is mandatory. :contentReference[oaicite:5]{index=5}

Maintain it throughout the project.
Do not leave it empty until the end.

For each significant Codex or LLM-assisted step, append:
- date/time
- goal
- prompt used or concise faithful summary
- result
- what was accepted / changed / rejected

---

## Commit workflow

After each completed implementation step, prepare code in a state suitable for a manual Git commit.

### Commit message style
Use semantic commits such as:
- `feat: initialize production-ready project structure`
- `feat: implement core accounting domain and posting rules`
- `test: add integration coverage for reporting flows`
- `docs: finalize submission documentation`
- `refactor: simplify posting service responsibilities`

Do not create random or vague commit messages.

---

## Working mode for Codex

For non-trivial tasks, follow this order:

1. read `AGENTS.md`
2. inspect current structure
3. plan the change
4. implement the smallest clean solution
5. add/update tests
6. update docs if relevant
7. ensure Docker path still makes sense
8. prepare a concise summary
9. propose one semantic commit message

### If task is ambiguous
Choose the smallest correct solution that satisfies the assignment.

### If tempted to add features
Stop and ask:
- does this improve required accounting flow?
- does this improve reviewability?
- is it necessary for acceptance?

If not, skip it.

---

## Code style rules

- use type hints where reasonable
- keep files focused
- keep functions short when possible
- use meaningful names
- avoid cryptic abstractions
- avoid giant classes
- docstrings only where they add value
- comments should explain intent, not obvious syntax
- prefer plain, boring, maintainable Python

---

## Performance expectations

Performance is not the main challenge here.

Prioritize:
- correctness
- clarity
- maintainability
- deterministic behavior

Do not optimize prematurely.

---

## Security and privacy simplification

This is not a production SaaS with full auth requirements.

Do not spend time on:
- full auth system
- role management
- advanced secrets handling
- multi-user tenancy

Just avoid obviously unsafe coding habits.

---

## Reviewer experience rules

Always optimize for a reviewer being able to:
- run the app quickly
- understand the architecture quickly
- verify posting rules quickly
- verify reports quickly
- inspect tests quickly

When choosing between “smart” and “clear”, choose “clear”.

---

## Done criteria

A task is considered done only if all relevant items below are true:

- code is clean and readable
- solution remains within scope
- business logic is coherent
- journal entries balance
- reports are consistent with postings
- tests for the finalized step are present
- logging is in place
- docs are updated if needed
- Docker setup still works
- acceptance-condition files remain present


---

## Default decision bias

When in doubt:
- choose smaller scope
- choose clearer code
- choose explicit logic
- choose testable design
- choose reviewer-friendly UX
- choose maintainability over feature count
