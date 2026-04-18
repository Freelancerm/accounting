"""Streamlit view for minimal accounting app."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import streamlit as st

from src.core.settings import get_settings
from src.domain.models import BusinessEventType, CHART_OF_ACCOUNTS, JournalEntry
from src.reporting.partner_ledger import build_partner_ledger
from src.reporting.profit_and_loss import build_profit_and_loss
from src.repositories.sqlite import SQLiteRepository
from src.services.accounting_service import AccountingService


def render_app() -> None:
    """Render full Streamlit page."""
    settings = get_settings()
    st.set_page_config(page_title=settings.app_title, layout="wide")

    st.title(settings.app_title)
    st.caption("Business events -> balanced postings -> Profit and Loss + partner ledger.")

    service = AccountingService(SQLiteRepository())
    service.bootstrap_sample_data()
    entries = service.list_entries()

    left, right = st.columns([1, 1])
    with left:
        _render_event_form(service)
    with right:
        _render_summary(entries)

    tabs = st.tabs(["Business Events", "Journal Postings", "Reports", "Partners"])

    with tabs[0]:
        st.subheader("Recorded Events")
        st.dataframe([entry.to_journal_row() for entry in entries], use_container_width=True)

    with tabs[1]:
        st.subheader("Balanced Journal Postings")
        posting_rows = [row for entry in entries for row in entry.to_posting_rows()]
        st.dataframe(posting_rows, use_container_width=True)
        st.caption(f"Fixed chart of accounts: {CHART_OF_ACCOUNTS}")

    with tabs[2]:
        pnl_col, ledger_col = st.columns(2)
        with pnl_col:
            st.subheader("Profit and Loss")
            st.dataframe(build_profit_and_loss(entries), use_container_width=True)
        with ledger_col:
            st.subheader("Partner Ledger")
            st.dataframe(build_partner_ledger(entries), use_container_width=True)

    with tabs[3]:
        st.subheader("Partners")
        partners = [
            {
                "code": partner.code,
                "name": partner.name,
                "partner_type": partner.partner_type.value,
            }
            for partner in service.list_partners()
        ]
        st.dataframe(partners, use_container_width=True)


def _render_event_form(service: AccountingService) -> None:
    st.subheader("Create Business Event")
    with st.form("journal_entry_form"):
        entry_date = st.date_input("Date", value=date.today())
        event_type = st.selectbox(
            "Business Event",
            options=[event.value for event in BusinessEventType],
            format_func=lambda value: value.replace("_", " ").title(),
        )
        partner_code = st.text_input("Partner Code", placeholder="CUST-001 or VEND-001")
        partner_name = st.text_input("Partner Name", placeholder="Acme Client")
        amount = st.number_input("Amount", min_value=0.0, value=0.0, step=100.0, format="%.2f")
        reference = st.text_input("Reference", placeholder="INV-1001")
        description = st.text_input("Description", placeholder="Optional note")
        submitted = st.form_submit_button("Post Event")

        if submitted:
            try:
                _submit_event(
                    service=service,
                    event_type=BusinessEventType(event_type),
                    entry_date=entry_date,
                    partner_code=partner_code,
                    partner_name=partner_name,
                    amount=Decimal(f"{amount:.2f}"),
                    reference=reference,
                    description=description,
                )
                st.success("Balanced journal entry posted")
            except ValueError as exc:
                st.error(str(exc))


def _render_summary(entries: list[JournalEntry]) -> None:
    pnl = build_profit_and_loss(entries)
    revenue = float(pnl.loc[pnl["line_item"] == "Revenue", "amount"].iloc[0])
    expense = float(pnl.loc[pnl["line_item"] == "Expense", "amount"].iloc[0])
    net_result = float(pnl.loc[pnl["line_item"] == "Net Result", "amount"].iloc[0])

    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Revenue", f"${revenue:,.2f}")
    col2.metric("Expense", f"${expense:,.2f}")
    col3.metric("Net Result", f"${net_result:,.2f}")


def _submit_event(
    *,
    service: AccountingService,
    event_type: BusinessEventType,
    entry_date: date,
    partner_code: str,
    partner_name: str,
    amount: Decimal,
    reference: str,
    description: str,
) -> None:
    if event_type == BusinessEventType.SALES_INVOICE:
        service.record_sales_invoice(
            entry_date=entry_date,
            partner_code=partner_code,
            partner_name=partner_name,
            amount=amount,
            reference=reference,
            description=description,
        )
        return
    if event_type == BusinessEventType.EXPENSE_BILL:
        service.record_expense_bill(
            entry_date=entry_date,
            partner_code=partner_code,
            partner_name=partner_name,
            amount=amount,
            reference=reference,
            description=description,
        )
        return
    if event_type == BusinessEventType.CASH_RECEIPT:
        service.record_cash_receipt(
            entry_date=entry_date,
            partner_code=partner_code,
            partner_name=partner_name,
            amount=amount,
            reference=reference,
            description=description,
        )
        return
    service.record_cash_payment(
        entry_date=entry_date,
        partner_code=partner_code,
        partner_name=partner_name,
        amount=amount,
        reference=reference,
        description=description,
    )
