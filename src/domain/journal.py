"""Journal entities and validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from src.domain.accounts import ACCOUNT_BY_CODE, Account
from src.domain.errors import InvalidDomainInputError, InvalidPostingError


ZERO = Decimal("0.00")


@dataclass(frozen=True)
class JournalLine:
    """Single debit or credit line in journal entry."""

    account: Account
    debit: Decimal = ZERO
    credit: Decimal = ZERO

    def __post_init__(self) -> None:
        debit = self._normalize(self.debit)
        credit = self._normalize(self.credit)

        object.__setattr__(self, "debit", debit)
        object.__setattr__(self, "credit", credit)

        if self.account.code not in ACCOUNT_BY_CODE:
            raise InvalidDomainInputError("unknown account code")
        if debit < ZERO or credit < ZERO:
            raise InvalidPostingError("debit and credit must be non-negative")
        if debit == ZERO and credit == ZERO:
            raise InvalidPostingError("journal line must have debit or credit")
        if debit > ZERO and credit > ZERO:
            raise InvalidPostingError("journal line cannot have both debit and credit")

    @property
    def account_code(self) -> str:
        """Expose account code for reporting and persistence."""
        return self.account.code

    @property
    def account_name(self) -> str:
        """Expose account name for reporting and persistence."""
        return self.account.name

    @staticmethod
    def _normalize(amount: Decimal) -> Decimal:
        return amount.quantize(Decimal("0.01"))


@dataclass(frozen=True)
class JournalEntry:
    """Balanced journal entry."""

    entry_id: str
    entry_date: date
    event_type: str
    partner_code: str
    partner_name: str
    reference: str
    description: str
    lines: tuple[JournalLine, ...]

    def __post_init__(self) -> None:
        if not self.entry_id.strip():
            raise InvalidDomainInputError("entry id required")
        if not self.partner_code.strip():
            raise InvalidDomainInputError("partner code required")
        if not self.partner_name.strip():
            raise InvalidDomainInputError("partner name required")
        if not self.reference.strip():
            raise InvalidDomainInputError("reference required")
        if not self.lines:
            raise InvalidPostingError("journal entry must have lines")
        self.validate_balanced()

    @property
    def amount(self) -> Decimal:
        """Return total debit amount for entry."""
        return self.total_debits

    @property
    def total_debits(self) -> Decimal:
        """Return entry debit total."""
        return sum((line.debit for line in self.lines), start=ZERO)

    @property
    def total_credits(self) -> Decimal:
        """Return entry credit total."""
        return sum((line.credit for line in self.lines), start=ZERO)

    def validate_balanced(self) -> None:
        """Ensure journal entry balances exactly."""
        if self.total_debits != self.total_credits:
            raise InvalidPostingError("journal entry not balanced")

    def to_journal_row(self) -> dict[str, object]:
        """Serialize high-level journal row."""
        return {
            "entry_id": self.entry_id,
            "entry_date": self.entry_date.isoformat(),
            "event_type": self.event_type,
            "partner_code": self.partner_code,
            "partner_name": self.partner_name,
            "amount": float(self.amount),
            "reference": self.reference,
            "description": self.description,
        }

    def to_posting_rows(self) -> list[dict[str, object]]:
        """Serialize posting lines for reporting and UI tables."""
        rows: list[dict[str, object]] = []
        for line in self.lines:
            rows.append(
                {
                    "entry_id": self.entry_id,
                    "entry_date": self.entry_date.isoformat(),
                    "event_type": self.event_type,
                    "partner_code": self.partner_code,
                    "partner_name": self.partner_name,
                    "reference": self.reference,
                    "account_code": line.account_code,
                    "account_name": line.account_name,
                    "debit": float(line.debit),
                    "credit": float(line.credit),
                }
            )
        return rows
