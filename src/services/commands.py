"""Application service commands and results."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from src.domain.events import Partner, PartnerType
from src.domain.journal import JournalEntry


@dataclass(frozen=True)
class CreatePartnerCommand:
    code: str
    name: str
    partner_type: PartnerType


@dataclass(frozen=True)
class SalesInvoiceCommand:
    entry_date: date
    partner_code: str
    partner_name: str
    amount: Decimal
    reference: str
    description: str = ""


@dataclass(frozen=True)
class ExpenseBillCommand:
    entry_date: date
    partner_code: str
    partner_name: str
    amount: Decimal
    reference: str
    description: str = ""


@dataclass(frozen=True)
class CustomerReceiptCommand:
    entry_date: date
    partner_code: str
    partner_name: str
    amount: Decimal
    reference: str
    description: str = ""


@dataclass(frozen=True)
class VendorPaymentCommand:
    entry_date: date
    partner_code: str
    partner_name: str
    amount: Decimal
    reference: str
    description: str = ""


@dataclass(frozen=True)
class ServiceResult:
    partner: Partner
    document_id: str
    journal_entry: JournalEntry
