from collections import deque

import streamlit as st
from pydantic import BaseModel

st.set_page_config(
    page_title="2024 Recap",
    page_icon=":open_book:"
)

st.html(
    """
    <style>
    [data-testid="stExpanderToggleIcon"] {
        visibility: hidden;
    }
    [data-testid="stElementToolbar"] {
        visibility: hidden;
    }
    [data-testid="stBaseButton-secondary"] {
        background-color: #4682B4;
        color: white; # Expander content color
    }
    </style>
    """
)

st.title("2024 Recap")


class RecapItem(BaseModel):
    name: str
    value: str


MAX_COL_LEN = 4

with st.container():
    st.subheader("업무", divider=True)

    recap_items = [
        RecapItem(name="커리어", value="3.8년"),
        RecapItem(name="요금 절감", value="65,700$"),
        RecapItem(name="영어 발표", value="2번"),
    ]

    cols = st.columns(MAX_COL_LEN)

    for n, recap_item in enumerate(recap_items):
        item_name = recap_item.name
        item_value = recap_item.value
        with cols[n % MAX_COL_LEN]:
            with st.expander(label=item_name, expanded=True):
                is_click = st.button(label=item_value, key=item_name, use_container_width=True)


with st.container():
    st.subheader("일상", divider=True)

    recap_items = [
        RecapItem(name="드럼", value="11곡"),
        RecapItem(name="헬스", value="55회"),
        RecapItem(name="런닝", value="0회"),
        RecapItem(name="여행", value="4번"),
    ]

    cols = st.columns(MAX_COL_LEN)

    for n, recap_item in enumerate(recap_items):
        item_name = recap_item.name
        item_value = recap_item.value
        with cols[n % MAX_COL_LEN]:
            with st.expander(label=item_name, expanded=True):
                is_click = st.button(label=item_value, key=item_name, use_container_width=True)

with st.container():
    st.subheader("활동", divider=True)

    recap_items = [
        RecapItem(name="글쓰기", value="16편"),
        RecapItem(name="스터디", value="0회"),
    ]

    cols = st.columns(MAX_COL_LEN)

    for n, recap_item in enumerate(recap_items):
        item_name = recap_item.name
        item_value = recap_item.value
        with cols[n % MAX_COL_LEN]:
            with st.expander(label=item_name, expanded=True):
                is_click = st.button(label=item_value, key=item_name, use_container_width=True)
