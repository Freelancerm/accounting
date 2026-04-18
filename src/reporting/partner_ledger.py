"""Partner ledger reporting."""

from __future__ import annotations

import pandas as pd

from src.domain.models import JournalEntry


def build_partner_ledger(entries: list[JournalEntry]) -> pd.DataFrame:
    """Return partner-level movements for customer and vendor control accounts."""
    rows: list[dict[str, object]] = []
    control_accounts = {"1100", "2000"}
    for entry in entries:
        for line in entry.lines:
            if line.account_code not in control_accounts:
                continue
            rows.append(
                {
                    "entry_date": entry.entry_date.isoformat(),
                    "partner_code": entry.partner_code,
                    "partner_name": entry.partner_name,
                    "event_type": entry.event_type.value,
                    "reference": entry.reference,
                    "account_code": line.account_code,
                    "debit": float(line.debit),
                    "credit": float(line.credit),
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=[
                "entry_date",
                "partner_code",
                "partner_name",
                "event_type",
                "reference",
                "account_code",
                "debit",
                "credit",
                "running_balance",
            ]
        )

    frame = pd.DataFrame(rows).sort_values(["partner_code", "entry_date", "reference"])
    frame["signed_amount"] = frame.apply(
        lambda row: row["debit"] - row["credit"],
        axis=1,
    )
    frame["running_balance"] = frame.groupby("partner_code")["signed_amount"].cumsum()
    return frame.drop(columns=["signed_amount"])
