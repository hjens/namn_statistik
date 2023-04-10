# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from typing import Any, Callable, Sequence
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd


def get_names(filename: str) -> pd.DataFrame:
    def num_to_int(num):
        if num == "..":
            return 0
        return int(num)

    df = pd.read_csv(filename)
    df = df.melt(id_vars=["name"], var_name="year", value_name="num")
    df.num = df.num.apply(num_to_int)
    df.year = df.year.apply(num_to_int)
    return df


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df_boys = get_names("data/BE0001AM_20210507-184020.csv")
df_girls = get_names("data/BE0001AM_20210507-183718.csv")
df_all = pd.concat([df_boys, df_girls])
all_names = df_all.name.sort_values().unique()

df_spans = pd.read_csv("data/names_with_year_spans.csv")


@app.callback(Output("name-graph", "figure"), Input("name-dropdown", "value"))
def name_plot(names: Sequence[str]):
    df_names = df_all.query("name in @names") if names else df_all
    return px.line(
        df_names,
        x="year",
        y="num",
        color="name",
        labels={"year": "År", "num": "Antal födda med namnet", "name": "Namn"},
        template="simple_white",
    )


def top_list(
    df: pd.DataFrame, column_name: str, format_func: Callable[[Any], str], title: str
) -> html.Div:
    def item_text(item):
        return item["name"] + ": " + format_func(item[column_name])

    return html.Div(
        children=[
            html.H3(title),
            html.Ol(children=[html.Li(item_text(item)) for _, item in df.iterrows()]),
        ],
        style={"float": "left", "margin": "20px"},
    )


most_popular_names = top_list(
    df_all.groupby("name")["num"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
    .head(5),
    column_name="num",
    format_func=lambda num: "{0:,}".format(num).replace(",", " "),
    title="Flest bärare",
)

oldest_names = top_list(
    df_spans.sort_values(by="top_year").head(5),
    column_name="top_year",
    format_func=lambda y: str(2023 - y) + " år",
    title="Äldst medianbärare",
)

youngest_names = top_list(
    df_spans.sort_values(by="top_year", ascending=False).head(5),
    column_name="top_year",
    format_func=lambda y: str(2023 - y) + " år",
    title="Yngst medianbärare",
)


app.layout = html.Div(
    children=[
        html.H2(children="Antal födda per år"),
        dcc.Dropdown(all_names, multi=True, value=[all_names[0]], id="name-dropdown"),
        dcc.Graph(id="name-graph"),
        html.Div(
            children=[
                html.H2("Topplistor"),
                most_popular_names,
                oldest_names,
                youngest_names,
            ],
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8051)
