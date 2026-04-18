"""Purchase application service."""

from __future__ import annotations

from src.core.logging_config import get_logger
from src.domain.errors import DomainError
from src.domain.events import ExpenseBill, PartnerType
from src.repositories.sqlite import SQLiteRepository
from src.services.commands import ExpenseBillCommand
from src.services.workflow_support import ServiceWorkflow

logger = get_logger(__name__)


class PurchaseService:
    """Purchase flow orchestration."""

    def __init__(self, repository: SQLiteRepository) -> None:
        self._workflow = ServiceWorkflow(repository)

    def create_expense_bill(self, command: ExpenseBillCommand):
        try:
            event = ExpenseBill(
                entry_date=command.entry_date,
                partner=self._workflow.build_partner(
                    command.partner_code,
                    command.partner_name,
                    PartnerType.VENDOR,
                ),
                amount=command.amount,
                reference=command.reference,
                description=command.description,
            )
            return self._workflow.record_event(event)
        except DomainError:
            logger.warning(
                "Rejected purchase command",
                extra={"partner_code": command.partner_code, "reference": command.reference},
            )
            raise
