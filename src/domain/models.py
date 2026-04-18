"""Backward-compatible domain exports."""

from src.domain.accounts import ACCOUNT_BY_CODE, FIXED_CHART_OF_ACCOUNTS, Account
from src.domain.events import (
    BusinessEventType,
    CashReceipt,
    ExpenseBill,
    Partner,
    PartnerType,
    SalesInvoice,
    VendorPayment,
)
from src.domain.journal import JournalEntry, JournalLine

CHART_OF_ACCOUNTS = {account.code: account.name for account in FIXED_CHART_OF_ACCOUNTS}

__all__ = [
    "ACCOUNT_BY_CODE",
    "BusinessEventType",
    "CHART_OF_ACCOUNTS",
    "FIXED_CHART_OF_ACCOUNTS",
    "Account",
    "CashReceipt",
    "ExpenseBill",
    "JournalEntry",
    "JournalLine",
    "Partner",
    "PartnerType",
    "SalesInvoice",
    "VendorPayment",
]
