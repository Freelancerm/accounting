"""Streamlit UI shell for minimal accounting app."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import streamlit as st

from src.core.settings import get_settings
from src.domain.events import BusinessEventType, Partner, PartnerType
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
    col1.metric("Revenue", _format_currency(report.revenue))
    col2.metric("Expense", _format_currency(report.expense))
    col3.metric("Net Result", _format_currency(report.net_result))


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
        filtered_partners = _list_partners(
            services,
            None if filter_value == "all" else PartnerType(filter_value),
        )
        partner_rows = [
            {
                "code": partner.code,
                "name": partner.name,
                "partner_type": partner.partner_type.value,
            }
            for partner in filtered_partners
        ]
        render_table(
            partner_rows,
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
        metric_col1.metric("Revenue", _format_currency(pnl_report.revenue))
        metric_col2.metric("Expense", _format_currency(pnl_report.expense))
        metric_col3.metric("Net Result", _format_currency(pnl_report.net_result))
        render_table(
            [
                {"line_item": line.line_item, "amount": _format_currency(line.amount)}
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
    event_type = st.selectbox(
        "Business Event",
        options=[event.value for event in BusinessEventType],
        format_func=lambda value: value.replace("_", " ").title(),
        key="transaction_event_type",
    )
    selected_event_type = BusinessEventType(event_type)
    partner_name = st.text_input("Partner Name", placeholder="Acme Client", key="transaction_partner_name")
    partner_type = _partner_type_for_event(selected_event_type)
    suggested_partners = services.accounting.suggest_partners(partner_name, partner_type)
    suggestion_options = ["new_partner", *[f"{partner.code} | {partner.name}" for partner in suggested_partners]]
    partner_selection = st.selectbox(
        "Suggested Partner",
        options=suggestion_options,
        format_func=lambda value: _format_partner_option(value),
        key="transaction_partner_suggestion",
    )
    resolved_partner = _resolve_partner_selection(suggested_partners, partner_selection)
    preview_partner_name = resolved_partner.name if resolved_partner is not None else partner_name
    generated_partner_code = (
        resolved_partner.code
        if resolved_partner is not None
        else services.accounting.preview_partner_code(preview_partner_name, partner_type)
    )
    generated_reference = services.accounting.preview_reference(selected_event_type)

    with st.form("transaction_form"):
        entry_date = st.date_input("Date", value=date.today())
        st.text_input("Partner Code", value=generated_partner_code, disabled=True)
        st.text_input("Reference", value=generated_reference, disabled=True)
        amount = st.number_input("Amount", min_value=0.0, value=0.0, step=100.0, format="%.2f")
        description = st.text_input("Description", placeholder="Optional note")
        submitted = st.form_submit_button("Post Transaction")

        if submitted:
            try:
                resolved_partner_name = _resolve_partner_name(partner_name, resolved_partner)
                _submit_transaction(
                    services=services,
                    event_type=selected_event_type,
                    entry_date=entry_date,
                    partner_code=resolved_partner.code if resolved_partner is not None else "",
                    partner_name=resolved_partner_name,
                    amount=Decimal(f"{amount:.2f}"),
                    reference="",
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
def _resolve_partner_selection(partners: list[Partner], partner_selection: str) -> Partner | None:
    if partner_selection == "new_partner":
        return None

    partner_code = partner_selection.split(" | ", maxsplit=1)[0]
    return next((partner for partner in partners if partner.code == partner_code), None)


def _resolve_partner_name(partner_name: str, selected_partner: Partner | None) -> str:
    if selected_partner is not None:
        return selected_partner.name
    if not partner_name.strip():
        raise ValueError("partner name required")
    return partner_name.strip()


def _partner_type_for_event(event_type: BusinessEventType) -> PartnerType:
    if event_type in {BusinessEventType.SALES_INVOICE, BusinessEventType.CASH_RECEIPT}:
        return PartnerType.CUSTOMER
    return PartnerType.VENDOR


def _list_partners(services: AppServices, partner_type: PartnerType | None = None) -> list[Partner]:
    partners = services.partners.list_partners()
    if partner_type is None:
        return partners
    return [partner for partner in partners if partner.partner_type is partner_type]


def _format_currency(amount: Decimal) -> str:
    return f"${float(amount):,.2f}"


def _format_partner_option(option: str) -> str:
    if option == "new_partner":
        return "Create new partner from typed name"
    return option
