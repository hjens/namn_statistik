# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from typing import Sequence
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd


def get_names(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename)
    return df.melt(id_vars=["name"], var_name="year", value_name="num")


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df_boys = get_names("data/BE0001AM_20210507-184020.csv")
df_girls = get_names("data/BE0001AM_20210507-183718.csv")
df_all = pd.concat([df_boys, df_girls])
all_names = df_all.name.sort_values().unique()

df_spans = pd.read_csv("data/names_with_year_spans.csv")


@app.callback(Output("name-graph", "figure"), Input("name-dropdown", "value"))
def name_plot(names: Sequence[str]):
    if names:
        df_names = df_all.query("name in @names")
    else:
        df_names = df_all
    return px.line(
        df_names,
        x="year",
        y="num",
        color="name",
        labels={"year": "År", "num": "Antal födda med namnet", "name": "Namn"},
    )


@app.callback(Output("span-graph", "figure"), Input("span-slider", "value"))
def span_plot(slider):
    min_year = slider[0]
    max_year = slider[1]
    df_names = df_spans.query("top_year >= @min_year and top_year <= @max_year").copy()
    df_names["err_x"] = df_names.max_year - df_names.top_year
    df_names["err_x_minus"] = df_names.top_year - df_names.min_year
    df_names["text"] = df_names.apply(
        lambda x: f"{x['name']} ({x.min_year} - {x.max_year})", axis=1
    )

    fig_height = max(len(df_names) * 25, 200)
    fig = px.scatter(
        df_names.sort_values(by="top_year"),
        x="top_year",
        y="name",
        text="text",
        error_x_minus="err_x_minus",
        error_x="err_x",
        labels={"name": "", "top_year": ""},
        template="simple_white",
        height=fig_height,
    )
    fig.update_traces(hovertemplate="<b>%{y}</b>\n%{x}")
    fig.update_traces(textposition="top center")
    fig.update_yaxes(visible=False)
    fig.update_layout(
        margin=dict(l=20, r=20, t=0, b=0),
    )
    return fig


app.layout = html.Div(
    children=[
        html.H2(children="Antal födda per år"),
        dcc.Dropdown(all_names, multi=True, value=[all_names[0]], id="name-dropdown"),
        dcc.Graph(id="name-graph"),
        html.H2(children="Årsintervall som innehåller en tredjedel av alla med namnet"),
        dcc.RangeSlider(
            id="span-slider",
            min=1930,
            max=2020,
            step=1,
            value=(1990, 2020),
            marks={y: f"{y}" for y in range(1930, 2020, 5)},
        ),
        dcc.Graph(id="span-graph"),
    ]
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8051)
