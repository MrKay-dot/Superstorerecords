import altair as alt
import pandas as pd
import streamlit as st

from store_data import load_or_stop, render_filters, stop_if_empty


data = load_or_stop()
filtered_data = render_filters(data)
stop_if_empty(filtered_data)

st.title("Products & segments", icon=":material/inventory_2:")
st.caption("Compare sales, profit, and units to see which customers and products drive results.")

segment_results = (
    filtered_data.groupby("Segment", as_index=False)[["Quantity", "Sales", "Profit"]]
    .sum()
    .sort_values("Sales", ascending=False)
)
category_results = (
    filtered_data.groupby("Category", as_index=False)[["Quantity", "Sales", "Profit"]]
    .sum()
    .sort_values("Sales", ascending=False)
)

segment_chart, category_chart = st.columns(2)
with segment_chart:
    with st.container(border=True):
        st.subheader("Segment results")
        chart = (
            alt.Chart(segment_results)
            .mark_bar(color="#22D3EE", cornerRadiusEnd=4)
            .encode(
                x=alt.X("Sales:Q", title="Sales ($)", axis=alt.Axis(format="$~s")),
                y=alt.Y("Segment:N", title=None, sort="-x"),
                tooltip=[
                    alt.Tooltip("Segment:N", title="Segment"),
                    alt.Tooltip("Quantity:Q", title="Units", format=","),
                    alt.Tooltip("Sales:Q", title="Sales", format="$,.0f"),
                    alt.Tooltip("Profit:Q", title="Profit", format="$,.0f"),
                ],
            )
            .properties(height=180)
        )
        st.altair_chart(chart, width="stretch", alt="Sales by customer segment with quantity and profit details")
        st.dataframe(
            segment_results,
            hide_index=True,
            column_config={
                "Quantity": st.column_config.NumberColumn("Units", format="%d"),
                "Sales": st.column_config.NumberColumn(format="$%.2f"),
                "Profit": st.column_config.NumberColumn(format="$%.2f"),
            },
            alt="Quantity, sales, and profit totals by customer segment",
        )

with category_chart:
    with st.container(border=True):
        st.subheader("Category results")
        chart = (
            alt.Chart(category_results)
            .mark_bar(color="#A78BFA", cornerRadiusEnd=4)
            .encode(
                x=alt.X("Profit:Q", title="Profit ($)", axis=alt.Axis(format="$~s")),
                y=alt.Y("Category:N", title=None, sort="-x"),
                tooltip=[
                    alt.Tooltip("Category:N", title="Category"),
                    alt.Tooltip("Quantity:Q", title="Units", format=","),
                    alt.Tooltip("Sales:Q", title="Sales", format="$,.0f"),
                    alt.Tooltip("Profit:Q", title="Profit", format="$,.0f"),
                ],
            )
            .properties(height=180)
        )
        st.altair_chart(chart, width="stretch", alt="Profit by product category with quantity and sales details")
        st.dataframe(
            category_results,
            hide_index=True,
            column_config={
                "Quantity": st.column_config.NumberColumn("Units", format="%d"),
                "Sales": st.column_config.NumberColumn(format="$%.2f"),
                "Profit": st.column_config.NumberColumn(format="$%.2f"),
            },
            alt="Quantity, sales, and profit totals by product category",
        )

st.header("Top-performing products")
subcat, quantity, top_value = st.tabs(
    ["Sub-category profit", "Most purchased", "Top sales & profit"]
)
with subcat:
    top_subcategories = (
        filtered_data.groupby("Sub-Category", as_index=False)[["Sales", "Profit"]]
        .sum()
        .nlargest(10, "Profit")
        .rename(columns={"Sub-Category": "Sub-category"})
    )
    st.dataframe(
        top_subcategories,
        hide_index=True,
        column_config={
            "Sales": st.column_config.NumberColumn(format="$%.2f"),
            "Profit": st.column_config.NumberColumn(format="$%.2f"),
        },
        alt="Top 10 sub-categories ranked by total profit",
    )
with quantity:
    most_purchased = (
        filtered_data.groupby("Product Name", as_index=False)["Quantity"]
        .sum()
        .nlargest(10, "Quantity")
        .rename(columns={"Product Name": "Product"})
    )
    st.dataframe(
        most_purchased,
        hide_index=True,
        column_config={"Quantity": st.column_config.NumberColumn("Units purchased", format="%d")},
        alt="Top 10 products by total quantity purchased",
    )
with top_value:
    product_totals = filtered_data.groupby("Product Name", as_index=False)[["Sales", "Profit"]].sum()
    best_sales = product_totals.nlargest(10, "Sales").assign(Ranking="Top sales")
    best_profit = product_totals.nlargest(10, "Profit").assign(Ranking="Top profit")
    top_products = (
        pd.concat([best_sales, best_profit])
        .drop_duplicates(subset=["Product Name", "Ranking"])
        .rename(columns={"Product Name": "Product"})
        [["Ranking", "Product", "Sales", "Profit"]]
    )
    st.dataframe(
        top_products,
        hide_index=True,
        column_config={
            "Sales": st.column_config.NumberColumn(format="$%.2f"),
            "Profit": st.column_config.NumberColumn(format="$%.2f"),
        },
        alt="Top 10 products by sales and top 10 by profit",
    )
