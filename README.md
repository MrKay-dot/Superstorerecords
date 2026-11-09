# Londoner Superstore

The Netlify site is a static sales dashboard in `public/`. It runs in the browser and does not require a Python server. `netlify.toml` sets the publish directory and supports direct navigation links.

The dashboard includes overview metrics, region/segment/category filters, product and team rankings, monthly and daily sales, a trend-and-seasonality forecast with an approximate residual interval, and the original project brief PDF. All calculations use the bundled workbook data; no external chart scripts or runtime API are required.

## Refresh workbook data

After replacing `SuperStoreData.xlsx`, install `openpyxl` in your Python environment and run:

```sh
python scripts/export_data.py
```

Commit the updated `public/sales.csv` together with the workbook. Only the columns used by the dashboard are exported. The published dashboard exposes these sales records to visitors, as required for client-side filtering.

## Original application

The original Streamlit sources remain available for local use:

```sh
python -m pip install -r requirements.txt
streamlit run super_storedata.py
```

Streamlit requires a persistent Python server and cannot run as a Netlify static site.
