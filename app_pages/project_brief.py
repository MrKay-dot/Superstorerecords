import streamlit as st

from store_data import PDF_FILE


st.title("Project brief", icon=":material/description:")
st.caption("Accessible, text-based summary of the original project PDF.")

st.header("Londoner Superstore")
st.markdown(
    "The project brief asks for an analysis of what works best for the store and which "
    "products, regions, categories, and customer segments it should target or avoid."
)

st.header("Questions to answer")
st.markdown(
    """
- How many records are in the dataset?
- What are the total sales, total profit, and profit margin?
- Which customer segments perform best by quantity, sales, and profit?
- Which product categories perform best by quantity, sales, and profit?
- Which ten sub-categories generate the most profit?
- Which ten products are most purchased, and which products lead in sales and profit?
- How do regions perform by sales and profit?
- Which five states lead and lag in sales and profit?
- How are sales representatives and managers performing?
- How do sales vary month to month and day to day?
"""
)

st.header("Presentation and recommendations")
st.markdown(
    "The project asks for a dashboard with the most important visuals and a presentation "
    "of findings and recommendations. Use the navigation bar to explore the dashboard "
    "pages; compare performance before making decisions about investment or products to avoid."
)

if not PDF_FILE.is_file():
    st.error(f"The original PDF, {PDF_FILE.name}, is not available beside the app.")
else:
    st.download_button(
        "Download the original project PDF",
        data=PDF_FILE.read_bytes(),
        file_name=PDF_FILE.name,
        mime="application/pdf",
        icon=":material/download:",
    )
