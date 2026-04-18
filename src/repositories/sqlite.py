"""SQLite persistence for partners and journal entries."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date
from decimal import Decimal
from pathlib import Path
import sqlite3

from src.domain.accounts import ACCOUNT_BY_CODE
from src.domain.events import Partner, PartnerType
from src.domain.journal import JournalEntry, JournalLine


class SQLiteRepository:
    """Small explicit SQLite repository."""

    def __init__(self, database_path: str = "data/accounting.db") -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self._database_path)
        try:
            connection.row_factory = sqlite3.Row
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS partners (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    partner_type TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS journal_entries (
                    entry_id TEXT PRIMARY KEY,
                    entry_date TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    partner_code TEXT NOT NULL,
                    partner_name TEXT NOT NULL,
                    amount TEXT NOT NULL,
                    reference TEXT NOT NULL,
                    description TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS posting_lines (
                    line_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id TEXT NOT NULL,
                    account_code TEXT NOT NULL,
                    debit TEXT NOT NULL,
                    credit TEXT NOT NULL,
                    FOREIGN KEY(entry_id) REFERENCES journal_entries(entry_id)
                );
                """
            )

    def upsert_partner(self, partner: Partner) -> None:
        """Create or update partner."""
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO partners (code, name, partner_type)
                VALUES (?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                    name = excluded.name,
                    partner_type = excluded.partner_type
                """,
                (partner.code, partner.name, partner.partner_type.value),
            )

    def list_partners(self) -> list[Partner]:
        """Return all partners."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT code, name, partner_type FROM partners ORDER BY code"
            ).fetchall()
        return [
            Partner(code=row["code"], name=row["name"], partner_type=PartnerType(row["partner_type"]))
            for row in rows
        ]

    def save_journal_entry(self, entry: JournalEntry) -> None:
        """Persist balanced journal entry and lines."""
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO journal_entries (
                    entry_id, entry_date, event_type, partner_code, partner_name,
                    amount, reference, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.entry_id,
                    entry.entry_date.isoformat(),
                    entry.event_type,
                    entry.partner_code,
                    entry.partner_name,
                    str(entry.amount),
                    entry.reference,
                    entry.description,
                ),
            )
            connection.executemany(
                """
                INSERT INTO posting_lines (entry_id, account_code, debit, credit)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (entry.entry_id, line.account_code, str(line.debit), str(line.credit))
                    for line in entry.lines
                ],
            )

    def list_journal_entries(self) -> list[JournalEntry]:
        """Load journal entries with posting lines."""
        with self._connect() as connection:
            entry_rows = connection.execute(
                "SELECT * FROM journal_entries ORDER BY entry_date, entry_id"
            ).fetchall()
            line_rows = connection.execute(
                "SELECT entry_id, account_code, debit, credit FROM posting_lines ORDER BY line_id"
            ).fetchall()

        lines_by_entry: dict[str, list[PostingLine]] = {}
        for row in line_rows:
            lines_by_entry.setdefault(row["entry_id"], []).append(
                JournalLine(
                    account=ACCOUNT_BY_CODE[row["account_code"]],
                    debit=Decimal(row["debit"]),
                    credit=Decimal(row["credit"]),
                )
            )

        entries: list[JournalEntry] = []
        for row in entry_rows:
            entries.append(
                JournalEntry(
                    entry_id=row["entry_id"],
                    entry_date=date.fromisoformat(row["entry_date"]),
                    event_type=row["event_type"],
                    partner_code=row["partner_code"],
                    partner_name=row["partner_name"],
                    reference=row["reference"],
                    description=row["description"],
                    lines=tuple(lines_by_entry.get(row["entry_id"], [])),
                )
            )
        return entries
