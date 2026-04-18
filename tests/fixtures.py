from datetime import date
from decimal import Decimal

from src.domain.events import (
    CashReceipt,
    ExpenseBill,
    Partner,
    PartnerType,
    SalesInvoice,
    VendorPayment,
)
from src.domain.posting_rules import PostingService


def build_partner(*, code: str, name: str, partner_type: PartnerType) -> Partner:
    return Partner(code=code, name=name, partner_type=partner_type)


def customer_partner() -> Partner:
    return build_partner(code="CUST-001", name="Acme Client", partner_type=PartnerType.CUSTOMER)


def vendor_partner() -> Partner:
    return build_partner(code="VEND-001", name="Cloud Vendor", partner_type=PartnerType.VENDOR)


def sales_invoice() -> SalesInvoice:
    return SalesInvoice(
        entry_date=date(2026, 1, 5),
        partner=customer_partner(),
        amount=Decimal("125.00"),
        reference="INV-1001",
        description="Consulting invoice",
    )


def expense_bill() -> ExpenseBill:
    return ExpenseBill(
        entry_date=date(2026, 1, 6),
        partner=vendor_partner(),
        amount=Decimal("45.00"),
        reference="BILL-2001",
        description="Hosting bill",
    )


def cash_receipt() -> CashReceipt:
    return CashReceipt(
        entry_date=date(2026, 1, 7),
        partner=customer_partner(),
        amount=Decimal("80.00"),
        reference="RCPT-3001",
        description="Customer payment",
    )


def vendor_payment() -> VendorPayment:
    return VendorPayment(
        entry_date=date(2026, 1, 8),
        partner=vendor_partner(),
        amount=Decimal("20.00"),
        reference="PAY-4001",
        description="Vendor payment",
    )


def sales_journal_entry():
    return PostingService().post(sales_invoice())
