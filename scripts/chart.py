#!/usr/bin/env python3
"""
쿼리 결과(JSON)를 받아 Plotly 차트 HTML을 생성하고 브라우저에서 엽니다.

사용법:
  python scripts/chart.py '<json>' [bar|line|pie|scatter] [x_col] [y_col] [title]

예시:
  python scripts/chart.py '[{"genre":"Action","avg_rating":4.1}]' bar genre avg_rating "장르별 평균 평점"
"""
import json
import os
import subprocess
import sys
import tempfile

import pandas as pd
import plotly.express as px


CHART_FUNCS = {
    "bar": px.bar,
    "line": px.line,
    "pie": px.pie,
    "scatter": px.scatter,
}


def build_chart(records: list[dict], chart_type: str, x: str, y: str, title: str):
    df = pd.DataFrame(records)
    cols = list(df.columns)

    x = x or cols[0]
    y = y or (cols[1] if len(cols) > 1 else cols[0])

    func = CHART_FUNCS.get(chart_type, px.bar)

    if chart_type == "pie":
        fig = func(df, names=x, values=y, title=title)
    else:
        fig = func(df, x=x, y=y, title=title)

    fig.update_layout(
        font_family="sans-serif",
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


def open_chart(fig):
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, prefix="chart_")
    fig.write_html(tmp.name)
    tmp.close()
    print(f"차트 저장: {tmp.name}")
    subprocess.run(["open", tmp.name], check=False)
    return tmp.name


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python scripts/chart.py '<json>' [bar|line|pie|scatter] [x] [y] [title]")
        sys.exit(1)

    raw = sys.argv[1]
    chart_type = sys.argv[2] if len(sys.argv) > 2 else "bar"
    x_col = sys.argv[3] if len(sys.argv) > 3 else ""
    y_col = sys.argv[4] if len(sys.argv) > 4 else ""
    title = sys.argv[5] if len(sys.argv) > 5 else ""

    records = json.loads(raw)
    fig = build_chart(records, chart_type, x_col, y_col, title)
    open_chart(fig)
