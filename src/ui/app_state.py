"""UI bootstrap and service wiring."""

from __future__ import annotations

from dataclasses import dataclass

from src.repositories.sqlite import SQLiteRepository
from src.services.accounting_service import AccountingService
from src.services.cash_service import CashService
from src.services.partner_service import PartnerService
from src.services.purchase_service import PurchaseService
from src.services.sales_service import SalesService


@dataclass(frozen=True)
class AppServices:
    """Service container for UI layer."""

    accounting: AccountingService
    partners: PartnerService
    sales: SalesService
    purchases: PurchaseService
    cash: CashService


def get_app_services() -> AppServices:
    """Construct shared app services around one repository."""
    repository = SQLiteRepository()
    return AppServices(
        accounting=AccountingService(repository),
        partners=PartnerService(repository),
        sales=SalesService(repository),
        purchases=PurchaseService(repository),
        cash=CashService(repository),
    )
