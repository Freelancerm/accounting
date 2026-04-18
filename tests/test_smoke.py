from datetime import date
from decimal import Decimal

import pytest
from streamlit.testing.v1 import AppTest

from src.domain.accounts import (
    ACCOUNTS_PAYABLE,
    ACCOUNTS_RECEIVABLE,
    CASH,
    FIXED_CHART_OF_ACCOUNTS,
    REVENUE,
)
from src.domain.errors import InvalidDomainInputError, InvalidPostingError
from src.domain.events import (
    CashReceipt,
    ExpenseBill,
    Partner,
    PartnerType,
    SalesInvoice,
    VendorPayment,
)
from src.domain.journal import JournalEntry, JournalLine
from src.domain.posting_rules import PostingRules
from src.repositories.sqlite import SQLiteRepository
from src.services.accounting_service import AccountingService


def test_fixed_chart_of_accounts_is_stable() -> None:
    assert [account.code for account in FIXED_CHART_OF_ACCOUNTS] == [
        "1000",
        "1100",
        "2000",
        "4000",
        "5000",
    ]


def test_journal_entry_must_balance() -> None:
    with pytest.raises(InvalidPostingError, match="journal entry not balanced"):
        JournalEntry(
            entry_id="entry-1",
            entry_date=date(2026, 1, 1),
            event_type="sales_invoice",
            partner_code="CUST-001",
            partner_name="Client",
            reference="INV-1",
            description="test",
            lines=(
                JournalLine(account=ACCOUNTS_RECEIVABLE, debit=Decimal("100.00")),
                JournalLine(account=REVENUE, credit=Decimal("90.00")),
            ),
        )


def test_sales_invoice_posting_rule() -> None:
    entry = PostingRules().post_sales_invoice(
        SalesInvoice(
            entry_date=date(2026, 1, 1),
            partner=Partner("cust-001", "Client", PartnerType.CUSTOMER),
            amount=Decimal("100.00"),
            reference="inv-1",
        )
    )

    assert entry.event_type == "sales_invoice"
    assert [(line.account_code, line.debit, line.credit) for line in entry.lines] == [
        ("1100", Decimal("100.00"), Decimal("0.00")),
        ("4000", Decimal("0.00"), Decimal("100.00")),
    ]


def test_expense_bill_posting_rule() -> None:
    entry = PostingRules().post_expense_bill(
        ExpenseBill(
            entry_date=date(2026, 1, 2),
            partner=Partner("vend-001", "Vendor", PartnerType.VENDOR),
            amount=Decimal("30.00"),
            reference="bill-1",
        )
    )

    assert [(line.account_code, line.debit, line.credit) for line in entry.lines] == [
        ("5000", Decimal("30.00"), Decimal("0.00")),
        ("2000", Decimal("0.00"), Decimal("30.00")),
    ]


def test_cash_receipt_posting_rule() -> None:
    entry = PostingRules().post_cash_receipt(
        CashReceipt(
            entry_date=date(2026, 1, 3),
            partner=Partner("cust-001", "Client", PartnerType.CUSTOMER),
            amount=Decimal("70.00"),
            reference="rcpt-1",
        )
    )

    assert [(line.account_code, line.debit, line.credit) for line in entry.lines] == [
        ("1000", Decimal("70.00"), Decimal("0.00")),
        ("1100", Decimal("0.00"), Decimal("70.00")),
    ]


def test_vendor_payment_posting_rule() -> None:
    entry = PostingRules().post_vendor_payment(
        VendorPayment(
            entry_date=date(2026, 1, 4),
            partner=Partner("vend-001", "Vendor", PartnerType.VENDOR),
            amount=Decimal("20.00"),
            reference="pay-1",
        )
    )

    assert [(line.account_code, line.debit, line.credit) for line in entry.lines] == [
        ("2000", Decimal("20.00"), Decimal("0.00")),
        ("1000", Decimal("0.00"), Decimal("20.00")),
    ]


def test_invalid_partner_type_rejected_for_sales_invoice() -> None:
    with pytest.raises(InvalidDomainInputError, match="sales invoice requires customer partner"):
        SalesInvoice(
            entry_date=date(2026, 1, 1),
            partner=Partner("vend-001", "Vendor", PartnerType.VENDOR),
            amount=Decimal("100.00"),
            reference="INV-1",
        )


def test_invalid_zero_amount_rejected() -> None:
    with pytest.raises(InvalidDomainInputError, match="amount must be positive"):
        ExpenseBill(
            entry_date=date(2026, 1, 1),
            partner=Partner("vend-001", "Vendor", PartnerType.VENDOR),
            amount=Decimal("0.00"),
            reference="BILL-1",
        )


def test_journal_line_cannot_have_both_debit_and_credit() -> None:
    with pytest.raises(InvalidPostingError, match="journal line cannot have both debit and credit"):
        JournalLine(
            account=CASH,
            debit=Decimal("10.00"),
            credit=Decimal("10.00"),
        )


def test_accounting_service_logs_and_persists_sales_invoice(tmp_path, caplog) -> None:
    service = AccountingService(SQLiteRepository(str(tmp_path / "accounting.db")))

    with caplog.at_level("INFO"):
        entry = service.record_sales_invoice(
            entry_date=date(2026, 1, 5),
            partner_code="cust-001",
            partner_name="Client",
            amount=Decimal("125.00"),
            reference="inv-1001",
        )

    assert entry.partner_code == "CUST-001"
    assert entry.reference == "INV-1001"
    assert "Recorded accounting event" in caplog.text
    assert len(service.list_entries()) == 1


def test_app_smoke_renders_title() -> None:
    app = AppTest.from_file("app.py")
    app.run()
    assert not app.exception
    assert app.title[0].value == "Minimal Accounting"
