"""SQLite database bootstrap and connection management."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3

from src.core.logging_config import get_logger
from src.domain.accounts import FIXED_CHART_OF_ACCOUNTS

logger = get_logger(__name__)


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS accounts (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS partners (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    partner_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS business_documents (
    document_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    entry_date TEXT NOT NULL,
    partner_code TEXT NOT NULL,
    amount TEXT NOT NULL,
    reference TEXT NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY(partner_code) REFERENCES partners(code)
);

CREATE TABLE IF NOT EXISTS journal_entries (
    entry_id TEXT PRIMARY KEY,
    entry_date TEXT NOT NULL,
    event_type TEXT NOT NULL,
    partner_code TEXT NOT NULL,
    partner_name TEXT NOT NULL,
    reference TEXT NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY(partner_code) REFERENCES partners(code)
);

CREATE TABLE IF NOT EXISTS posting_lines (
    line_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id TEXT NOT NULL,
    account_code TEXT NOT NULL,
    debit TEXT NOT NULL,
    credit TEXT NOT NULL,
    FOREIGN KEY(entry_id) REFERENCES journal_entries(entry_id),
    FOREIGN KEY(account_code) REFERENCES accounts(code)
);
"""


class SQLiteDatabase:
    """Own SQLite bootstrap and connection lifecycle."""

    def __init__(self, database_path: str = "data/accounting.db") -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self):
        """Open SQLite connection with row mapping."""
        connection = sqlite3.connect(self._database_path)
        try:
            connection.row_factory = sqlite3.Row
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            logger.exception("SQLite transaction failed", extra={"database_path": str(self._database_path)})
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        """Create schema and seed fixed accounts."""
        with self.connect() as connection:
            connection.executescript(SCHEMA_SQL)
            connection.executemany(
                """
                INSERT INTO accounts (code, name)
                VALUES (?, ?)
                ON CONFLICT(code) DO UPDATE SET name = excluded.name
                """,
                [(account.code, account.name) for account in FIXED_CHART_OF_ACCOUNTS],
            )
