"""Spending Analysis page - Deep dive into spending patterns."""

import streamlit as st
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from src.utils.formatters import milliunits_to_dollars

st.title("\U0001F4B8 Spending Analysis")

# Get resources from session state
db = st.session_state.get('db')
budget_id = st.session_state.get('budget_id')

if not db or not budget_id:
    st.warning("Please select a budget from the sidebar")
    st.stop()


def format_month_label(month_str: str) -> str:
    """Convert YYYY-MM to 'January 2025' format."""
    try:
        dt = datetime.strptime(month_str, "%Y-%m")
        return dt.strftime("%B %Y")
    except ValueError:
        return month_str


# Get available months
available_months = db.get_available_months(budget_id)

if not available_months:
    st.warning("No transaction data available. Please sync your data.")
    st.stop()

# Filters
st.sidebar.subheader("Filters")

# Month selector
month_labels = {m: format_month_label(m) for m in available_months}
selected_month = st.sidebar.selectbox(
    "Month",
    options=available_months,
    format_func=lambda x: month_labels.get(x, x),
    index=0  # Default to most recent month
)

# Category filter
categories = db.get_categories(budget_id, include_hidden=False)
category_names = ["All Categories"] + sorted(set(cat['name'] for cat in categories))
selected_category = st.sidebar.selectbox("Category", options=category_names)

# Get spending data for selected month
spending_by_cat = db.get_spending_by_category_for_month(budget_id, selected_month)
transactions = db.get_transactions_for_month(budget_id, selected_month)

# Filter by category if selected
if selected_category != "All Categories":
    spending_by_cat = [s for s in spending_by_cat if s['category_name'] == selected_category]
    transactions = [t for t in transactions if t['category_name'] == selected_category]

# Summary metrics
st.subheader(f"Summary - {month_labels[selected_month]}")

col1, col2, col3 = st.columns(3)

total_spent = sum(row['total_amount'] for row in spending_by_cat)
total_transactions = sum(row['transaction_count'] for row in spending_by_cat)
avg_transaction = total_spent / total_transactions if total_transactions > 0 else 0

with col1:
    st.metric("Total Spent", f"${milliunits_to_dollars(total_spent):,.2f}")

with col2:
    st.metric("Transactions", f"{total_transactions:,}")

with col3:
    st.metric("Avg Transaction", f"${milliunits_to_dollars(int(avg_transaction)):,.2f}")

st.divider()

# Spending breakdown
st.subheader("Spending Breakdown")

if spending_by_cat:
    # Create dataframe
    df = pl.DataFrame([
        {
            'Category': row['category_name'] or 'Uncategorized',
            'Amount': float(milliunits_to_dollars(row['total_amount'])),
            'Count': row['transaction_count'],
            'Avg': float(milliunits_to_dollars(row['total_amount'] // row['transaction_count'])) if row['transaction_count'] > 0 else 0.0
        }
        for row in spending_by_cat
    ])

    # Horizontal bar chart
    fig = px.bar(
        df.head(15),
        x='Amount',
        y='Category',
        orientation='h',
        color='Amount',
        color_continuous_scale='Greens'
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Data table
    with st.expander("View Detailed Data"):
        st.dataframe(
            df.to_pandas().style.format({
                'Amount': '${:,.2f}',
                'Count': '{:,}',
                'Avg': '${:,.2f}'
            }),
            use_container_width=True
        )
else:
    st.info("No spending data available for the selected month.")

st.divider()

# Monthly trend analysis (show last 12 months for context)
st.subheader("Monthly Spending Trend")

monthly_trend = db.get_monthly_spending_trend(budget_id, months=12)

if monthly_trend:
    df_trend = pl.DataFrame([
        {
            'Month': row['month'],
            'Amount': float(milliunits_to_dollars(row['total_amount']))
        }
        for row in monthly_trend
    ])

    # Calculate average for reference line
    avg_monthly = df_trend['Amount'].mean()

    # Highlight selected month
    colors = ['#4CAF50' if m == selected_month else '#2E7D32' for m in df_trend['Month'].to_list()]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_trend['Month'].to_list(),
        y=df_trend['Amount'].to_list(),
        name='Monthly Spending',
        marker_color=colors
    ))

    # Average line
    fig.add_hline(
        y=avg_monthly,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Avg: ${avg_monthly:,.0f}",
        annotation_position="top right"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Spending ($)",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Compare to previous month
    current_idx = df_trend['Month'].to_list().index(selected_month) if selected_month in df_trend['Month'].to_list() else -1
    if current_idx > 0:
        current = df_trend['Amount'][current_idx]
        previous = df_trend['Amount'][current_idx - 1]
        change = ((current - previous) / previous * 100) if previous > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Selected Month", f"${current:,.2f}")
        with col2:
            st.metric("Previous Month", f"${previous:,.2f}")
        with col3:
            st.metric("Change", f"{change:+.1f}%", delta=f"${current - previous:,.0f}")

else:
    st.info("No trend data available.")

st.divider()

# Top payees for selected month
st.subheader("Top Payees")

if transactions:
    payee_totals = {}
    for txn in transactions:
        if txn['amount'] < 0:  # Only outflows
            payee = txn['payee_name'] or 'Unknown'
            if payee not in payee_totals:
                payee_totals[payee] = {'amount': 0, 'count': 0}
            payee_totals[payee]['amount'] += abs(txn['amount'])
            payee_totals[payee]['count'] += 1

    if payee_totals:
        # Sort and display top 10
        sorted_payees = sorted(payee_totals.items(), key=lambda x: x[1]['amount'], reverse=True)[:10]

        df_payees = pl.DataFrame([
            {
                'Payee': payee,
                'Total': float(milliunits_to_dollars(data['amount'])),
                'Transactions': data['count'],
                'Avg': float(milliunits_to_dollars(data['amount'] // data['count'])) if data['count'] > 0 else 0.0
            }
            for payee, data in sorted_payees
        ])

        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                df_payees,
                values='Total',
                names='Payee',
                hole=0.4
            )
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.dataframe(
                df_payees.to_pandas().style.format({
                    'Total': '${:,.2f}',
                    'Transactions': '{:,}',
                    'Avg': '${:,.2f}'
                }),
                use_container_width=True
            )
    else:
        st.info("No outflow transactions for the selected month.")
else:
    st.info("No transaction data available for the selected month.")

st.divider()

# Transaction list
st.subheader("Transactions")

outflow_txns = [t for t in transactions if t['amount'] < 0]
if outflow_txns:
    with st.expander(f"View All Transactions ({len(outflow_txns)})"):
        txn_data = pl.DataFrame([
            {
                'Date': t['date'],
                'Payee': t['payee_name'] or 'Unknown',
                'Category': t['category_name'] or 'Uncategorized',
                'Amount': float(milliunits_to_dollars(abs(t['amount']))),
                'Memo': t['memo'] or ''
            }
            for t in outflow_txns
        ])
        st.dataframe(
            txn_data.to_pandas().style.format({'Amount': '${:,.2f}'}),
            use_container_width=True
        )
else:
    st.info("No transactions for the selected filters.")
