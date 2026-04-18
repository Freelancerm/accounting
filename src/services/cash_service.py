"""Cash application service."""

from __future__ import annotations

from src.core.logging_config import get_logger
from src.domain.errors import DomainError
from src.domain.events import CashReceipt, PartnerType, VendorPayment
from src.repositories.sqlite import SQLiteRepository
from src.services.commands import CustomerReceiptCommand, ServiceResult, VendorPaymentCommand
from src.services.workflow_support import ServiceWorkflow

logger = get_logger(__name__)


class CashService:
    """Cash flow orchestration."""

    def __init__(self, repository: SQLiteRepository) -> None:
        self._workflow = ServiceWorkflow(repository)

    def register_customer_receipt(self, command: CustomerReceiptCommand) -> ServiceResult:
        try:
            event = CashReceipt(
                entry_date=command.entry_date,
                partner=self._workflow.build_partner(
                    command.partner_code,
                    command.partner_name,
                    PartnerType.CUSTOMER,
                ),
                amount=command.amount,
                reference=command.reference,
                description=command.description,
            )
        except DomainError:
            logger.warning(
                "Rejected customer receipt command",
                extra={"partner_code": command.partner_code, "reference": command.reference},
            )
            raise
        return self._workflow.record_event(event)

    def register_vendor_payment(self, command: VendorPaymentCommand) -> ServiceResult:
        try:
            event = VendorPayment(
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
        except DomainError:
            logger.warning(
                "Rejected vendor payment command",
                extra={"partner_code": command.partner_code, "reference": command.reference},
            )
            raise
        return self._workflow.record_event(event)
