"""Shared helpers for thin application services."""

from __future__ import annotations

from src.core.logging_config import get_logger
from src.domain.errors import DomainError
from src.domain.events import BusinessEvent, Partner, PartnerType
from src.domain.journal import JournalEntry
from src.domain.posting_rules import PostingService
from src.repositories.sqlite import SQLiteRepository
from src.services.commands import ServiceResult

logger = get_logger(__name__)


class ServiceWorkflow:
    """Shared transactional workflow for event + posting persistence."""

    def __init__(self, repository: SQLiteRepository, posting_service: PostingService | None = None) -> None:
        self._repository = repository
        self._posting_service = posting_service or PostingService()

    def build_partner(self, code: str, name: str, partner_type: PartnerType) -> Partner:
        return Partner(code=code, name=name, partner_type=partner_type)

    def create_partner(self, partner: Partner) -> Partner:
        try:
            self._repository.upsert_partner(partner)
            logger.info(
                "Partner created or updated",
                extra={"partner_code": partner.code, "partner_type": partner.partner_type.value},
            )
            return partner
        except DomainError:
            logger.warning("Rejected partner command", extra={"partner_code": partner.code})
            raise
        except Exception:
            logger.exception("Unexpected partner service failure", extra={"partner_code": partner.code})
            raise

    def record_event(self, event: BusinessEvent) -> ServiceResult:
        try:
            with self._repository.database.connect() as connection:
                entry = self._posting_service.post(event)
                self._repository.partners.upsert(event.partner, connection=connection)
                document_id = self._repository.documents.save(event, connection=connection)
                self._repository.journal_entries.save(entry, connection=connection)
            logger.info(
                "Recorded service workflow",
                extra={
                    "event_type": event.event_type.value,
                    "partner_code": event.partner.code,
                    "reference": event.reference,
                    "amount": str(event.amount),
                },
            )
            return ServiceResult(partner=event.partner, document_id=document_id, journal_entry=entry)
        except DomainError:
            logger.warning(
                "Rejected service workflow",
                extra={"event_type": event.event_type.value, "partner_code": event.partner.code},
            )
            raise
        except Exception:
            logger.exception(
                "Unexpected service workflow failure",
                extra={"event_type": event.event_type.value, "partner_code": event.partner.code},
            )
            raise
