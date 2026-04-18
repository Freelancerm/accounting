from datetime import date
from decimal import Decimal

from streamlit.testing.v1 import AppTest

from src.domain.models import BusinessEventType
from src.reporting.partner_ledger import build_partner_ledger
from src.reporting.profit_and_loss import build_profit_and_loss
from src.repositories.sqlite import SQLiteRepository
from src.services.accounting_service import AccountingService


def test_app_smoke_renders_title() -> None:
    app = AppTest.from_file("app.py")
    app.run()
    assert not app.exception
    assert app.title[0].value == "Minimal Accounting"


def test_posting_rules_and_reports(tmp_path) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    service = AccountingService(repository)

    sales = service.record_sales_invoice(
        entry_date=date(2026, 1, 1),
        partner_code="CUST-001",
        partner_name="Client",
        amount=Decimal("100.00"),
        reference="INV-1",
    )
    bill = service.record_expense_bill(
        entry_date=date(2026, 1, 2),
        partner_code="VEND-001",
        partner_name="Vendor",
        amount=Decimal("30.00"),
        reference="BILL-1",
    )
    receipt = service.record_cash_receipt(
        entry_date=date(2026, 1, 3),
        partner_code="CUST-001",
        partner_name="Client",
        amount=Decimal("70.00"),
        reference="RCPT-1",
    )
    payment = service.record_cash_payment(
        entry_date=date(2026, 1, 4),
        partner_code="VEND-001",
        partner_name="Vendor",
        amount=Decimal("20.00"),
        reference="PAY-1",
    )

    assert sales.event_type == BusinessEventType.SALES_INVOICE
    assert bill.event_type == BusinessEventType.EXPENSE_BILL
    assert receipt.event_type == BusinessEventType.CASH_RECEIPT
    assert payment.event_type == BusinessEventType.CASH_PAYMENT

    entries = service.list_entries()
    for entry in entries:
        debit_total = sum(line.debit for line in entry.lines)
        credit_total = sum(line.credit for line in entry.lines)
        assert debit_total == credit_total

    pnl = build_profit_and_loss(entries)
    ledger = build_partner_ledger(entries)

    assert float(pnl.loc[pnl["line_item"] == "Revenue", "amount"].iloc[0]) == 100.0
    assert float(pnl.loc[pnl["line_item"] == "Expense", "amount"].iloc[0]) == 30.0
    assert float(pnl.loc[pnl["line_item"] == "Net Result", "amount"].iloc[0]) == 70.0
    assert set(ledger["partner_code"]) == {"CUST-001", "VEND-001"}


def test_invalid_amount_rejected(tmp_path) -> None:
    service = AccountingService(SQLiteRepository(str(tmp_path / "accounting.db")))

    try:
        service.record_sales_invoice(
            entry_date=date(2026, 1, 1),
            partner_code="CUST-001",
            partner_name="Client",
            amount=Decimal("0.00"),
            reference="INV-0",
        )
    except ValueError as exc:
        assert str(exc) == "amount must be positive"
    else:
        raise AssertionError("expected ValueError")
