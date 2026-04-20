"""Explicit posting engine for minimal accounting events."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from uuid import uuid4

from src.domain.accounts import (
    ACCOUNTS_PAYABLE,
    ACCOUNTS_RECEIVABLE,
    CASH,
    EXPENSE,
    REVENUE,
)
from src.domain.errors import InvalidPostingError
from src.domain.events import BusinessEvent, CashReceipt, ExpenseBill, SalesInvoice, VendorPayment
from src.domain.journal import JournalEntry, JournalLine


@dataclass(frozen=True)
class PostingService:
    """Posting engine for supported business events."""

    def post(self, event: BusinessEvent) -> JournalEntry:
        """Convert supported event into balanced journal entry."""
        handlers: dict[type[BusinessEvent], Callable[[BusinessEvent], JournalEntry]] = {
            SalesInvoice: lambda item: self.post_sales_invoice(item),
            ExpenseBill: lambda item: self.post_expense_bill(item),
            CashReceipt: lambda item: self.post_cash_receipt(item),
            VendorPayment: lambda item: self.post_vendor_payment(item),
        }
        handler = handlers.get(type(event))
        if handler is None:
            raise InvalidPostingError(f"unsupported event type: {type(event).__name__}")
        return handler(event)

    @staticmethod
    def post_sales_invoice(event: SalesInvoice) -> JournalEntry:
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

    @staticmethod
    def post_expense_bill(event: ExpenseBill) -> JournalEntry:
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

    @staticmethod
    def post_cash_receipt(event: CashReceipt) -> JournalEntry:
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

    @staticmethod
    def post_vendor_payment(event: VendorPayment) -> JournalEntry:
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


PostingRules = PostingService
