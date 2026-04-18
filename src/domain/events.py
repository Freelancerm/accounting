"""Business event entities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from src.domain.errors import InvalidDomainInputError


class PartnerType(StrEnum):
    """Supported partner types."""

    CUSTOMER = "customer"
    VENDOR = "vendor"


class BusinessEventType(StrEnum):
    """Supported business events."""

    SALES_INVOICE = "sales_invoice"
    EXPENSE_BILL = "expense_bill"
    CASH_RECEIPT = "cash_receipt"
    CASH_PAYMENT = "cash_payment"


@dataclass(frozen=True)
class Partner:
    """Simple partner master record."""

    code: str
    name: str
    partner_type: PartnerType

    def __post_init__(self) -> None:
        normalized_code = self.code.strip().upper()
        normalized_name = self.name.strip()
        if not normalized_code:
            raise InvalidDomainInputError("partner code required")
        if not normalized_name:
            raise InvalidDomainInputError("partner name required")
        object.__setattr__(self, "code", normalized_code)
        object.__setattr__(self, "name", normalized_name)


@dataclass(frozen=True)
class BusinessEvent:
    """Base business event input."""

    entry_date: date
    partner: Partner
    amount: Decimal
    reference: str
    description: str = ""

    event_type: BusinessEventType = BusinessEventType.SALES_INVOICE

    def __post_init__(self) -> None:
        normalized_amount = self.amount.quantize(Decimal("0.01"))
        normalized_reference = self.reference.strip().upper()
        normalized_description = self.description.strip()

        if normalized_amount <= Decimal("0.00"):
            raise InvalidDomainInputError("amount must be positive")
        if not normalized_reference:
            raise InvalidDomainInputError("reference required")

        object.__setattr__(self, "amount", normalized_amount)
        object.__setattr__(self, "reference", normalized_reference)
        object.__setattr__(self, "description", normalized_description)


@dataclass(frozen=True)
class SalesInvoice(BusinessEvent):
    """Customer sales invoice."""

    event_type: BusinessEventType = BusinessEventType.SALES_INVOICE

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.partner.partner_type is not PartnerType.CUSTOMER:
            raise InvalidDomainInputError("sales invoice requires customer partner")


@dataclass(frozen=True)
class ExpenseBill(BusinessEvent):
    """Vendor expense bill."""

    event_type: BusinessEventType = BusinessEventType.EXPENSE_BILL

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.partner.partner_type is not PartnerType.VENDOR:
            raise InvalidDomainInputError("expense bill requires vendor partner")


@dataclass(frozen=True)
class CashReceipt(BusinessEvent):
    """Cash receipt from customer."""

    event_type: BusinessEventType = BusinessEventType.CASH_RECEIPT

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.partner.partner_type is not PartnerType.CUSTOMER:
            raise InvalidDomainInputError("cash receipt requires customer partner")


@dataclass(frozen=True)
class VendorPayment(BusinessEvent):
    """Cash payment to vendor."""

    event_type: BusinessEventType = BusinessEventType.CASH_PAYMENT

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.partner.partner_type is not PartnerType.VENDOR:
            raise InvalidDomainInputError("vendor payment requires vendor partner")
