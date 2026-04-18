"""Profit and loss reporting."""

from __future__ import annotations

import pandas as pd

from src.domain.models import JournalEntry


def build_profit_and_loss(entries: list[JournalEntry]) -> pd.DataFrame:
    """Return simplified P&L from fixed revenue and expense accounts."""
    revenue_total = sum(
        float(line.credit)
        for entry in entries
        for line in entry.lines
        if line.account_code == "4000"
    )
    expense_total = sum(
        float(line.debit)
        for entry in entries
        for line in entry.lines
        if line.account_code == "5000"
    )
    return pd.DataFrame(
        [
            {"line_item": "Revenue", "amount": revenue_total},
            {"line_item": "Expense", "amount": expense_total},
            {"line_item": "Net Result", "amount": revenue_total - expense_total},
        ]
    )
