"""Profit and Loss reporting service."""

from __future__ import annotations

from decimal import Decimal

import pandas as pd

from src.core.logging_config import get_logger
from src.domain.journal import JournalEntry
from src.reporting.models import ProfitAndLossLine, ProfitAndLossView

logger = get_logger(__name__)


class ProfitAndLossReport:
    """Generate simplified Profit and Loss view."""

    @staticmethod
    def build(entries: list[JournalEntry]) -> ProfitAndLossView:
        """Build report from journal entries."""
        try:
            revenue_total = sum(
                (line.credit for entry in entries for line in entry.lines if line.account_code == "4000"),
                start=Decimal("0.00"),
            )
            expense_total = sum(
                (line.debit for entry in entries for line in entry.lines if line.account_code == "5000"),
                start=Decimal("0.00"),
            )
            return ProfitAndLossView(
                lines=(
                    ProfitAndLossLine("Revenue", revenue_total),
                    ProfitAndLossLine("Expense", expense_total),
                    ProfitAndLossLine("Net Result", revenue_total - expense_total),
                )
            )
        except Exception:
            logger.exception("Profit and Loss generation failed")
            raise


def build_profit_and_loss(entries: list[JournalEntry]) -> pd.DataFrame:
    """Compatibility adapter for Streamlit rendering."""
    report = ProfitAndLossReport().build(entries)
    return pd.DataFrame(
        [{"line_item": line.line_item, "amount": float(line.amount)} for line in report.lines]
    )
