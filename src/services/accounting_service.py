"""Application orchestration for business events and postings."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from src.core.logging_config import get_logger
from src.domain.errors import DomainError
from src.domain.events import CashReceipt, ExpenseBill, Partner, PartnerType, SalesInvoice, VendorPayment
from src.domain.journal import JournalEntry
from src.domain.posting_rules import PostingService
from src.repositories.sqlite import SQLiteRepository

logger = get_logger(__name__)


class AccountingService:
    """Record business events and generate balanced postings."""

    def __init__(self, repository: SQLiteRepository) -> None:
        self._repository = repository
        self._posting_service = PostingService()

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
        event = SalesInvoice(
            entry_date=entry_date,
            partner=self._build_partner(partner_code, partner_name, PartnerType.CUSTOMER),
            amount=amount,
            reference=reference,
            description=description,
        )
        return self._record_posted_event(event)

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
        event = ExpenseBill(
            entry_date=entry_date,
            partner=self._build_partner(partner_code, partner_name, PartnerType.VENDOR),
            amount=amount,
            reference=reference,
            description=description,
        )
        return self._record_posted_event(event)

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
        event = CashReceipt(
            entry_date=entry_date,
            partner=self._build_partner(partner_code, partner_name, PartnerType.CUSTOMER),
            amount=amount,
            reference=reference,
            description=description,
        )
        return self._record_posted_event(event)

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
        event = VendorPayment(
            entry_date=entry_date,
            partner=self._build_partner(partner_code, partner_name, PartnerType.VENDOR),
            amount=amount,
            reference=reference,
            description=description,
        )
        return self._record_posted_event(event)

    def list_entries(self) -> list[JournalEntry]:
        """Return all journal entries."""
        return self._repository.list_journal_entries()

    def list_partners(self) -> list[Partner]:
        """Return all partners."""
        return self._repository.list_partners()

    def _record_posted_event(
        self,
        event: SalesInvoice | ExpenseBill | CashReceipt | VendorPayment,
    ) -> JournalEntry:
        try:
            entry = self._posting_service.post(event)
            self._repository.upsert_partner(event.partner)
            self._repository.save_journal_entry(entry)
            logger.info(
                "Recorded accounting event",
                extra={
                    "event_type": event.event_type.value,
                    "partner_code": event.partner.code,
                    "reference": event.reference,
                    "amount": str(event.amount),
                },
            )
            return entry
        except DomainError:
            logger.warning(
                "Rejected accounting event",
                extra={
                    "event_type": event.event_type.value,
                    "partner_code": event.partner.code,
                    "reference": event.reference,
                },
            )
            raise
        except Exception:
            logger.exception(
                "Unexpected service failure while recording accounting event",
                extra={
                    "event_type": event.event_type.value,
                    "partner_code": event.partner.code,
                    "reference": event.reference,
                },
            )
            raise

    @staticmethod
    def _build_partner(code: str, name: str, partner_type: PartnerType) -> Partner:
        return Partner(code=code, name=name, partner_type=partner_type)
