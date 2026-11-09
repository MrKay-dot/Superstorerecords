import altair as alt
import pandas as pd
import streamlit as st

from store_data import load_or_stop, render_filters, stop_if_empty


data = load_or_stop()
filtered_data = render_filters(data)
stop_if_empty(filtered_data)

st.title("Store overview", icon=":material/dashboard:")
st.caption("A quick view of store performance. Use the navigation bar to explore products, teams, and sales trends.")

total_sales = float(filtered_data["Sales"].sum())
total_profit = float(filtered_data["Profit"].sum())
profit_margin = total_profit / total_sales * 100 if total_sales else 0

metrics = st.columns(4)
metrics[0].metric("Records", f"{len(filtered_data):,}", border=True)
metrics[1].metric("Total sales", f"${total_sales:,.0f}", border=True)
metrics[2].metric("Total profit", f"${total_profit:,.0f}", border=True)
metrics[3].metric("Profit margin", f"{profit_margin:.1f}%", border=True)

st.header("Performance at a glance")
left, right = st.columns(2)
with left:
    with st.container(border=True):
        st.subheader("Sales by category")
        category_sales = (
            filtered_data.groupby("Category", as_index=False)[["Sales", "Profit"]]
            .sum()
            .sort_values("Sales", ascending=False)
        )
        chart = (
            alt.Chart(category_sales)
            .transform_fold(["Sales", "Profit"], as_=["Measure", "Amount"])
            .mark_bar()
            .encode(
                x=alt.X("Amount:Q", title="Amount ($)", axis=alt.Axis(format="$~s")),
                y=alt.Y("Category:N", title=None, sort="-x"),
                color=alt.Color("Measure:N", title="Measure"),
                tooltip=[
                    alt.Tooltip("Category:N", title="Category"),
                    alt.Tooltip("Measure:N", title="Measure"),
                    alt.Tooltip("Amount:Q", title="Amount", format="$,.0f"),
                ],
            )
            .properties(height=220)
        )
        st.altair_chart(chart, width="stretch", alt="Sales and profit by product category")

with right:
    with st.container(border=True):
        st.subheader("Regional performance")
        region_sales = (
            filtered_data.groupby("Region", as_index=False)[["Sales", "Profit"]]
            .sum()
            .sort_values("Sales", ascending=False)
        )
        chart = (
            alt.Chart(region_sales)
            .mark_bar(color="#22D3EE", cornerRadiusEnd=4)
            .encode(
                x=alt.X("Sales:Q", title="Sales ($)", axis=alt.Axis(format="$~s")),
                y=alt.Y("Region:N", title=None, sort="-x"),
                tooltip=[
                    alt.Tooltip("Region:N", title="Region"),
                    alt.Tooltip("Sales:Q", title="Sales", format="$,.0f"),
                    alt.Tooltip("Profit:Q", title="Profit", format="$,.0f"),
                ],
            )
            .properties(height=220)
        )
        st.altair_chart(chart, width="stretch", alt="Sales by region; hover for profit details")

st.header("What to explore next")
st.markdown(
    "- **Products & segments:** compare quantity, sales, and profit across customer and product groups.\n"
    "- **Regions & teams:** find leading and underperforming states, regions, sales reps, and managers.\n"
    "- **Time & forecast:** review monthly and daily sales, plus a directional outlook."
)

segment_profit = filtered_data.groupby("Segment")["Profit"].sum()
category_profit = filtered_data.groupby("Category")["Profit"].sum()
region_profit = filtered_data.groupby("Region")["Profit"].sum()
state_profit = filtered_data.groupby("State")["Profit"].sum()
top_segment = segment_profit.idxmax()
top_category = category_profit.idxmax()
top_region = region_profit.idxmax()
lowest_profit_state = state_profit.idxmin()

with st.container(border=True):
    st.header("Findings & recommendations")
    st.markdown(
        f"- **Invest around proven performance:** {top_segment} is the highest-profit "
        f"customer segment, and {top_category} is the highest-profit category in the current selection.\n"
        f"- **Use a regional benchmark:** {top_region} leads regions by total profit; compare "
        "its product mix and customer segments with other regions before expanding.\n"
        f"- **Review improvement opportunities:** {lowest_profit_state} has the lowest total "
        "state profit in this selection. Investigate pricing, product mix, and discounting "
        "before deciding whether to reduce or increase investment."
    )
