# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from typing import Sequence
import dash
import dash_core_components as dcc
from dash import html
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
all_names = df_all.name.unique()


@app.callback(Output("name-graph", "figure"), Input("name-dropdown", "value"))
def name_plot(names: Sequence[str]):
    return px.line(
        df_all.query("name in @names"),
        x="year",
        y="num",
        color="name",
        labels={"year": "År", "num": "Antal", "name": "Namn"},
    )


app.layout = html.Div(
    children=[
        html.H1(children="Antal födda per år"),
        dcc.Dropdown(all_names, multi=True, value=all_names[0], id="name-dropdown"),
        dcc.Graph(id="name-graph"),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
