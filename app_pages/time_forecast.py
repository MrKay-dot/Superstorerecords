import altair as alt
import pandas as pd
import streamlit as st

from store_data import build_forecast, load_or_stop, render_filters, stop_if_empty


data = load_or_stop()
filtered_data = render_filters(data)
stop_if_empty(filtered_data)

st.title("Time & forecast", icon=":material/calendar_month:")
st.caption("Review the sales timeline and explore a directional forecast based on historical patterns.")

monthly = (
    filtered_data.set_index("Order Date")["Sales"]
    .resample("MS")
    .sum()
    .rename("Sales")
    .rename_axis("Month")
    .reset_index()
)
daily = (
    filtered_data.set_index("Order Date")["Sales"]
    .resample("D")
    .sum()
    .rename("Sales")
    .rename_axis("Date")
    .reset_index()
)

monthly_view, daily_view = st.tabs(["Monthly sales", "Daily sales"])
with monthly_view:
    st.subheader("Monthly sales")
    st.line_chart(
        monthly,
        x="Month",
        y="Sales",
        x_label="Month",
        y_label="Sales ($)",
        alt="Monthly sales history",
    )
with daily_view:
    st.subheader("Daily sales")
    st.line_chart(
        daily,
        x="Date",
        y="Sales",
        x_label="Date",
        y_label="Sales ($)",
        alt="Daily sales history",
    )

st.header("Forward outlook")
forecast_years = st.segmented_control(
    "Forecast horizon",
    options=[1, 2, 3, 5],
    default=3,
    format_func=lambda value: f"{value} year" if value == 1 else f"{value} years",
    key="forecast_years",
)
history, forecast = build_forecast(filtered_data, int(forecast_years or 3))
if forecast.empty:
    st.warning("At least two months of sales history are needed to create a forecast.")
else:
    st.caption(
        "This is a directional estimate using a linear trend and average monthly seasonality. "
        "The shaded range is an approximate 95% residual interval, not a guarantee."
    )
    history_line = (
        alt.Chart(history)
        .mark_line(color="#22D3EE", strokeWidth=2.5)
        .encode(
            x=alt.X("Month:T", title="Month", axis=alt.Axis(format="%b %Y", labelAngle=-35)),
            y=alt.Y("Sales:Q", title="Sales ($)", axis=alt.Axis(format="$~s")),
            tooltip=[
                alt.Tooltip("Month:T", title="Month", format="%b %Y"),
                alt.Tooltip("Sales:Q", title="Actual sales", format="$,.0f"),
            ],
        )
    )
    forecast_band = (
        alt.Chart(forecast)
        .mark_area(color="#A78BFA", opacity=0.16)
        .encode(
            x=alt.X("Month:T", title="Month"),
            y=alt.Y("Lower:Q", title="Sales ($)", axis=alt.Axis(format="$~s")),
            y2=alt.Y2("Upper:Q"),
            tooltip=[
                alt.Tooltip("Month:T", title="Month", format="%b %Y"),
                alt.Tooltip("Lower:Q", title="Low estimate", format="$,.0f"),
                alt.Tooltip("Upper:Q", title="High estimate", format="$,.0f"),
            ],
        )
    )
    forecast_line = (
        alt.Chart(forecast)
        .mark_line(color="#A78BFA", strokeWidth=2.5, strokeDash=[7, 4], point=True)
        .encode(
            x=alt.X("Month:T"),
            y=alt.Y("Sales:Q"),
            tooltip=[
                alt.Tooltip("Month:T", title="Month", format="%b %Y"),
                alt.Tooltip("Sales:Q", title="Projected sales", format="$,.0f"),
            ],
        )
    )
    start_rule = (
        alt.Chart(pd.DataFrame({"Month": [forecast["Month"].min()]}))
        .mark_rule(color="#64748B", strokeDash=[3, 4])
        .encode(x="Month:T")
    )
    st.altair_chart(
        alt.layer(forecast_band, history_line, forecast_line, start_rule)
        .properties(height=340)
        .interactive(),
        width="stretch",
        alt="Monthly sales history with a multi-year forecast and approximate uncertainty range",
    )
    latest_sales = float(history["Sales"].tail(12).sum())
    projected_sales = float(forecast["Sales"].head(12).sum())
    delta = (
        f"{(projected_sales / latest_sales - 1) * 100:+.1f}% vs. latest 12 months"
        if latest_sales
        else None
    )
    st.metric("Projected sales (next 12 months)", f"${projected_sales:,.0f}", delta, border=True)
