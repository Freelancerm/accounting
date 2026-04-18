"""Compatibility facade around explicit SQLite repositories."""

from __future__ import annotations

from src.domain.events import BusinessEvent, Partner
from src.domain.journal import JournalEntry
from src.repositories.database import SQLiteDatabase
from src.repositories.documents import BusinessDocumentRepository
from src.repositories.journal_entries import JournalEntryRepository
from src.repositories.partners import PartnerRepository


class SQLiteRepository:
    """Small facade used by existing app/service code."""

    def __init__(self, database_path: str = "data/accounting.db") -> None:
        self.database = SQLiteDatabase(database_path)
        self.partners = PartnerRepository(self.database)
        self.documents = BusinessDocumentRepository(self.database)
        self.journal_entries = JournalEntryRepository(self.database)

    def upsert_partner(self, partner: Partner) -> None:
        self.partners.upsert(partner)

    def list_partners(self) -> list[Partner]:
        return self.partners.list_all()

    def save_business_document(self, event: BusinessEvent, document_id: str | None = None) -> str:
        return self.documents.save(event, document_id=document_id)

    def list_business_documents(self) -> list[tuple[str, BusinessEvent]]:
        partners = {partner.code: partner for partner in self.partners.list_all()}
        return self.documents.list_all(partners)

    def save_journal_entry(self, entry: JournalEntry) -> None:
        self.journal_entries.save(entry)

    def list_journal_entries(self) -> list[JournalEntry]:
        return self.journal_entries.list_all()
