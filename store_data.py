from __future__ import annotations

from pathlib import Path
import math as m

try:
    import pandas as pd
except (ImportError, ModuleNotFoundError) as exc:
    pd = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None

try:
    import streamlit as st
except (ImportError, ModuleNotFoundError) as exc:
    st = None
    if IMPORT_ERROR is None:
        IMPORT_ERROR = exc


def _cache_data(*args, **kwargs):
    if st is None:
        if args and callable(args[0]) and len(args) == 1 and not kwargs:
            return args[0]

        def decorator(func):
            return func

        return decorator
    return st.cache_data(*args, **kwargs)


DATA_FILE = Path(__file__).with_name("SuperStoreData.xlsx")
PDF_FILE = Path(__file__).with_name("Superstore Project - Jan Cohort.pdf")
REQUIRED_COLUMNS = {
    "Order Date",
    "Order ID",
    "Sales",
    "Profit",
    "Region",
    "Segment",
    "Category",
    "Sub-Category",
    "Product Name",
    "Quantity",
    "State",
    "Sales Rep",
    "Sales Team Manager",
}


@_cache_data(show_spinner="Loading store data...")
def load_data(file_path: str = str(DATA_FILE)) -> pd.DataFrame:
    data = pd.read_excel(file_path)
    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        raise ValueError(f"Workbook is missing required columns: {', '.join(sorted(missing_columns))}")

    data["Order Date"] = pd.to_datetime(data["Order Date"], errors="coerce")
    for column in ("Sales", "Profit", "Quantity"):
        data[column] = pd.to_numeric(data[column], errors="coerce")
    return data.dropna(subset=["Order Date", "Sales", "Profit", "Quantity"])


def load_or_stop() -> pd.DataFrame:
    if pd is None:
        message = (
            "Required data dependencies are unavailable. Install pandas and numpy "
            f"to load the sales workbook. Details: {IMPORT_ERROR}"
        )
        if st is None:
            raise RuntimeError(message) from IMPORT_ERROR
        st.error(message, icon=":material/error:")
        st.stop()
    if not DATA_FILE.is_file():
        st.error(
            f"Could not find {DATA_FILE.name}. Place the workbook beside "
            f"{Path(__file__).name} and reload the app.",
            icon=":material/error:",
        )
        st.stop()
    try:
        return load_data()
    except (OSError, ValueError, ImportError) as error:
        st.error(f"Could not load the sales workbook: {error}", icon=":material/error:")
        st.stop()


def render_filters(data: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.markdown("## :material/storefront: Londoner Superstore")
        st.caption("Sales intelligence")
        st.divider()
        st.markdown("### Filters")
        selected_region = st.selectbox(
            "Region",
            ["All regions", *sorted(data["Region"].dropna().unique())],
            key="filter_region",
        )
        selected_segment = st.selectbox(
            "Customer segment",
            ["All segments", *sorted(data["Segment"].dropna().unique())],
            key="filter_segment",
        )
        selected_category = st.selectbox(
            "Product category",
            ["All categories", *sorted(data["Category"].dropna().unique())],
            key="filter_category",
        )

    filtered_data = data
    if selected_region != "All regions":
        filtered_data = filtered_data[filtered_data["Region"] == selected_region]
    if selected_segment != "All segments":
        filtered_data = filtered_data[filtered_data["Segment"] == selected_segment]
    if selected_category != "All categories":
        filtered_data = filtered_data[filtered_data["Category"] == selected_category]
    return filtered_data


def stop_if_empty(data: pd.DataFrame) -> None:
    if data.empty:
        st.warning("No sales records match these filters. Choose a different filter combination.")
        st.stop()


def build_forecast(data: pd.DataFrame, years: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    monthly_sales = data.set_index("Order Date")["Sales"].resample("MS").sum().asfreq("MS", fill_value=0)
    if len(monthly_sales) < 2:
        history = monthly_sales.rename("Sales").rename_axis("Month").reset_index()
        return history, pd.DataFrame()

    time_index = list(range(len(monthly_sales)))
    sales_values = monthly_sales.tolist()
    mean_time = sum(time_index) / len(time_index)
    mean_sales = sum(sales_values) / len(sales_values)
    slope = sum(
        (time - mean_time) * (sales - mean_sales)
        for time, sales in zip(time_index, sales_values)
    ) / sum((time - mean_time) ** 2 for time in time_index)
    intercept = mean_sales - slope * mean_time
    trend = [intercept + slope * time for time in time_index]
    residuals = [sales - fitted for sales, fitted in zip(sales_values, trend)]
    seasonal_effect = (
        pd.Series(residuals, index=monthly_sales.index.month)
        .groupby(level=0)
        .mean()
        .reindex(range(1, 13), fill_value=0)
    )
    seasonal_effect -= seasonal_effect.mean()

    future_months = pd.date_range(
        monthly_sales.index[-1] + pd.offsets.MonthBegin(1),
        periods=years * 12,
        freq="MS",
    )
    future_index = list(range(len(monthly_sales), len(monthly_sales) + len(future_months)))
    future_trend = [intercept + slope * time for time in future_index]
    seasonal = [seasonal_effect.loc[month] for month in future_months.month]
    predicted_sales = [
        max(trend_value + seasonal_value, 0)
        for trend_value, seasonal_value in zip(future_trend, seasonal)
    ]
    residual_mean = sum(residuals) / len(residuals)
    residual_std = m.sqrt(
        sum((residual - residual_mean) ** 2 for residual in residuals)
        / (len(residuals) - 1)
    )
    interval = [
        1.96 * residual_std * m.sqrt(1 + index / len(monthly_sales))
        for index in future_index
    ]

    history = monthly_sales.rename("Sales").rename_axis("Month").reset_index()
    forecast = pd.DataFrame(
        {
            "Month": future_months,
            "Sales": predicted_sales,
            "Lower": [max(sales - margin, 0) for sales, margin in zip(predicted_sales, interval)],
            "Upper": [sales + margin for sales, margin in zip(predicted_sales, interval)],
        }
    )
    return history, forecast
