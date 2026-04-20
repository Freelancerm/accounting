from datetime import date
from decimal import Decimal

import pytest

from src.domain.errors import InvalidDomainInputError
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
from tests.fixtures import customer_partner


def test_partner_service_creates_partner(tmp_path, caplog) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    service = PartnerService(repository)

    with caplog.at_level("INFO"):
        partner = service.create_partner(
            CreatePartnerCommand(code="cust-001", name="Acme Client", partner_type=customer_partner().partner_type)
        )

    assert partner.code == "CUST-001"
    assert len(service.list_partners()) == 1
    assert "Partner created or updated" in caplog.text


def test_sales_service_records_document_and_journal(tmp_path) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    result = SalesService(repository).create_sales_invoice(
        SalesInvoiceCommand(
            entry_date=date(2026, 1, 5),
            partner_code="cust-001",
            partner_name="Acme Client",
            amount=Decimal("125.00"),
            reference="inv-1001",
        )
    )

    assert result.partner.code == "CUST-001"
    assert result.journal_entry.reference == "INV-1001"
    assert len(repository.list_business_documents()) == 1
    assert len(repository.list_journal_entries()) == 1


def test_sales_service_generates_partner_code_and_reference_for_new_partner(tmp_path) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    result = SalesService(repository).create_sales_invoice(
        SalesInvoiceCommand(
            entry_date=date(2026, 1, 5),
            partner_code="",
            partner_name="New Client",
            amount=Decimal("125.00"),
            reference="",
        )
    )

    assert result.partner.code == "CUST-001"
    assert result.journal_entry.reference == "INV-1001"
    assert repository.list_partners()[0].name == "New Client"


def test_sales_service_reuses_existing_partner_when_name_matches(tmp_path) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    partner_service = PartnerService(repository)
    partner_service.create_partner(
        CreatePartnerCommand(
            code="cust-001",
            name="Acme Client",
            partner_type=customer_partner().partner_type,
        )
    )

    result = SalesService(repository).create_sales_invoice(
        SalesInvoiceCommand(
            entry_date=date(2026, 1, 5),
            partner_code="",
            partner_name="acme client",
            amount=Decimal("125.00"),
            reference="",
        )
    )

    assert result.partner.code == "CUST-001"
    assert len(repository.list_partners()) == 1


def test_purchase_service_records_expense_bill(tmp_path) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    result = PurchaseService(repository).create_expense_bill(
        ExpenseBillCommand(
            entry_date=date(2026, 1, 6),
            partner_code="vend-001",
            partner_name="Cloud Vendor",
            amount=Decimal("45.00"),
            reference="bill-2001",
        )
    )

    assert result.journal_entry.event_type == "expense_bill"
    assert len(repository.list_business_documents()) == 1
    assert len(repository.list_journal_entries()[0].lines) == 2


def test_cash_service_records_customer_receipt_and_vendor_payment(tmp_path) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    service = CashService(repository)

    receipt = service.register_customer_receipt(
        CustomerReceiptCommand(
            entry_date=date(2026, 1, 7),
            partner_code="cust-001",
            partner_name="Acme Client",
            amount=Decimal("80.00"),
            reference="rcpt-3001",
        )
    )
    payment = service.register_vendor_payment(
        VendorPaymentCommand(
            entry_date=date(2026, 1, 8),
            partner_code="vend-001",
            partner_name="Cloud Vendor",
            amount=Decimal("20.00"),
            reference="pay-4001",
        )
    )

    assert receipt.journal_entry.event_type == "cash_receipt"
    assert payment.journal_entry.event_type == "cash_payment"
    assert len(repository.list_business_documents()) == 2
    assert len(repository.list_journal_entries()) == 2


def test_service_validation_error_bubbles_cleanly(tmp_path, caplog) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    service = SalesService(repository)

    with pytest.raises(InvalidDomainInputError, match="amount must be positive"):
        with caplog.at_level("WARNING"):
            service.create_sales_invoice(
                SalesInvoiceCommand(
                    entry_date=date(2026, 1, 5),
                    partner_code="cust-001",
                    partner_name="Acme Client",
                    amount=Decimal("0.00"),
                    reference="inv-1001",
                )
            )

    assert "Rejected sales command" in caplog.text


def test_partner_service_returns_name_suggestions(tmp_path) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    service = PartnerService(repository)
    service.create_partner(
        CreatePartnerCommand(code="cust-001", name="Acme Client", partner_type=customer_partner().partner_type)
    )
    service.create_partner(
        CreatePartnerCommand(code="cust-002", name="Acme Growth", partner_type=customer_partner().partner_type)
    )

    suggestions = service.suggest_partners("acme", customer_partner().partner_type)

    assert [partner.code for partner in suggestions] == ["CUST-001", "CUST-002"]


def test_transaction_rolls_back_when_journal_save_fails(tmp_path, monkeypatch) -> None:
    repository = SQLiteRepository(str(tmp_path / "accounting.db"))
    service = SalesService(repository)
    original_save = repository.journal_entries.save

    def broken_save(entry, connection=None):
        raise RuntimeError("boom")

    monkeypatch.setattr(repository.journal_entries, "save", broken_save)

    with pytest.raises(RuntimeError, match="boom"):
        service.create_sales_invoice(
            SalesInvoiceCommand(
                entry_date=date(2026, 1, 5),
                partner_code="cust-001",
                partner_name="Acme Client",
                amount=Decimal("125.00"),
                reference="inv-1001",
            )
        )

    monkeypatch.setattr(repository.journal_entries, "save", original_save)
    assert repository.list_partners() == []
    assert repository.list_business_documents() == []
    assert repository.list_journal_entries() == []
