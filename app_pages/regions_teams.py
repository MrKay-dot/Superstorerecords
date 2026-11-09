import altair as alt
import pandas as pd
import streamlit as st

from store_data import load_or_stop, render_filters, stop_if_empty


data = load_or_stop()
filtered_data = render_filters(data)
stop_if_empty(filtered_data)

st.title("Regions & teams", icon=":material/groups:")
st.caption("Compare geography and sales leadership to identify strong markets and opportunities.")

region_summary = (
    filtered_data.groupby("Region", as_index=False)[["Sales", "Profit"]]
    .sum()
    .sort_values("Sales", ascending=False)
)
region_summary["Profit margin"] = (
    region_summary["Profit"].div(region_summary["Sales"].replace(0, float("nan"))).mul(100)
)
st.header("Regional performance")
st.dataframe(
    region_summary,
    hide_index=True,
    column_config={
        "Sales": st.column_config.NumberColumn(format="$%.2f"),
        "Profit": st.column_config.NumberColumn(format="$%.2f"),
        "Profit margin": st.column_config.NumberColumn(format="%.1f%%"),
    },
    alt="Regional sales, profit, and profit margin",
)

state_sales = (
    filtered_data.groupby("State", as_index=False)[["Sales", "Profit"]]
    .sum()
)
state_tabs = st.tabs(["Sales leaders & opportunities", "Profit leaders & opportunities"])
for tab, metric in zip(state_tabs, ["Sales", "Profit"]):
    with tab:
        top_states = state_sales.nlargest(5, metric).assign(Ranking=f"Top 5 by {metric.lower()}")
        bottom_states = state_sales.nsmallest(5, metric).assign(Ranking=f"Bottom 5 by {metric.lower()}")
        state_rankings = (
            pd.concat([top_states, bottom_states])
            .drop_duplicates(subset=["State", "Ranking"])
            .rename(columns={"State": "State"})
            [["Ranking", "State", "Sales", "Profit"]]
        )
        st.dataframe(
            state_rankings,
            hide_index=True,
            column_config={
                "Sales": st.column_config.NumberColumn(format="$%.2f"),
                "Profit": st.column_config.NumberColumn(format="$%.2f"),
            },
            alt=f"Top and bottom five states ranked by {metric.lower()}",
        )

st.header("Sales leadership")
representatives, managers = st.columns(2)
for column, field, title in [
    (representatives, "Sales Rep", "Sales by representative"),
    (managers, "Sales Team Manager", "Sales by manager"),
]:
    with column:
        with st.container(border=True):
            st.subheader(title)
            performance = (
                filtered_data.groupby(field, as_index=False)["Sales"]
                .sum()
                .nlargest(10, "Sales")
                .sort_values("Sales")
            )
            chart = (
                alt.Chart(performance)
                .mark_bar(color="#22D3EE", cornerRadiusEnd=4)
                .encode(
                    x=alt.X("Sales:Q", title="Sales ($)", axis=alt.Axis(format="$~s")),
                    y=alt.Y(f"{field}:N", title=None, sort="-x"),
                    tooltip=[
                        alt.Tooltip(f"{field}:N", title="Name"),
                        alt.Tooltip("Sales:Q", title="Sales", format="$,.0f"),
                    ],
                )
                .properties(height=300)
            )
            st.altair_chart(chart, width="stretch", alt=f"Top 10 {field.lower()} by sales")
