"""Application orchestration for business events and postings."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Callable

from src.domain.events import BusinessEventType, Partner, PartnerType
from src.domain.journal import JournalEntry
from src.repositories.sqlite import SQLiteRepository
from src.services.cash_service import CashService
from src.services.commands import (
    CustomerReceiptCommand,
    ExpenseBillCommand,
    SalesInvoiceCommand,
    VendorPaymentCommand,
)
from src.services.partner_service import PartnerService
from src.services.purchase_service import PurchaseService
from src.services.sales_service import SalesService


class AccountingService:
    """Record business events and generate balanced postings."""

    def __init__(self, repository: SQLiteRepository) -> None:
        self._repository = repository
        self.partners = PartnerService(repository)
        self.sales = SalesService(repository)
        self.purchases = PurchaseService(repository)
        self.cash = CashService(repository)

    def seed_demo_data(self, on_progress: Callable[[int, int], None] | None = None) -> int:
        """Seed minimal demo data once and report inserted step progress."""
        if self._repository.list_journal_entries():
            return 0

        demo_steps = (
            lambda: self.record_sales_invoice(
                entry_date=date(2026, 1, 5),
                partner_code="CUST-001",
                partner_name="Acme Client",
                amount=Decimal("12500.00"),
                reference="INV-1001",
                description="January consulting invoice",
            ),
            lambda: self.record_expense_bill(
                entry_date=date(2026, 1, 7),
                partner_code="VEND-001",
                partner_name="Cloud Vendor",
                amount=Decimal("950.00"),
                reference="BILL-2001",
                description="Hosting bill",
            ),
            lambda: self.record_cash_receipt(
                entry_date=date(2026, 1, 10),
                partner_code="CUST-001",
                partner_name="Acme Client",
                amount=Decimal("8000.00"),
                reference="RCPT-3001",
                description="Partial customer receipt",
            ),
        )

        total_steps = len(demo_steps)
        for index, step in enumerate(demo_steps, start=1):
            step()
            if on_progress is not None:
                on_progress(index, total_steps)
        return total_steps

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
        return self.sales.create_sales_invoice(
            SalesInvoiceCommand(
                entry_date=entry_date,
                partner_code=partner_code,
                partner_name=partner_name,
                amount=amount,
                reference=reference,
                description=description,
            )
        ).journal_entry

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
        return self.purchases.create_expense_bill(
            ExpenseBillCommand(
                entry_date=entry_date,
                partner_code=partner_code,
                partner_name=partner_name,
                amount=amount,
                reference=reference,
                description=description,
            )
        ).journal_entry

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
        return self.cash.register_customer_receipt(
            CustomerReceiptCommand(
                entry_date=entry_date,
                partner_code=partner_code,
                partner_name=partner_name,
                amount=amount,
                reference=reference,
                description=description,
            )
        ).journal_entry

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
        return self.cash.register_vendor_payment(
            VendorPaymentCommand(
                entry_date=entry_date,
                partner_code=partner_code,
                partner_name=partner_name,
                amount=amount,
                reference=reference,
                description=description,
            )
        ).journal_entry

    def list_entries(self) -> list[JournalEntry]:
        """Return all journal entries."""
        return self._repository.list_journal_entries()

    def list_partners(self) -> list[Partner]:
        """Return all partners."""
        return self.partners.list_partners()

    def suggest_partners(self, name_query: str, partner_type: PartnerType, *, limit: int = 5) -> list[Partner]:
        """Return partner suggestions for transaction entry."""
        return self.partners.suggest_partners(name_query, partner_type, limit=limit)

    def preview_partner_code(self, partner_name: str, partner_type: PartnerType) -> str:
        """Return existing or next generated partner code."""
        if not partner_name.strip():
            return ""
        return self.partners.resolve_partner_identity("", partner_name, partner_type).code

    def preview_reference(self, event_type: BusinessEventType) -> str:
        """Return next generated document reference for event type."""
        return self._repository.next_reference(event_type)
