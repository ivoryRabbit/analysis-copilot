from collections import deque

import streamlit as st

from models.source_config import SourceConfig
from utils.image import get_image_path

st.set_page_config(
    page_title="Mini-Data-Catalog",
    page_icon=":open_book:"
)

st.markdown("""
<style>
.streamlit-expanderContent div {
    display: flex;
    justify-content: center;
    font-size: 20px;
}
[data-testid="stExpanderToggleIcon"] {
    visibility: hidden;
}
[data-testid="stElementToolbar"] {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

st.title("Data Source")

data_source_types = [
    "Postgres",
    "Athena",
    "Cassandra",
    "ClickHouse",
    "MongoDB",
    "MySQL",
    "Presto",
    "Redshift",
    "ScyllaDB",
    "Trino",
]


initial_data_sources = [
    SourceConfig(source_type="Postgres", name="Movie", host="localhost", port=5432, user="postgres", password="postgres", database="dev"),
    SourceConfig(source_type="Athena", name="Sample"),
    SourceConfig(source_type="Cassandra", name="Sample"),
    SourceConfig(source_type="ClickHouse", name="Sample"),
    SourceConfig(source_type="MongoDB", name="Sample"),
    SourceConfig(source_type="MySQL", name="Sample"),
    SourceConfig(source_type="Presto", name="Sample"),
    SourceConfig(source_type="Redshift", name="Sample"),
    SourceConfig(source_type="ScyllaDB", name="Sample"),
    SourceConfig(source_type="Trino", name="Sample"),
]

if "registered_data_source" not in st.session_state:
    st.session_state["registered_data_source"] = deque()
    st.session_state["registered_data_source"].extend(initial_data_sources)

if "cursor_data_source" not in st.session_state:
    st.session_state["cursor_data_source"] = None


with st.container(border=True):
    source_type = st.selectbox(
        "**데이터 소스**를 추가해주세요",
        options=data_source_types,
        index=None,
        placeholder="Select a data source",
    )


if source_type is not None:
    with st.form("config"):
        name = st.text_input("Name")

        col1, col2 = st.columns(2)
        with col1:
            host = st.text_input("Host")
        with col2:
            port = st.text_input("Port")
        user = st.text_input("User")
        password = st.text_input("Password", type="password")
        database = st.text_input("Database")

        submit = st.form_submit_button(label="추가", use_container_width=True)

        if submit is True:
            if name is None:
                st.error("'Name'을 입력해주세요.")
            else:
                st.session_state["registered_data_source"].appendleft(
                    SourceConfig(
                        source_type=source_type,
                        name=name,
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database,
                    )
                )


MAX_COL_LEN = 4
cols = st.columns(MAX_COL_LEN)

for n, data_source in enumerate(st.session_state["registered_data_source"]):
    source_type = data_source.source_type
    source_name = data_source.name
    with cols[n % MAX_COL_LEN]:
        image_path = get_image_path(source_type)
        with st.expander(label=source_type, expanded=True):
            st.image(image_path)
            is_click = st.button(label=source_name, key=f"{source_type}-{source_name}", use_container_width=True)

            if is_click is True:
                st.session_state["cursor_data_source"] = data_source
                st.switch_page("pages/data_catalog.py")


# TODO: convert the widget for data source registration to modal
# if "select_data_source" not in st.session_state:
#     st.session_state["select_data_source"] = None
#
# @st.dialog("데이터 소스를 추가해주세요")
# def register_data_source(source_type: str):
#     with st.form("config"):
#         name = st.text_input("Name")
#
#         col1, col2 = st.columns(2)
#         with col1:
#             host = st.text_input("Host")
#         with col2:
#             port = st.text_input("Port")
#         user = st.text_input("User")
#         password = st.text_input("Password", type="password")
#         database = st.text_input("Database")
#
#         submit = st.form_submit_button(label="추가", use_container_width=True)
#
#         if submit is True:
#             if name is None:
#                 st.error("'Name'을 입력해주세요.")
#             else:
#                 st.session_state["registered_data_source"].appendleft(
#                     SourceConfig(
#                         source_type=source_type,
#                         name=name,
#                         host=host,
#                         port=port,
#                         user=user,
#                         password=password,
#                         database=database,
#                     )
#                 )
#             st.session_state["select_data_source"] = source_type
#             st.rerun()
#
#
# if st.session_state["select_data_source"] is None:
#     with st.container(border=True):
#         source_type = st.selectbox(
#             "**데이터 소스**를 추가해주세요",
#             options=data_source_types,
#             index=None,
#         )
#
#         if source_type is not None:
#             register_data_source(source_type)
# else:
#     st.session_state["select_data_source"] = None