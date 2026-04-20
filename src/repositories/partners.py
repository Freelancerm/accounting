"""Partner repository."""

from __future__ import annotations

from contextlib import nullcontext
import sqlite3

from src.core.logging_config import get_logger
from src.domain.events import Partner, PartnerType
from src.repositories.database import SQLiteDatabase

logger = get_logger(__name__)


class PartnerRepository:
    """Persist and load partners."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def upsert(self, partner: Partner, connection: sqlite3.Connection | None = None) -> None:
        """Create or update partner."""
        try:
            connection_manager = nullcontext(connection) if connection is not None else self._database.connect()
            with connection_manager as active_connection:
                active_connection.execute(
                    """
                    INSERT INTO partners (code, name, partner_type)
                    VALUES (?, ?, ?)
                    ON CONFLICT(code) DO UPDATE SET
                        name = excluded.name,
                        partner_type = excluded.partner_type
                    """,
                    (partner.code, partner.name, partner.partner_type.value),
                )
        except Exception:
            logger.exception("Partner repository write failed", extra={"partner_code": partner.code})
            raise

    def list_all(self, connection: sqlite3.Connection | None = None) -> list[Partner]:
        """Return all partners."""
        try:
            connection_manager = nullcontext(connection) if connection is not None else self._database.connect()
            with connection_manager as active_connection:
                rows = active_connection.execute(
                    "SELECT code, name, partner_type FROM partners ORDER BY code"
                ).fetchall()
        except Exception:
            logger.exception("Partner repository read failed")
            raise
        return [
            Partner(code=row["code"], name=row["name"], partner_type=PartnerType(row["partner_type"]))
            for row in rows
        ]

    def search_by_name(
        self,
        query: str,
        partner_type: PartnerType,
        *,
        limit: int = 5,
        connection: sqlite3.Connection | None = None,
    ) -> list[Partner]:
        """Return small case-insensitive partner suggestion list."""
        normalized_query = query.strip()
        if not normalized_query:
            return []

        try:
            connection_manager = nullcontext(connection) if connection is not None else self._database.connect()
            with connection_manager as active_connection:
                rows = active_connection.execute(
                    """
                    SELECT code, name, partner_type
                    FROM partners
                    WHERE partner_type = ?
                      AND UPPER(name) LIKE UPPER(?)
                    ORDER BY name, code
                    LIMIT ?
                    """,
                    (partner_type.value, f"%{normalized_query}%", limit),
                ).fetchall()
        except Exception:
            logger.exception(
                "Partner repository search failed",
                extra={"partner_type": partner_type.value, "query": normalized_query},
            )
            raise

        return [
            Partner(code=row["code"], name=row["name"], partner_type=PartnerType(row["partner_type"]))
            for row in rows
        ]

    def find_by_exact_name(
        self,
        name: str,
        partner_type: PartnerType,
        connection: sqlite3.Connection | None = None,
    ) -> Partner | None:
        """Return exact case-insensitive partner name match when present."""
        normalized_name = name.strip()
        if not normalized_name:
            return None

        try:
            connection_manager = nullcontext(connection) if connection is not None else self._database.connect()
            with connection_manager as active_connection:
                row = active_connection.execute(
                    """
                    SELECT code, name, partner_type
                    FROM partners
                    WHERE partner_type = ?
                      AND UPPER(name) = UPPER(?)
                    ORDER BY code
                    LIMIT 1
                    """,
                    (partner_type.value, normalized_name),
                ).fetchone()
        except Exception:
            logger.exception(
                "Partner repository exact-name lookup failed",
                extra={"partner_type": partner_type.value, "name": normalized_name},
            )
            raise

        if row is None:
            return None
        return Partner(code=row["code"], name=row["name"], partner_type=PartnerType(row["partner_type"]))
