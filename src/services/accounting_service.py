"""Application orchestration for business events and postings."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
import uuid

from src.core.logging_config import get_logger
from src.domain.models import (
    BusinessEventType,
    JournalEntry,
    Partner,
    PartnerType,
    PostingLine,
)
from src.repositories.sqlite import SQLiteRepository

logger = get_logger(__name__)


class AccountingService:
    """Record business events and generate balanced postings."""

    def __init__(self, repository: SQLiteRepository) -> None:
        self._repository = repository

    def bootstrap_sample_data(self) -> None:
        """Seed minimal demo data once."""
        if self._repository.list_journal_entries():
            return

        self.record_sales_invoice(
            entry_date=date(2026, 1, 5),
            partner_code="CUST-001",
            partner_name="Acme Client",
            amount=Decimal("12500.00"),
            reference="INV-1001",
            description="January consulting invoice",
        )
        self.record_expense_bill(
            entry_date=date(2026, 1, 7),
            partner_code="VEND-001",
            partner_name="Cloud Vendor",
            amount=Decimal("950.00"),
            reference="BILL-2001",
            description="Hosting bill",
        )
        self.record_cash_receipt(
            entry_date=date(2026, 1, 10),
            partner_code="CUST-001",
            partner_name="Acme Client",
            amount=Decimal("8000.00"),
            reference="RCPT-3001",
            description="Partial customer receipt",
        )

    def record_sales_invoice(
        self,
        *,
        entry_date: date,
        partner_code: str,
        partner_name: str,
        amount: Decimal,
        reference: str,
        description: str = "",
    ) -> JournalEntry:
        self._validate_amount(amount)
        return self._record_event(
            event_type=BusinessEventType.SALES_INVOICE,
            partner_type=PartnerType.CUSTOMER,
            entry_date=entry_date,
            partner_code=partner_code,
            partner_name=partner_name,
            amount=amount,
            reference=reference,
            description=description,
            lines=(
                PostingLine(account_code="1100", debit=amount, credit=Decimal("0.00")),
                PostingLine(account_code="4000", debit=Decimal("0.00"), credit=amount),
            ),
        )

    def record_expense_bill(
        self,
        *,
        entry_date: date,
        partner_code: str,
        partner_name: str,
        amount: Decimal,
        reference: str,
        description: str = "",
    ) -> JournalEntry:
        self._validate_amount(amount)
        return self._record_event(
            event_type=BusinessEventType.EXPENSE_BILL,
            partner_type=PartnerType.VENDOR,
            entry_date=entry_date,
            partner_code=partner_code,
            partner_name=partner_name,
            amount=amount,
            reference=reference,
            description=description,
            lines=(
                PostingLine(account_code="5000", debit=amount, credit=Decimal("0.00")),
                PostingLine(account_code="2000", debit=Decimal("0.00"), credit=amount),
            ),
        )

    def record_cash_receipt(
        self,
        *,
        entry_date: date,
        partner_code: str,
        partner_name: str,
        amount: Decimal,
        reference: str,
        description: str = "",
    ) -> JournalEntry:
        self._validate_amount(amount)
        return self._record_event(
            event_type=BusinessEventType.CASH_RECEIPT,
            partner_type=PartnerType.CUSTOMER,
            entry_date=entry_date,
            partner_code=partner_code,
            partner_name=partner_name,
            amount=amount,
            reference=reference,
            description=description,
            lines=(
                PostingLine(account_code="1000", debit=amount, credit=Decimal("0.00")),
                PostingLine(account_code="1100", debit=Decimal("0.00"), credit=amount),
            ),
        )

    def record_cash_payment(
        self,
        *,
        entry_date: date,
        partner_code: str,
        partner_name: str,
        amount: Decimal,
        reference: str,
        description: str = "",
    ) -> JournalEntry:
        self._validate_amount(amount)
        return self._record_event(
            event_type=BusinessEventType.CASH_PAYMENT,
            partner_type=PartnerType.VENDOR,
            entry_date=entry_date,
            partner_code=partner_code,
            partner_name=partner_name,
            amount=amount,
            reference=reference,
            description=description,
            lines=(
                PostingLine(account_code="2000", debit=amount, credit=Decimal("0.00")),
                PostingLine(account_code="1000", debit=Decimal("0.00"), credit=amount),
            ),
        )

    def list_entries(self) -> list[JournalEntry]:
        """Return all journal entries."""
        return self._repository.list_journal_entries()

    def list_partners(self) -> list[Partner]:
        """Return all partners."""
        return self._repository.list_partners()

    def _record_event(
        self,
        *,
        event_type: BusinessEventType,
        partner_type: PartnerType,
        entry_date: date,
        partner_code: str,
        partner_name: str,
        amount: Decimal,
        reference: str,
        description: str,
        lines: tuple[PostingLine, ...],
    ) -> JournalEntry:
        normalized_code = partner_code.strip().upper()
        normalized_name = partner_name.strip()
        normalized_reference = reference.strip().upper()
        normalized_amount = amount.quantize(Decimal("0.01"))

        if not normalized_code:
            raise ValueError("partner code required")
        if not normalized_name:
            raise ValueError("partner name required")
        if normalized_amount <= Decimal("0.00"):
            raise ValueError("amount must be positive")
        if not normalized_reference:
            raise ValueError("reference required")

        partner = Partner(
            code=normalized_code,
            name=normalized_name,
            partner_type=partner_type,
        )
        entry = JournalEntry(
            entry_id=str(uuid.uuid4()),
            entry_date=entry_date,
            event_type=event_type,
            partner_code=partner.code,
            partner_name=partner.name,
            amount=normalized_amount,
            reference=normalized_reference,
            description=description.strip(),
            lines=lines,
        )
        self._repository.upsert_partner(partner)
        self._repository.save_journal_entry(entry)
        logger.info(
            "Recorded accounting event",
            extra={
                "event_type": event_type.value,
                "partner_code": partner.code,
                "reference": entry.reference,
            },
        )
        return entry

    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        """Fail early before posting-line construction."""
        if amount <= Decimal("0.00"):
            raise ValueError("amount must be positive")
