"""Fixed chart of accounts."""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.errors import InvalidDomainInputError


@dataclass(frozen=True)
class Account:
    """Fixed account definition."""

    code: str
    name: str

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise InvalidDomainInputError("account code required")
        if not self.name.strip():
            raise InvalidDomainInputError("account name required")


CASH = Account(code="1000", name="Cash")
ACCOUNTS_RECEIVABLE = Account(code="1100", name="Accounts Receivable")
ACCOUNTS_PAYABLE = Account(code="2000", name="Accounts Payable")
REVENUE = Account(code="4000", name="Revenue")
EXPENSE = Account(code="5000", name="Expense")

FIXED_CHART_OF_ACCOUNTS: tuple[Account, ...] = (
    CASH,
    ACCOUNTS_RECEIVABLE,
    ACCOUNTS_PAYABLE,
    REVENUE,
    EXPENSE,
)

ACCOUNT_BY_CODE: dict[str, Account] = {account.code: account for account in FIXED_CHART_OF_ACCOUNTS}
