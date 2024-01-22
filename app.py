from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import plotly.io as pio
import plotly.graph_objects as go

import json
import pandas as pd

from pages import readme, data, analytics
from utils.dash import get_header_buttons, get_navigation, get_filters, DashboardColors
from utils.model import DataModel

# Plotly template
with open("assets/template.json", "r") as f:
    plotly_template = json.load(f)
pio.templates["plotly_template"] = go.layout.Template(plotly_template)
pio.templates.default = "plotly_template"

# Dash params
DASHBOARD_NAME = "Subscription model analytics"

# Dash app
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

# Custom dash app tab and logo
app.title = DASHBOARD_NAME
app._favicon = "logo.png"

# Server
server = app.server

# Navigation
pages = {
    "Readme": {"href": "/", "content": readme},
    "Data": {"href": "/data", "content": data},
    "Analytics": {"href": "/analytics", "content": analytics},
}

# Header
title = html.H1(f"📈 {DASHBOARD_NAME}", style={"color": DashboardColors.white})

header = html.Div(
    [
        dbc.Stack(
            [dbc.Stack([title, get_navigation(pages)]), get_header_buttons()],
            direction="horizontal",
        )
    ],
    style={
        "padding": "1rem",
        "background-color": DashboardColors.black,
        "width": "100%",
    },
    id="header",
)

# Content
CONTENT_STYLE = {"margin-left": "1rem", "margin-right": "1rem", "padding": "1rem"}
content = dcc.Loading(
    id="loading",
    type="circle",
    color=DashboardColors.gray,
    children=[
        html.Div(
            id="page-content",
            style=CONTENT_STYLE,
        )
    ],
)

# Filter
dict_filter_choices = {
        "date": {
            "display_name": "Date range",
            "data": ["day", "week", "month"],
        }
    }

filters = html.Div(
    [
        dbc.Row(
            get_filters(dict_filter_choices),
            # align="Center",
        )
    ],
    style={"padding": "20px", "margin-right": "30px", "margin-left": "30px"},
    id="div-white-border-radius",
)

# Storage
storage = html.Div(
    [dcc.Store(id="store-input-data"), dcc.Store(id="store-model-charts")]
)

# Layout
app.layout = html.Div(
    [dcc.Location(id="url"), header, filters, content, storage]
)


# Callback page navigation
@app.callback(
    Output("page-content", "children"),
    [
        Input("url", "pathname"),
        Input("store-input-data", "data"),
        Input("store-model-charts", "data"),
        Input("dropdown-filter-date", "value")
    ],
)
def render_page_content(pathname, input_data, charts_data, date_range):
    if pathname == "/":
        return pages["Readme"]["content"].make_layout()
    elif pathname == "/data":
        return pages["Data"]["content"].make_layout(input_data)
    elif pathname == "/analytics":
        if date_range:
            chart_data_date_range = charts_data[date_range]
        else:
            chart_data_date_range = None
        return pages["Analytics"]["content"].make_layout(chart_data_date_range)
    else:
        return None

# Callback load data
@app.callback(
    [
        Output("store-input-data", "data"),
        Output("store-model-charts", "data"),
        Output("button-load-data", "value"),
        Output("output-load-data", "children"),
    ],
    Input("button-load-data", "n_clicks"),
)
def load_data(n_clicks):
    if n_clicks:
        # Load data
        filename = "dataset.csv"
        dataset = pd.read_csv(filename)
        dataset["start_date"] = pd.to_datetime(dataset["start_date"])
        dataset["end_date"] = pd.to_datetime(dataset["end_date"])

        # Create data model
        model = DataModel(dataset)
        model.fit()

        # Get data
        fig_dict = {}
        for date_range in model.date_range_dict.keys():
            fig_dict[date_range] = model.get_charts(date_range)

        return [
            dataset.to_json(date_format="iso", orient="split"),
            fig_dict,
            "Load data",
            True,
        ]
    else:
        return [None, None, "Load data", False]


# Callback load data modal
@app.callback(
    Output("modal-load-data", "is_open"),
    inputs=[
        Input("output-load-data", "children"),
        Input("button-modal-load-data", "n_clicks"),
    ],
    state=[State("modal-load-data", "is_open")],
)
def toggle_modal(output_load_data, close_click, is_open):
    if close_click or output_load_data:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True)
