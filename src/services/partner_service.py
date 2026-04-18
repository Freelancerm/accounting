"""Partner application service."""

from __future__ import annotations

from src.core.logging_config import get_logger
from src.domain.errors import DomainError
from src.domain.events import Partner
from src.repositories.sqlite import SQLiteRepository
from src.services.commands import CreatePartnerCommand
from src.services.workflow_support import ServiceWorkflow

logger = get_logger(__name__)


class PartnerService:
    """Partner orchestration."""

    def __init__(self, repository: SQLiteRepository) -> None:
        self._workflow = ServiceWorkflow(repository)
        self._repository = repository

    def create_partner(self, command: CreatePartnerCommand) -> Partner:
        try:
            partner = self._workflow.build_partner(command.code, command.name, command.partner_type)
        except DomainError:
            logger.warning("Rejected partner command", extra={"partner_code": command.code})
            raise
        return self._workflow.create_partner(partner)

    def list_partners(self) -> list[Partner]:
        return self._repository.list_partners()
