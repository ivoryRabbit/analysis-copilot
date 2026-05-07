import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect

from models.source_config import SourceConfig

st.set_page_config(
    page_title="Mini-Data-Catalog",
    page_icon=":open_book:"
)

st.title("Data Catalog")

if "cursor_data_source" not in st.session_state:
    st.session_state["cursor_data_source"] = None

if st.session_state["cursor_data_source"] is None:
    st.stop()


def get_connection_url(source_config: SourceConfig) -> str:
    if source_config.source_type == "Postgres":
        connection_url = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            user=source_config.user,
            password=source_config.password,
            host=source_config.host,
            port=source_config.port,
            database=source_config.database,
        )
    else:
        connection_url = "mysql://{user}:{password}@{host}:{port}/{database}".format(
            user=source_config.user,
            password=source_config.password,
            host=source_config.host,
            port=source_config.port,
            database=source_config.database,
        )
    return connection_url


with st.sidebar:

    database_url = get_connection_url(st.session_state["cursor_data_source"])
    engine = create_engine(database_url)
    inspector = inspect(engine)

    schemas = inspector.get_schema_names()
    schema_name = st.selectbox("**스키마**를 선택해주세요.", options=schemas, index=None, placeholder="Choose a schema")


if schema_name is not None:
    tables = inspector.get_table_names(schema=schema_name)

    table_name = st.selectbox("**테이블**을 선택해주세요.", options=tables, index=None)

    if table_name is not None:
        st.subheader("Table", divider=True)

        st.text_area(label="Description")

        columns = inspector.get_columns(table_name=table_name, schema=schema_name)
        column_df = (
            pd.DataFrame(columns)
            .filter(items=["name", "type", "nullable", "comment"])
        )

        st.subheader("Columns", divider=True)
        st.data_editor(column_df, use_container_width=True)
