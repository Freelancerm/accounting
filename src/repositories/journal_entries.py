"""Journal entry repository."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from src.core.logging_config import get_logger
from src.domain.accounts import ACCOUNT_BY_CODE
from src.domain.journal import JournalEntry, JournalLine
from src.repositories.database import SQLiteDatabase

logger = get_logger(__name__)


class JournalEntryRepository:
    """Persist and load journal entries."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def save(self, entry: JournalEntry) -> None:
        """Persist balanced journal entry and lines."""
        try:
            with self._database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO journal_entries (
                        entry_id, entry_date, event_type, partner_code, partner_name, reference, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.entry_id,
                        entry.entry_date.isoformat(),
                        entry.event_type,
                        entry.partner_code,
                        entry.partner_name,
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
        except Exception:
            logger.exception("Journal entry repository write failed", extra={"entry_id": entry.entry_id})
            raise

    def list_all(self) -> list[JournalEntry]:
        """Return all journal entries with posting lines."""
        try:
            with self._database.connect() as connection:
                entry_rows = connection.execute(
                    """
                    SELECT entry_id, entry_date, event_type, partner_code, partner_name, reference, description
                    FROM journal_entries
                    ORDER BY entry_date, entry_id
                    """
                ).fetchall()
                line_rows = connection.execute(
                    """
                    SELECT entry_id, account_code, debit, credit
                    FROM posting_lines
                    ORDER BY line_id
                    """
                ).fetchall()
        except Exception:
            logger.exception("Journal entry repository read failed")
            raise

        lines_by_entry: dict[str, list[JournalLine]] = {}
        for row in line_rows:
            lines_by_entry.setdefault(row["entry_id"], []).append(
                JournalLine(
                    account=ACCOUNT_BY_CODE[row["account_code"]],
                    debit=Decimal(row["debit"]),
                    credit=Decimal(row["credit"]),
                )
            )

        return [
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
            for row in entry_rows
        ]
