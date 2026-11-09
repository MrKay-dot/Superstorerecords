from datetime import date

import streamlit as st


st.set_page_config(
    page_title="Londoner Superstore | Sales intelligence",
    page_icon=":material/storefront:",
    layout="wide",
)

st.html(
    """
    <style>
    .stApp {
        background-color: #0B1220;
        background-image:
            linear-gradient(rgba(11, 18, 32, 0.86), rgba(11, 18, 32, 0.82)),
            url("/app/static/superstore-background.jpg");
        background-position: center;
        background-size: cover;
        background-attachment: fixed;
    }
    </style>
    """
)

page = st.navigation(
    [
        st.Page(
            "app_pages/overview.py",
            title="Overview",
            icon=":material/dashboard:",
            help="Start here for store-wide sales, profit, and the most important performance indicators.",
        ),
        st.Page(
            "app_pages/products_segments.py",
            title="Products & segments",
            icon=":material/inventory_2:",
            help="Compare customer segments and product categories, and explore the best-performing products.",
        ),
        st.Page(
            "app_pages/regions_teams.py",
            title="Regions & teams",
            icon=":material/groups:",
            help="Compare regional and state results, then review sales representative and manager performance.",
        ),
        st.Page(
            "app_pages/time_forecast.py",
            title="Time & forecast",
            icon=":material/calendar_month:",
            help="Explore monthly and daily sales history and review a directional multi-year forecast.",
        ),
        st.Page(
            "app_pages/project_brief.py",
            title="Project brief",
            icon=":material/description:",
            help="Read the project brief in accessible text or download the original PDF.",
        ),
    ],
    position="top",
)
page.run()

st.divider()
st.caption(f"Copyright {date.today().year} Londoner Superstore. All rights reserved.")
