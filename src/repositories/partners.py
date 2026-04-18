"""Partner repository."""

from __future__ import annotations

from src.core.logging_config import get_logger
from src.domain.events import Partner, PartnerType
from src.repositories.database import SQLiteDatabase

logger = get_logger(__name__)


class PartnerRepository:
    """Persist and load partners."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def upsert(self, partner: Partner) -> None:
        """Create or update partner."""
        try:
            with self._database.connect() as connection:
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
        except Exception:
            logger.exception("Partner repository write failed", extra={"partner_code": partner.code})
            raise

    def list_all(self) -> list[Partner]:
        """Return all partners."""
        try:
            with self._database.connect() as connection:
                rows = connection.execute(
                    "SELECT code, name, partner_type FROM partners ORDER BY code"
                ).fetchall()
        except Exception:
            logger.exception("Partner repository read failed")
            raise
        return [
            Partner(code=row["code"], name=row["name"], partner_type=PartnerType(row["partner_type"]))
            for row in rows
        ]
