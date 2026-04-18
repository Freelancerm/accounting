from datetime import date
from decimal import Decimal

from src.reporting.partner_ledger import PartnerLedgerReport
from src.reporting.profit_and_loss import ProfitAndLossReport
from src.repositories.sqlite import SQLiteRepository
from src.services.cash_service import CashService
from src.services.commands import (
    CreatePartnerCommand,
    CustomerReceiptCommand,
    ExpenseBillCommand,
    SalesInvoiceCommand,
    VendorPaymentCommand,
)
from src.services.partner_service import PartnerService
from src.services.purchase_service import PurchaseService
from src.services.sales_service import SalesService
from tests.fixtures import customer_partner, vendor_partner


def test_end_to_end_business_flow_persists_and_reports_correctly(tmp_path) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    partner_service = PartnerService(repository)
    sales_service = SalesService(repository)
    purchase_service = PurchaseService(repository)
    cash_service = CashService(repository)

    partner_service.create_partner(
        CreatePartnerCommand(
            code=customer_partner().code,
            name=customer_partner().name,
            partner_type=customer_partner().partner_type,
        )
    )
    partner_service.create_partner(
        CreatePartnerCommand(
            code=vendor_partner().code,
            name=vendor_partner().name,
            partner_type=vendor_partner().partner_type,
        )
    )

    sales_service.create_sales_invoice(
        SalesInvoiceCommand(
            entry_date=date(2026, 1, 1),
            partner_code="CUST-001",
            partner_name="Acme Client",
            amount=Decimal("250.00"),
            reference="INV-1001",
        )
    )
    purchase_service.create_expense_bill(
        ExpenseBillCommand(
            entry_date=date(2026, 1, 2),
            partner_code="VEND-001",
            partner_name="Cloud Vendor",
            amount=Decimal("90.00"),
            reference="BILL-2001",
        )
    )
    cash_service.register_customer_receipt(
        CustomerReceiptCommand(
            entry_date=date(2026, 1, 3),
            partner_code="CUST-001",
            partner_name="Acme Client",
            amount=Decimal("200.00"),
            reference="RCPT-3001",
        )
    )
    cash_service.register_vendor_payment(
        VendorPaymentCommand(
            entry_date=date(2026, 1, 4),
            partner_code="VEND-001",
            partner_name="Cloud Vendor",
            amount=Decimal("40.00"),
            reference="PAY-4001",
        )
    )

    partners = repository.list_partners()
    documents = repository.list_business_documents()
    journal_entries = repository.list_journal_entries()
    pnl = ProfitAndLossReport().build(journal_entries)
    ledger = PartnerLedgerReport().build(journal_entries)

    assert len(partners) == 2
    assert len(documents) == 4
    assert len(journal_entries) == 4
    assert pnl.revenue == Decimal("250.00")
    assert pnl.expense == Decimal("90.00")
    assert pnl.net_result == Decimal("160.00")

    balances = {row.partner_code: row.balance for row in ledger.balances}
    assert balances["CUST-001"] == Decimal("50.00")
    assert balances["VEND-001"] == Decimal("50.00")


def test_invalid_flow_does_not_persist_partial_records(tmp_path) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    sales_service = SalesService(repository)

    try:
        sales_service.create_sales_invoice(
            SalesInvoiceCommand(
                entry_date=date(2026, 1, 1),
                partner_code="",
                partner_name="Acme Client",
                amount=Decimal("100.00"),
                reference="INV-1001",
            )
        )
    except Exception:
        pass
    else:
        raise AssertionError("expected invalid flow to fail")

    assert repository.list_partners() == []
    assert repository.list_business_documents() == []
    assert repository.list_journal_entries() == []
