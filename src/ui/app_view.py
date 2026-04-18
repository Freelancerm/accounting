"""Streamlit UI shell for minimal accounting app."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import streamlit as st

from src.core.settings import get_settings
from src.domain.events import BusinessEventType, PartnerType
from src.reporting.partner_ledger import PartnerLedgerReport
from src.reporting.profit_and_loss import ProfitAndLossReport
from src.services.commands import (
    CreatePartnerCommand,
    CustomerReceiptCommand,
    ExpenseBillCommand,
    SalesInvoiceCommand,
    VendorPaymentCommand,
)
from src.ui.app_state import AppServices, get_app_services
from src.ui.helpers import queue_notification, render_empty_state, render_error, render_notification, render_table


def render_app() -> None:
    """Render full Streamlit application shell."""
    settings = get_settings()
    st.set_page_config(page_title=settings.app_title, layout="wide")

    services = get_app_services()
    services.accounting.bootstrap_sample_data()

    st.title(settings.app_title)
    st.caption("Minimal accounting review app: partners, transactions, and reports.")
    render_notification()

    section = st.sidebar.radio(
        "Navigation",
        options=["Transactions", "Partners", "Reports"],
        key="main_navigation",
    )

    entries = services.accounting.list_entries()
    _render_summary(entries)

    if section == "Transactions":
        _render_transactions_section(services, entries)
        return
    if section == "Partners":
        _render_partners_section(services)
        return
    _render_reports_section(entries)


def _render_summary(entries) -> None:
    report = ProfitAndLossReport().build(entries)
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Revenue", f"${float(report.revenue):,.2f}")
    col2.metric("Expense", f"${float(report.expense):,.2f}")
    col3.metric("Net Result", f"${float(report.net_result):,.2f}")


def _render_transactions_section(services: AppServices, entries) -> None:
    form_col, data_col = st.columns([1, 2])

    with form_col:
        _render_transaction_form(services)

    with data_col:
        event_tab, journal_tab = st.tabs(["Business Events", "Journal Postings"])

        with event_tab:
            st.subheader("Recorded Events")
            render_table(
                [entry.to_journal_row() for entry in entries],
                empty_message="No business events yet.",
            )

        with journal_tab:
            st.subheader("Journal Postings")
            render_table(
                [row for entry in entries for row in entry.to_posting_rows()],
                empty_message="No journal postings yet.",
            )


def _render_partners_section(services: AppServices) -> None:
    form_col, list_col = st.columns([1, 2])

    with form_col:
        st.subheader("Create Partner")
        with st.form("partner_form"):
            partner_code = st.text_input("Partner Code", placeholder="CUST-001")
            partner_name = st.text_input("Partner Name", placeholder="Acme Client")
            partner_type = st.selectbox(
                "Partner Type",
                options=[partner_type.value for partner_type in PartnerType],
                format_func=lambda value: value.title(),
            )
            submitted = st.form_submit_button("Save Partner")

            if submitted:
                try:
                    services.partners.create_partner(
                        CreatePartnerCommand(
                            code=partner_code,
                            name=partner_name,
                            partner_type=PartnerType(partner_type),
                        )
                    )
                    queue_notification("success", "Partner saved")
                    st.rerun()
                except Exception as error:
                    render_error("Could not save partner", error)

    with list_col:
        st.subheader("Partners")
        filter_value = st.selectbox(
            "Filter by Type",
            options=["all", *[partner_type.value for partner_type in PartnerType]],
            format_func=lambda value: "All" if value == "all" else value.title(),
            key="partner_type_filter",
        )
        partners = [
            {
                "code": partner.code,
                "name": partner.name,
                "partner_type": partner.partner_type.value,
            }
            for partner in services.partners.list_partners()
            if filter_value == "all" or partner.partner_type.value == filter_value
        ]
        render_table(
            partners,
            empty_message=(
                "No partners yet."
                if filter_value == "all"
                else f"No {filter_value} partners yet."
            ),
        )


def _render_reports_section(entries) -> None:
    report_tab, ledger_tab = st.tabs(["Profit and Loss", "Partner Ledger"])

    with report_tab:
        st.subheader("Profit and Loss")
        pnl_report = ProfitAndLossReport().build(entries)
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Revenue", f"${float(pnl_report.revenue):,.2f}")
        metric_col2.metric("Expense", f"${float(pnl_report.expense):,.2f}")
        metric_col3.metric("Net Result", f"${float(pnl_report.net_result):,.2f}")
        render_table(
            [
                {"line_item": line.line_item, "amount": float(line.amount)}
                for line in pnl_report.lines
            ],
            empty_message="No Profit and Loss data yet.",
        )

    with ledger_tab:
        st.subheader("Partner Ledger")
        ledger_report = PartnerLedgerReport().build(entries)
        ledger_partner_filter = st.selectbox(
            "Filter Ledger by Partner",
            options=["all", *[balance.partner_code for balance in ledger_report.balances]],
            format_func=lambda value: "All Partners" if value == "all" else value,
            key="ledger_partner_filter",
        )
        movement_rows = [
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
            for movement in ledger_report.movements
            if ledger_partner_filter == "all" or movement.partner_code == ledger_partner_filter
        ]
        render_table(
            movement_rows,
            empty_message=(
                "No partner ledger data yet."
                if ledger_partner_filter == "all"
                else f"No ledger movements for {ledger_partner_filter}."
            ),
        )

        filtered_balances = [
            {
                "partner_code": balance.partner_code,
                "partner_name": balance.partner_name,
                "balance": float(balance.balance),
            }
            for balance in ledger_report.balances
            if ledger_partner_filter == "all" or balance.partner_code == ledger_partner_filter
        ]

        if filtered_balances:
            st.caption("Current partner balances")
            render_table(
                filtered_balances,
                empty_message="No partner balances yet.",
            )
        else:
            render_empty_state(
                "No partner balances yet."
                if ledger_partner_filter == "all"
                else f"No partner balance for {ledger_partner_filter}."
            )


def _render_transaction_form(services: AppServices) -> None:
    st.subheader("Create Transaction")
    with st.form("transaction_form"):
        entry_date = st.date_input("Date", value=date.today())
        event_type = st.selectbox(
            "Business Event",
            options=[event.value for event in BusinessEventType],
            format_func=lambda value: value.replace("_", " ").title(),
        )
        available_partners = _partner_options_for_event(services, BusinessEventType(event_type))
        partner_selection = st.selectbox(
            "Existing Partner (Optional)",
            options=["manual", *available_partners],
            format_func=lambda value: "Manual Entry" if value == "manual" else value,
            key="transaction_partner_selection",
        )
        partner_code = st.text_input("Partner Code", placeholder="CUST-001 or VEND-001")
        partner_name = st.text_input("Partner Name", placeholder="Acme Client")
        amount = st.number_input("Amount", min_value=0.0, value=0.0, step=100.0, format="%.2f")
        reference = st.text_input("Reference", placeholder="INV-1001")
        description = st.text_input("Description", placeholder="Optional note")
        submitted = st.form_submit_button("Post Transaction")

        if submitted:
            try:
                resolved_partner_code, resolved_partner_name = _resolve_partner_input(
                    services=services,
                    partner_selection=partner_selection,
                    fallback_code=partner_code,
                    fallback_name=partner_name,
                )
                _submit_transaction(
                    services=services,
                    event_type=BusinessEventType(event_type),
                    entry_date=entry_date,
                    partner_code=resolved_partner_code,
                    partner_name=resolved_partner_name,
                    amount=Decimal(f"{amount:.2f}"),
                    reference=reference,
                    description=description,
                )
                queue_notification("success", "Balanced journal entry posted")
                st.rerun()
            except Exception as error:
                render_error("Could not post transaction", error)


def _submit_transaction(
    *,
    services: AppServices,
    event_type: BusinessEventType,
    entry_date: date,
    partner_code: str,
    partner_name: str,
    amount: Decimal,
    reference: str,
    description: str,
) -> None:
    if event_type == BusinessEventType.SALES_INVOICE:
        services.sales.create_sales_invoice(
            SalesInvoiceCommand(
                entry_date=entry_date,
                partner_code=partner_code,
                partner_name=partner_name,
                amount=amount,
                reference=reference,
                description=description,
            )
        )
        return
    if event_type == BusinessEventType.EXPENSE_BILL:
        services.purchases.create_expense_bill(
            ExpenseBillCommand(
                entry_date=entry_date,
                partner_code=partner_code,
                partner_name=partner_name,
                amount=amount,
                reference=reference,
                description=description,
            )
        )
        return
    if event_type == BusinessEventType.CASH_RECEIPT:
        services.cash.register_customer_receipt(
            CustomerReceiptCommand(
                entry_date=entry_date,
                partner_code=partner_code,
                partner_name=partner_name,
                amount=amount,
                reference=reference,
                description=description,
            )
        )
        return
    services.cash.register_vendor_payment(
        VendorPaymentCommand(
            entry_date=entry_date,
            partner_code=partner_code,
            partner_name=partner_name,
            amount=amount,
            reference=reference,
            description=description,
        )
    )


def _partner_options_for_event(services: AppServices, event_type: BusinessEventType) -> list[str]:
    expected_type = (
        PartnerType.CUSTOMER
        if event_type in {BusinessEventType.SALES_INVOICE, BusinessEventType.CASH_RECEIPT}
        else PartnerType.VENDOR
    )
    return [
        f"{partner.code} | {partner.name}"
        for partner in services.partners.list_partners()
        if partner.partner_type is expected_type
    ]


def _resolve_partner_input(
    *,
    services: AppServices,
    partner_selection: str,
    fallback_code: str,
    fallback_name: str,
) -> tuple[str, str]:
    if partner_selection == "manual":
        _validate_transaction_input(fallback_code, fallback_name)
        return fallback_code, fallback_name

    partner_code = partner_selection.split(" | ", maxsplit=1)[0]
    partner = next(
        (partner for partner in services.partners.list_partners() if partner.code == partner_code),
        None,
    )
    if partner is None:
        raise ValueError("selected partner not found")
    return partner.code, partner.name


def _validate_transaction_input(partner_code: str, partner_name: str) -> None:
    if not partner_code.strip():
        raise ValueError("partner code required")
    if not partner_name.strip():
        raise ValueError("partner name required")
