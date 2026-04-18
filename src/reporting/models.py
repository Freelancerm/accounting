"""Report DTOs and view models."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ProfitAndLossLine:
    """Single line in simplified P&L."""

    line_item: str
    amount: Decimal


@dataclass(frozen=True)
class ProfitAndLossView:
    """Simplified P&L result."""

    lines: tuple[ProfitAndLossLine, ...]

    @property
    def revenue(self) -> Decimal:
        return next((line.amount for line in self.lines if line.line_item == "Revenue"), Decimal("0.00"))

    @property
    def expense(self) -> Decimal:
        return next((line.amount for line in self.lines if line.line_item == "Expense"), Decimal("0.00"))

    @property
    def net_result(self) -> Decimal:
        return next((line.amount for line in self.lines if line.line_item == "Net Result"), Decimal("0.00"))


@dataclass(frozen=True)
class PartnerLedgerMovement:
    """Single partner ledger movement row."""

    entry_date: str
    partner_code: str
    partner_name: str
    event_type: str
    reference: str
    account_code: str
    debit: Decimal
    credit: Decimal
    running_balance: Decimal


@dataclass(frozen=True)
class PartnerBalance:
    """Current partner balance summary."""

    partner_code: str
    partner_name: str
    balance: Decimal


@dataclass(frozen=True)
class PartnerLedgerView:
    """Partner ledger result."""

    movements: tuple[PartnerLedgerMovement, ...]
    balances: tuple[PartnerBalance, ...]
