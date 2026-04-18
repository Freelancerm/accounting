"""Partner ledger reporting service."""

from __future__ import annotations

from decimal import Decimal

import pandas as pd

from src.core.logging_config import get_logger
from src.domain.journal import JournalEntry
from src.reporting.models import PartnerBalance, PartnerLedgerMovement, PartnerLedgerView

logger = get_logger(__name__)


class PartnerLedgerReport:
    """Generate simplified partner ledger view."""

    def build(self, entries: list[JournalEntry]) -> PartnerLedgerView:
        """Build partner ledger from journal entries."""
        try:
            control_accounts = {"1100", "2000"}
            movements: list[PartnerLedgerMovement] = []
            balances_by_partner: dict[str, Decimal] = {}
            names_by_partner: dict[str, str] = {}

            posting_rows = []
            for entry in entries:
                for line in entry.lines:
                    if line.account_code in control_accounts:
                        posting_rows.append((entry, line))

            posting_rows.sort(key=lambda item: (item[0].partner_code, item[0].entry_date, item[0].reference))

            for entry, line in posting_rows:
                delta = _balance_delta(line.account_code, line.debit, line.credit)
                running_balance = balances_by_partner.get(entry.partner_code, Decimal("0.00")) + delta
                balances_by_partner[entry.partner_code] = running_balance
                names_by_partner[entry.partner_code] = entry.partner_name
                movements.append(
                    PartnerLedgerMovement(
                        entry_date=entry.entry_date.isoformat(),
                        partner_code=entry.partner_code,
                        partner_name=entry.partner_name,
                        event_type=entry.event_type,
                        reference=entry.reference,
                        account_code=line.account_code,
                        debit=line.debit,
                        credit=line.credit,
                        running_balance=running_balance,
                    )
                )

            balances = tuple(
                PartnerBalance(
                    partner_code=partner_code,
                    partner_name=names_by_partner[partner_code],
                    balance=balances_by_partner[partner_code],
                )
                for partner_code in sorted(balances_by_partner)
            )
            return PartnerLedgerView(movements=tuple(movements), balances=balances)
        except Exception:
            logger.exception("Partner ledger generation failed")
            raise


def build_partner_ledger(entries: list[JournalEntry]) -> pd.DataFrame:
    """Compatibility adapter for Streamlit rendering."""
    report = PartnerLedgerReport().build(entries)
    return pd.DataFrame(
        [
            {
                "entry_date": movement.entry_date,
                "partner_code": movement.partner_code,
                "partner_name": movement.partner_name,
                "event_type": movement.event_type,
                "reference": movement.reference,
                "account_code": movement.account_code,
                "debit": float(movement.debit),
                "credit": float(movement.credit),
                "running_balance": float(movement.running_balance),
            }
            for movement in report.movements
        ]
    )


def _balance_delta(account_code: str, debit: Decimal, credit: Decimal) -> Decimal:
    """Return positive open balance for AR and AP style control accounts."""
    if account_code == "1100":
        return debit - credit
    return credit - debit
