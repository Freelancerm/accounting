import sqlite3

from src.domain.accounts import FIXED_CHART_OF_ACCOUNTS
from src.repositories.database import SQLiteDatabase
from src.repositories.documents import BusinessDocumentRepository
from src.repositories.journal_entries import JournalEntryRepository
from src.repositories.partners import PartnerRepository
from tests.fixtures import customer_partner, expense_bill, sales_invoice, sales_journal_entry


def test_database_bootstrap_seeds_fixed_accounts(tmp_path) -> None:
    database = SQLiteDatabase(str(tmp_path / "accounting.db"))

    with database.connect() as connection:
        rows = connection.execute("SELECT code, name FROM accounts ORDER BY code").fetchall()

    assert [(row["code"], row["name"]) for row in rows] == [
        (account.code, account.name) for account in FIXED_CHART_OF_ACCOUNTS
    ]


def test_partner_repository_round_trip(tmp_path) -> None:
    repository = PartnerRepository(SQLiteDatabase(str(tmp_path / "accounting.db")))
    repository.upsert(customer_partner())

    partners = repository.list_all()

    assert len(partners) == 1
    assert partners[0].code == "CUST-001"
    assert partners[0].name == "Acme Client"


def test_business_document_repository_round_trip(tmp_path) -> None:
    database = SQLiteDatabase(str(tmp_path / "accounting.db"))
    partners = PartnerRepository(database)
    documents = BusinessDocumentRepository(database)
    partner = customer_partner()
    partners.upsert(partner)

    document_id = documents.save(sales_invoice(), document_id="doc-1")
    saved_documents = documents.list_all({partner.code: partner})

    assert document_id == "doc-1"
    assert len(saved_documents) == 1
    saved_id, event = saved_documents[0]
    assert saved_id == "doc-1"
    assert event.reference == "INV-1001"
    assert event.partner.code == "CUST-001"


def test_journal_entry_repository_round_trip(tmp_path) -> None:
    database = SQLiteDatabase(str(tmp_path / "accounting.db"))
    partners = PartnerRepository(database)
    journals = JournalEntryRepository(database)
    partner = customer_partner()
    partners.upsert(partner)

    entry = sales_journal_entry()
    journals.save(entry)
    saved_entries = journals.list_all()

    assert len(saved_entries) == 1
    assert saved_entries[0].entry_id == entry.entry_id
    assert [(line.account_code, line.debit, line.credit) for line in saved_entries[0].lines] == [
        ("1100", entry.lines[0].debit, entry.lines[0].credit),
        ("4000", entry.lines[1].debit, entry.lines[1].credit),
    ]


def test_repository_logs_and_raises_on_sqlite_error(tmp_path, caplog) -> None:
    database = SQLiteDatabase(str(tmp_path / "accounting.db"))
    partners = PartnerRepository(database)

    with database.connect() as connection:
        connection.execute("DROP TABLE partners")

    try:
        with caplog.at_level("ERROR"):
            partners.upsert(customer_partner())
    except sqlite3.Error:
        assert "Partner repository write failed" in caplog.text
    else:
        raise AssertionError("expected sqlite3.Error")


def test_multiple_repositories_can_store_separate_records(tmp_path) -> None:
    database = SQLiteDatabase(str(tmp_path / "accounting.db"))
    partners = PartnerRepository(database)
    documents = BusinessDocumentRepository(database)
    journals = JournalEntryRepository(database)

    partner = customer_partner()
    partners.upsert(partner)
    documents.save(sales_invoice(), document_id="doc-sales")
    documents.save(expense_bill(), document_id="doc-expense")
    journals.save(sales_journal_entry())

    assert len(partners.list_all()) == 1
    assert len(documents.list_all({partner.code: partner, "VEND-001": expense_bill().partner})) == 2
    assert len(journals.list_all()) == 1
