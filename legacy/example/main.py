import streamlit as st


pages = {
    "Data Source": [
        st.Page("pages/data_source.py", title="Data Source"),
    ],
    "Data Catalog": [
        st.Page("pages/data_catalog.py", title="Data Catalog"),
    ],
    "Temp": [
        st.Page("pages/recap.py", title="2024 Recap"),
    ],
}

pg = st.navigation(pages)
pg.run()
