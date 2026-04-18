"""Business document repository."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from src.core.logging_config import get_logger
from src.domain.events import (
    BusinessEvent,
    BusinessEventType,
    CashReceipt,
    ExpenseBill,
    Partner,
    SalesInvoice,
    VendorPayment,
)
from src.repositories.database import SQLiteDatabase

logger = get_logger(__name__)


EVENT_CLASS_BY_TYPE = {
    BusinessEventType.SALES_INVOICE.value: SalesInvoice,
    BusinessEventType.EXPENSE_BILL.value: ExpenseBill,
    BusinessEventType.CASH_RECEIPT.value: CashReceipt,
    BusinessEventType.CASH_PAYMENT.value: VendorPayment,
}


class BusinessDocumentRepository:
    """Persist and load business documents."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def save(self, event: BusinessEvent, document_id: str | None = None) -> str:
        """Persist business document and return identifier."""
        saved_document_id = document_id or str(uuid4())
        try:
            with self._database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO business_documents (
                        document_id, event_type, entry_date, partner_code, amount, reference, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        saved_document_id,
                        event.event_type.value,
                        event.entry_date.isoformat(),
                        event.partner.code,
                        str(event.amount),
                        event.reference,
                        event.description,
                    ),
                )
        except Exception:
            logger.exception(
                "Business document repository write failed",
                extra={"document_id": saved_document_id, "event_type": event.event_type.value},
            )
            raise
        return saved_document_id

    def list_all(self, partners_by_code: dict[str, Partner]) -> list[tuple[str, BusinessEvent]]:
        """Return stored business documents with reconstructed event models."""
        try:
            with self._database.connect() as connection:
                rows = connection.execute(
                    """
                    SELECT document_id, event_type, entry_date, partner_code, amount, reference, description
                    FROM business_documents
                    ORDER BY entry_date, document_id
                    """
                ).fetchall()
        except Exception:
            logger.exception("Business document repository read failed")
            raise

        documents: list[tuple[str, BusinessEvent]] = []
        for row in rows:
            event_cls = EVENT_CLASS_BY_TYPE[row["event_type"]]
            documents.append(
                (
                    row["document_id"],
                    event_cls(
                        entry_date=date.fromisoformat(row["entry_date"]),
                        partner=partners_by_code[row["partner_code"]],
                        amount=Decimal(row["amount"]),
                        reference=row["reference"],
                        description=row["description"],
                    ),
                )
            )
        return documents
