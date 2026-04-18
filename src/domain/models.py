"""Core accounting domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum


class PartnerType(StrEnum):
    """Supported partner types."""

    CUSTOMER = "customer"
    VENDOR = "vendor"


class BusinessEventType(StrEnum):
    """Minimal supported business events."""

    SALES_INVOICE = "sales_invoice"
    EXPENSE_BILL = "expense_bill"
    CASH_RECEIPT = "cash_receipt"
    CASH_PAYMENT = "cash_payment"


CHART_OF_ACCOUNTS = {
    "1000": "Cash",
    "1100": "Accounts Receivable",
    "2000": "Accounts Payable",
    "4000": "Revenue",
    "5000": "Expense",
}


@dataclass(frozen=True)
class Partner:
    """Partner master record."""

    code: str
    name: str
    partner_type: PartnerType


@dataclass(frozen=True)
class PostingLine:
    """Single journal posting line."""

    account_code: str
    debit: Decimal
    credit: Decimal

    def __post_init__(self) -> None:
        if self.account_code not in CHART_OF_ACCOUNTS:
            raise ValueError("unknown account code")
        if self.debit < Decimal("0.00") or self.credit < Decimal("0.00"):
            raise ValueError("debit and credit must be non-negative")
        if self.debit and self.credit:
            raise ValueError("posting line cannot have both debit and credit")
        if not self.debit and not self.credit:
            raise ValueError("posting line must have debit or credit")


@dataclass(frozen=True)
class JournalEntry:
    """Balanced journal entry generated from business event."""

    entry_id: str
    entry_date: date
    event_type: BusinessEventType
    partner_code: str
    partner_name: str
    amount: Decimal
    reference: str
    description: str
    lines: tuple[PostingLine, ...]

    def __post_init__(self) -> None:
        if self.amount <= Decimal("0.00"):
            raise ValueError("amount must be positive")
        if not self.partner_code.strip():
            raise ValueError("partner code required")
        if not self.partner_name.strip():
            raise ValueError("partner name required")
        if not self.reference.strip():
            raise ValueError("reference required")
        self.validate_balanced()

    def validate_balanced(self) -> None:
        """Ensure journal entry is balanced."""
        debit_total = sum((line.debit for line in self.lines), start=Decimal("0.00"))
        credit_total = sum((line.credit for line in self.lines), start=Decimal("0.00"))
        if debit_total != credit_total:
            raise ValueError("journal entry not balanced")

    def to_journal_row(self) -> dict[str, object]:
        """Serialize high-level journal row."""
        return {
            "entry_id": self.entry_id,
            "entry_date": self.entry_date.isoformat(),
            "event_type": self.event_type.value,
            "partner_code": self.partner_code,
            "partner_name": self.partner_name,
            "amount": float(self.amount),
            "reference": self.reference,
            "description": self.description,
        }

    def to_posting_rows(self) -> list[dict[str, object]]:
        """Serialize posting lines for tabular rendering."""
        rows: list[dict[str, object]] = []
        for line in self.lines:
            rows.append(
                {
                    "entry_id": self.entry_id,
                    "entry_date": self.entry_date.isoformat(),
                    "event_type": self.event_type.value,
                    "partner_code": self.partner_code,
                    "partner_name": self.partner_name,
                    "reference": self.reference,
                    "account_code": line.account_code,
                    "account_name": CHART_OF_ACCOUNTS[line.account_code],
                    "debit": float(line.debit),
                    "credit": float(line.credit),
                }
            )
        return rows
