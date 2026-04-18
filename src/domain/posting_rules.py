"""Explicit posting rules for minimal accounting events."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from src.domain.accounts import (
    ACCOUNTS_PAYABLE,
    ACCOUNTS_RECEIVABLE,
    CASH,
    EXPENSE,
    REVENUE,
)
from src.domain.events import CashReceipt, ExpenseBill, SalesInvoice, VendorPayment
from src.domain.journal import JournalEntry, JournalLine


@dataclass(frozen=True)
class PostingRules:
    """Factory for fixed double-entry posting rules."""

    def post_sales_invoice(self, event: SalesInvoice) -> JournalEntry:
        return JournalEntry(
            entry_id=str(uuid4()),
            entry_date=event.entry_date,
            event_type=event.event_type.value,
            partner_code=event.partner.code,
            partner_name=event.partner.name,
            reference=event.reference,
            description=event.description,
            lines=(
                JournalLine(account=ACCOUNTS_RECEIVABLE, debit=event.amount),
                JournalLine(account=REVENUE, credit=event.amount),
            ),
        )

    def post_expense_bill(self, event: ExpenseBill) -> JournalEntry:
        return JournalEntry(
            entry_id=str(uuid4()),
            entry_date=event.entry_date,
            event_type=event.event_type.value,
            partner_code=event.partner.code,
            partner_name=event.partner.name,
            reference=event.reference,
            description=event.description,
            lines=(
                JournalLine(account=EXPENSE, debit=event.amount),
                JournalLine(account=ACCOUNTS_PAYABLE, credit=event.amount),
            ),
        )

    def post_cash_receipt(self, event: CashReceipt) -> JournalEntry:
        return JournalEntry(
            entry_id=str(uuid4()),
            entry_date=event.entry_date,
            event_type=event.event_type.value,
            partner_code=event.partner.code,
            partner_name=event.partner.name,
            reference=event.reference,
            description=event.description,
            lines=(
                JournalLine(account=CASH, debit=event.amount),
                JournalLine(account=ACCOUNTS_RECEIVABLE, credit=event.amount),
            ),
        )

    def post_vendor_payment(self, event: VendorPayment) -> JournalEntry:
        return JournalEntry(
            entry_id=str(uuid4()),
            entry_date=event.entry_date,
            event_type=event.event_type.value,
            partner_code=event.partner.code,
            partner_name=event.partner.name,
            reference=event.reference,
            description=event.description,
            lines=(
                JournalLine(account=ACCOUNTS_PAYABLE, debit=event.amount),
                JournalLine(account=CASH, credit=event.amount),
            ),
        )
