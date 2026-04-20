"""Sales application service."""

from __future__ import annotations

from src.core.logging_config import get_logger
from src.domain.errors import DomainError
from src.domain.events import BusinessEventType, PartnerType, SalesInvoice
from src.repositories.sqlite import SQLiteRepository
from src.services.commands import SalesInvoiceCommand, ServiceResult
from src.services.workflow_support import ServiceWorkflow

logger = get_logger(__name__)


class SalesService:
    """Sales flow orchestration."""

    def __init__(self, repository: SQLiteRepository) -> None:
        self._workflow = ServiceWorkflow(repository)

    def create_sales_invoice(self, command: SalesInvoiceCommand) -> ServiceResult:
        try:
            event = SalesInvoice(
                entry_date=command.entry_date,
                partner=self._workflow.resolve_partner(
                    command.partner_code,
                    command.partner_name,
                    PartnerType.CUSTOMER,
                ),
                amount=command.amount,
                reference=self._workflow.resolve_reference(BusinessEventType.SALES_INVOICE, command.reference),
                description=command.description,
            )
        except DomainError:
            logger.warning(
                "Rejected sales command",
                extra={"partner_code": command.partner_code, "reference": command.reference},
            )
            raise
        return self._workflow.record_event(event)
