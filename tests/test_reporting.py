from decimal import Decimal

from src.reporting.partner_ledger import PartnerLedgerReport
from src.reporting.profit_and_loss import ProfitAndLossReport
from src.repositories.sqlite import SQLiteRepository
from src.services.cash_service import CashService
from src.services.commands import (
    CustomerReceiptCommand,
    ExpenseBillCommand,
    SalesInvoiceCommand,
    VendorPaymentCommand,
)
from src.services.purchase_service import PurchaseService
from src.services.sales_service import SalesService


def test_profit_and_loss_aggregates_revenue_and_expense(tmp_path) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    SalesService(repository).create_sales_invoice(
        SalesInvoiceCommand(
            entry_date=__import__("datetime").date(2026, 1, 1),
            partner_code="cust-001",
            partner_name="Client",
            amount=Decimal("100.00"),
            reference="INV-1",
        )
    )
    PurchaseService(repository).create_expense_bill(
        ExpenseBillCommand(
            entry_date=__import__("datetime").date(2026, 1, 2),
            partner_code="vend-001",
            partner_name="Vendor",
            amount=Decimal("30.00"),
            reference="BILL-1",
        )
    )

    report = ProfitAndLossReport().build(repository.list_journal_entries())

    assert report.revenue == Decimal("100.00")
    assert report.expense == Decimal("30.00")
    assert report.net_result == Decimal("70.00")


def test_partner_ledger_shows_customer_and_vendor_movements_and_balances(tmp_path) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    SalesService(repository).create_sales_invoice(
        SalesInvoiceCommand(
            entry_date=__import__("datetime").date(2026, 1, 1),
            partner_code="cust-001",
            partner_name="Client",
            amount=Decimal("100.00"),
            reference="INV-1",
        )
    )
    CashService(repository).register_customer_receipt(
        CustomerReceiptCommand(
            entry_date=__import__("datetime").date(2026, 1, 3),
            partner_code="cust-001",
            partner_name="Client",
            amount=Decimal("70.00"),
            reference="RCPT-1",
        )
    )
    PurchaseService(repository).create_expense_bill(
        ExpenseBillCommand(
            entry_date=__import__("datetime").date(2026, 1, 2),
            partner_code="vend-001",
            partner_name="Vendor",
            amount=Decimal("30.00"),
            reference="BILL-1",
        )
    )
    CashService(repository).register_vendor_payment(
        VendorPaymentCommand(
            entry_date=__import__("datetime").date(2026, 1, 4),
            partner_code="vend-001",
            partner_name="Vendor",
            amount=Decimal("20.00"),
            reference="PAY-1",
        )
    )

    report = PartnerLedgerReport().build(repository.list_journal_entries())

    assert len(report.movements) == 4
    balances = {item.partner_code: item.balance for item in report.balances}
    assert balances["CUST-001"] == Decimal("30.00")
    assert balances["VEND-001"] == Decimal("10.00")


def test_reports_return_empty_state_cleanly(tmp_path) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    entries = repository.list_journal_entries()

    pnl = ProfitAndLossReport().build(entries)
    ledger = PartnerLedgerReport().build(entries)

    assert pnl.revenue == Decimal("0.00")
    assert pnl.expense == Decimal("0.00")
    assert pnl.net_result == Decimal("0.00")
    assert ledger.movements == ()
    assert ledger.balances == ()
