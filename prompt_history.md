- **Prompts**
    - **Step 1. Create project skeleton**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Create a production-minded initial project structure for a minimal accounting web app in Python using Streamlit.
        
        Context:
        This assignment requires:
        - Python
        - Streamlit UI
        - Dockerfile
        - prompt_history.md
        - simplified accounting flow
        - simplified Profit and Loss report
        - partner ledger
        
        Constraints:
        - Do not use ready-made accounting libraries or accounting engines.
        - Keep the architecture clean, small, and maintainable.
        - Apply DRY and SOLID pragmatically.
        - Add logging setup.
        - Make the project Docker-ready.
        - Use pinned dependencies.
        - Keep code readable and reviewable.
        - Create tests scaffold as well.
        - Use current Streamlit documentation through Context7 when needed.
        
        Preferred structure:
        - app.py
        - src/
          - core/
          - domain/
          - services/
          - repositories/
          - reporting/
          - ui/
        - tests/
        - docs/
        - prompt_history.md
        - README.md
        - Dockerfile
        - requirements.txt
        
        Deliver:
        1. Initial file/folder structure
        2. requirements.txt with pinned packages
        3. Dockerfile
        4. .dockerignore
        5. basic README with setup and run instructions
        6. prompt_history.md template
        7. logging configuration module
        8. a minimal app entrypoint that runs
        9. at least one smoke test
        
        Done when:
        - project structure exists
        - app starts
        - tests run
        - Dockerfile exists
        - README exists
        - prompt_history.md exists
        ```
        
        Commit:
        `feat: initialize project structure`
        
    - **Step 2. Define domain model and accounting rules**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Design and implement the core domain model and fixed accounting rules for the app.
        
        Context:
        We need a minimal but coherent accounting flow.
        Use fixed chart of accounts only:
        - 1000 Cash
        - 1100 Accounts Receivable
        - 2000 Accounts Payable
        - 4000 Revenue
        - 5000 Expense
        
        Supported business events:
        - Sales invoice
        - Expense bill
        - Cash receipt from customer
        - Cash payment to vendor
        
        Constraints:
        - Production-minded code
        - DRY and SOLID
        - No overengineering
        - Explicit, readable naming
        - Use dataclasses or typed models where appropriate
        - Add structured logging in service boundaries
        - Add tests for all finalized domain rules
        - No database complexity yet unless needed
        - No UI-heavy work yet
        
        Implement:
        1. domain entities/value objects for:
           - Partner
           - PartnerType
           - Account
           - JournalEntry
           - JournalLine
           - SalesInvoice
           - ExpenseBill
           - CashReceipt
           - VendorPayment
        2. fixed chart of accounts definition
        3. validation rules so journal entries must balance
        4. posting rule definitions for the four business events
        5. errors/exceptions for invalid posting or invalid domain input
        6. unit tests for:
           - balanced entry validation
           - each posting scenario
           - invalid input cases
        
        Done when:
        - domain layer is clean and typed
        - posting rules are explicit and understandable
        - tests verify balanced postings and rule correctness
        ```
        
        Commit:
        `feat: implement core accounting domain and posting rules`
        
    - **Step 3. Build posting engine**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Implement the posting engine that converts business events into balanced journal entries.
        
        Context:
        Business events:
        - Sales invoice -> Dr AR / Cr Revenue
        - Expense bill -> Dr Expense / Cr AP
        - Cash receipt from customer -> Dr Cash / Cr AR
        - Cash payment to vendor -> Dr AP / Cr Cash
        
        Constraints:
        - Production-minded code
        - Keep logic DRY and testable
        - Separate domain rules from orchestration
        - Use logging for service-level errors and key actions
        - Avoid duplication in posting logic
        - Add tests for all finalized posting workflows
        
        Implement:
        1. PostingService or equivalent
        2. clear interface for posting supported event types
        3. journal line generation with account code and amount
        4. proper domain exceptions and error logging
        5. unit tests for:
           - each event posted into expected journal lines
           - unsupported event types
           - zero or negative amount rejection if not allowed
           - balanced output validation
        
        Also:
        - make code easy to extend without rewriting everything
        - briefly document the design in docs/decisions.md
        
        Done when:
        - posting engine is isolated and testable
        - all required events produce correct journal entries
        - tests pass
        ```
        
        Commit:
        `feat: add posting engine for business events`
        
    - **Step 4. Add persistence layer**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Add a simple production-minded persistence layer for storing partners, business documents, and journal entries.
        
        Context:
        This app is still intentionally small.
        Use a simple persistence choice that is easy to run and review.
        Prefer SQLite for this assignment unless there is a compelling reason not to.
        
        Constraints:
        - Keep repository abstractions clean
        - Avoid premature complexity
        - Use DRY and SOLID pragmatically
        - Keep persistence logic separate from domain logic
        - Add logging for repository errors
        - Add tests for repository behavior
        - Docker compatibility must remain simple
        - No heavy ORM magic if it harms clarity
        
        Implement:
        1. persistence strategy and folder structure
        2. repositories for:
           - partners
           - business events/documents
           - journal entries
        3. simple database initialization/bootstrap
        4. seed or bootstrap fixed chart of accounts if needed
        5. repository tests
        6. test fixtures/helpers to keep tests readable
        
        Important:
        - keep the storage schema simple and explicit
        - ensure code remains easy to review
        - do not bury business logic inside persistence layer
        
        Done when:
        - data can be created and retrieved
        - repository interfaces are clean
        - tests cover core repository behavior
        ```
        
        Commit:
        `feat: add persistence layer with repository abstractions`
        
    - **Step 5. Add application services**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Implement application services that orchestrate the user flows.
        
        Context:
        We need clean service-layer orchestration for:
        - create customer/vendor partner
        - create sales invoice and post it
        - create expense bill and post it
        - register customer cash receipt and post it
        - register vendor payment and post it
        
        Constraints:
        - Production-minded code
        - DRY and SOLID
        - Clear separation between UI, service layer, domain, and persistence
        - Use logging for failures and important service operations
        - Return meaningful results/errors
        - Add tests after finishing the service layer
        
        Implement:
        1. PartnerService
        2. SalesService
        3. PurchaseService
        4. CashService or similarly clean structure
        5. transaction-like handling so business event and journal posting stay consistent
        6. tests for service workflows
        7. error paths and validation paths
        
        Also:
        - keep services thin but useful
        - prefer explicit commands/DTOs if that improves clarity
        - avoid stuffing everything into one god-service
        
        Done when:
        - main business flows work end to end through service layer
        - tests verify service behavior
        - logging is in place
        ```
        
        Commit:
        `feat: implement application services for core accounting flows`
        
    - **Step 6. Build reporting layer**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Implement the reporting layer for simplified Profit and Loss and partner ledger.
        
        Context:
        Assignment requires:
        - simplified Profit and Loss
        - small partner ledger
        Reports must be understandable and consistent with the posting model.
        
        Constraints:
        - Production-minded code
        - Reporting logic must be separate from UI
        - Keep calculations simple, explicit, and correct
        - Add logging for report generation errors
        - Add tests for every finalized report
        - Avoid overcomplicated SQL unless clearly justified
        
        Implement:
        1. ProfitAndLossReport service
        2. PartnerLedgerReport service
        3. supporting query/repository methods
        4. report DTOs/view models appropriate for UI rendering
        5. tests for:
           - revenue and expense aggregation into P&L
           - partner ledger movements and balances
           - customer and vendor scenarios
           - empty-state reporting
        
        Clarify behavior:
        - P&L should reflect revenue and expense movement simply
        - partner ledger should show movements and current balance per partner
        
        Done when:
        - reports are generated independently of Streamlit
        - tests confirm correctness
        ```
        
        Commit:
        `feat: implement profit and loss and partner ledger reporting`
        
    - **Step 7. Build Streamlit UI shell**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Create a clean and simple Streamlit UI shell for the accounting app.
        
        Context:
        Use current official Streamlit docs through Context7 before using non-trivial Streamlit APIs.
        We need a small, usable UI for review, not a flashy dashboard.
        
        Constraints:
        - Production-minded code
        - Keep UI thin and delegate logic to services
        - Use clear layout and navigation
        - Prefer Streamlit primitives like forms, tabs, tables, and metrics
        - Avoid business logic inside UI callbacks
        - Add smoke tests or any reasonable UI-level tests possible for this architecture
        - Keep logging for error handling
        - Docker run path must still work
        
        Implement:
        1. app entrypoint with page config
        2. navigation structure
        3. pages/sections for:
           - partners
           - transactions
           - reports
        4. common UI helpers
        5. graceful error rendering for failed operations
        6. success/error notifications
        7. basic empty states
        
        Done when:
        - app navigation is usable
        - UI is clean and thin
        - service layer is called from UI cleanly
        ```
        
        Commit:
        `feat: add Streamlit application shell and navigation`
        
    - **Step 8. Build partner management UI**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Implement the Streamlit UI for managing partners.
        
        Context:
        Partners are simplified and should support at least:
        - name
        - type: customer or vendor
        
        Constraints:
        - Production-minded code
        - Keep UI logic thin
        - Use forms and tables cleanly
        - Validate user input
        - Show meaningful errors
        - Add tests after this step if applicable to current architecture
        - Logging should capture service failures, not spam normal flow
        
        Implement:
        1. create partner form
        2. partner list/table
        3. simple filtering by type if useful
        4. empty states and validation feedback
        5. tests for partner service/UI-adjacent behavior where appropriate
        
        Done when:
        - user can create and list customer/vendor partners from the UI
        - behavior is clean and stable
        ```
        
        Commit:
        `feat: add partner management interface`
        
    - **Step 9. Build business transaction UI**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Implement the Streamlit UI for creating business transactions that trigger accounting postings.
        
        Context:
        Required flows:
        - sales invoice
        - expense bill
        - customer cash receipt
        - vendor payment
        
        Constraints:
        - Production-minded code
        - Keep UI forms clear and small
        - Reuse form/helper components where appropriate
        - Do not duplicate service-calling logic unnecessarily
        - Validate required fields and amounts
        - Handle errors gracefully
        - Add tests after finalizing the step
        - Keep logging in service layer and critical UI boundary points
        
        Implement:
        1. transaction forms for all four business events
        2. partner selection where relevant
        3. amount/date/reference fields as needed
        4. success feedback after posting
        5. optional transaction list/history view if it stays small and useful
        6. tests for transaction workflows through service layer and any integration-level paths you can cover reasonably
        
        Done when:
        - user can create all required business events from UI
        - postings are generated and stored
        - errors are handled cleanly
        ```
        
        Commit:
        `feat: add transaction flows for invoices receipts bills and payments`
        
    - **Step 10. Build reports UI**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Implement the Streamlit UI for Profit and Loss and partner ledger reports.
        
        Context:
        Reports already exist in reporting layer.
        Now expose them clearly in the UI.
        
        Constraints:
        - Production-minded code
        - Keep report rendering simple and readable
        - Use metrics, tables, or grouped views only where useful
        - Keep calculations in reporting layer, not UI
        - Add tests after finalizing
        - Logging should handle report-generation failures
        
        Implement:
        1. Profit and Loss page/section
        2. Partner ledger page/section
        3. partner filter for ledger
        4. empty states
        5. report refresh controls only if needed
        6. tests for integration paths around reporting if reasonable
        
        Done when:
        - reports are visible and understandable in UI
        - UI is thin
        - reporting logic remains outside UI
        ```
        
        Commit:
        `feat: add reporting interface for pnl and partner ledger`
        
    - **Step 11. Add integration tests and hardening**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Harden the app and add broader automated test coverage.
        
        Context:
        Core flows now exist.
        We need stronger confidence and production-minded cleanup.
        
        Constraints:
        - Production-minded code
        - Improve quality without bloating scope
        - Keep tests readable and maintainable
        - Add logging improvements where useful
        - Avoid unnecessary abstractions
        - Docker setup must remain simple and working
        
        Implement:
        1. integration tests for end-to-end business flows through services
        2. test data helpers/fixtures cleanup
        3. validation hardening
        4. improve exception handling and logs
        5. remove dead code and duplication
        6. small refactors that improve readability and SOLID compliance without changing behavior
        
        Important:
        - do not add random features
        - focus on reliability and clarity
        
        Done when:
        - major flows are covered by tests
        - codebase is cleaner
        - logging and error handling are improved
        ```
        
        Commit:
        `test: add integration coverage and harden core workflows`
        
    - **Step 12. Finalize Docker and runtime behavior**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Finalize Docker support and ensure the app is easy to run and review.
        
        Context:
        Dockerfile already exists but now finalize the runtime path for the completed app.
        
        Constraints:
        - Production-minded setup
        - Keep Docker simple and reliable
        - Do not overengineer containerization
        - Ensure Streamlit app runs correctly in container
        - Add any minimal health/readiness notes if useful
        - Verify local and Docker instructions match reality
        
        Implement:
        1. review and improve Dockerfile
        2. improve .dockerignore if needed
        3. ensure correct Streamlit startup command
        4. ensure required files are copied correctly
        5. document Docker build/run in README
        6. add a lightweight smoke verification if reasonable
        
        Done when:
        - app builds and runs in Docker
        - README includes exact Docker commands
        - setup is reviewer-friendly
        ```
        
        Commit:
        `chore: finalize docker runtime and deployment instructions`
        
    - **Step 13. Final documentation and submission readiness**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Prepare the repository for final submission.
        
        Context:
        The assignment requires:
        - public GitHub repository
        - working Python + Streamlit solution
        - Dockerfile
        - setup/run instructions
        - prompt history
        - short explanation of product and technical decisions
        
        Constraints:
        - Keep docs concise but sufficient
        - Make repo easy for reviewer to understand quickly
        - Do not invent features not in the code
        - Ensure documentation matches actual implementation
        
        Implement:
        1. finalize README.md
        2. finalize docs/decisions.md with concise product and technical decisions
        3. review prompt_history.md and ensure it is populated clearly
        4. add sample usage section
        5. add architecture overview section
        6. add limitations/non-goals section aligned with assignment simplifications
        7. add testing instructions
        8. verify naming consistency across repository
        
        Done when:
        - repository is submission-ready
        - docs are coherent and accurate
        - all acceptance-condition files are present
        ```
        
        Commit:
        `docs: finalize submission documentation and project decisions`
        
    - **Step 14. Final review and cleanup pass**
        
        ```markdown
        Read AGENTS.md first and follow it strictly.
        
        Goal:
        Perform a final production-minded review of the whole repository and apply safe cleanup improvements.
        
        Context:
        The app should remain intentionally small but clean, coherent, and reviewable.
        
        Constraints:
        - No major feature additions
        - Focus on readability, maintainability, and consistency
        - Preserve current behavior unless fixing clear defects
        - Keep DRY and SOLID pragmatic
        - Ensure logging is useful and not noisy
        - Ensure tests still pass
        - Keep Docker working
        
        Review for:
        1. duplicated logic
        2. oversized files/functions
        3. naming clarity
        4. exception handling consistency
        5. logging quality
        6. test quality
        7. README accuracy
        8. prompt_history completeness
        
        Apply:
        - safe refactors
        - cleanup of small inconsistencies
        - improved comments/docstrings only where useful
        
        Done when:
        - codebase is cleaner
        - behavior is unchanged except for clear bug fixes
        - tests remain green
        ```
        
        Commit:
        `refactor: polish codebase for readability consistency and maintainability`
        
    - **Step 15. Polish User experience**
        
        ```markdown
        When we create transactions. Fields 
        Partner Code
        Reference
        must generating automatically. User don't must to type it
        Remove field existing partner 
        When user typing Pertner name, under the hood service must complete search in existing clients and suggest to choose it in dropdown menu
        
        ```
      Commit:
        `feat: perform best UI exp for user`
        
    - **Step 16. Provide Demo data button**
        
        ```markdown
        Our project must start empty, without demo (seed) data.
        
        On our website must be a button “Seed Demo Data” 
        
        when user click it, show loading progress and seed our database with demo data
        ```
        Commit:
        `feat: added Seed Demo Data button`
- **Fixing after AI:**
    
    Added static methods, fixing warnings in PyCharm
Commit:
        `fix: fixing type hinting, added staticmethods`
    
    Added foreign keys using in src/repositories/database.py:
    
    `connection.execute("PRAGMA foreign_keys = ON")`
Commit:
        `fix: fixed foreign keys in db connect`
    

