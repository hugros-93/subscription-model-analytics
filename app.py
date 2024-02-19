from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import plotly.io as pio
import plotly.graph_objects as go

import json
import pandas as pd

from pages import readme, data, growth, retention
from utils.dash import get_header_buttons, get_navigation, DashboardColors
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
    "Growth": {"href": "/growth", "content": growth},
    "Retention": {"href": "/retention", "content": retention},
    "Data": {"href": "/data", "content": data},
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

# Storage
storage = html.Div(
    [dcc.Store(id="store-input-data"), dcc.Store(id="store-model-charts")]
)

# Layout
app.layout = html.Div([dcc.Location(id="url"), header, content, storage])


# Callback page navigation
@app.callback(
    Output("page-content", "children"),
    [
        Input("url", "pathname"),
        Input("store-input-data", "data"),
        Input("store-model-charts", "data"),
    ],
)
def render_page_content(pathname, input_data, charts_data):
    date_range = 'month'
    if pathname == "/":
        return pages["Readme"]["content"].make_layout()
    elif pathname == "/data":
        return pages["Data"]["content"].make_layout(input_data)
    elif pathname == "/growth":
        if charts_data and date_range:
            chart_data_date_range = charts_data[date_range]
        else:
            chart_data_date_range = None
        return pages["Growth"]["content"].make_layout(chart_data_date_range)
    elif pathname == "/retention":
        if charts_data and date_range:
            chart_data_date_range = charts_data[date_range]
        else:
            chart_data_date_range = None
        return pages["Retention"]["content"].make_layout(chart_data_date_range)
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
        print(f"> Loading data")
        filename = "data/dataset.csv"
        dataset = pd.read_csv(filename)
        dataset["start_date"] = pd.to_datetime(dataset["start_date"])
        dataset["end_date"] = pd.to_datetime(dataset["end_date"])

        # Load or create charts
        print(f"> Loading charts")
        try:
            # Load existing data
            with open("figures/fig_dict.json", "r") as f:
                fig_dict = json.load(f)
            for date_range in fig_dict:
                for fig in fig_dict[date_range]:
                    if type(fig_dict[date_range][fig]) == list:
                        fig_dict[date_range][fig] = [
                            go.Figure(json.loads(x)) for x in fig_dict[date_range][fig]
                        ]
                    else:
                        fig_dict[date_range][fig] = go.Figure(
                            json.loads(fig_dict[date_range][fig])
                        )
            print(f"> Existing charts loaded!")
        except Exception as e:
            print(f"> Not loading existing charts: {e}")
            # Create data model
            print(f"> Fitting model")
            model = DataModel(dataset)
            model.fit()

            # Get charts
            print(f"> Creating charts")
            fig_dict = {}
            for date_range in model.date_range_dict.keys():
                fig_dict[date_range] = model.get_charts(date_range)

            # Export data
            print(f"> Exporting charts")
            fig_dict_json = {}
            for date_range in fig_dict:
                fig_dict_json[date_range] = {}
                for fig in fig_dict[date_range]:
                    if type(fig_dict[date_range][fig]) == list:
                        fig_dict_json[date_range][fig] = [
                            x.to_json() for x in fig_dict[date_range][fig]
                        ]
                        for i, x in enumerate(fig_dict[date_range][fig]):
                            x.write_html(f"figures/{fig}_{date_range}_{i}.html")
                    else:
                        fig_dict_json[date_range][fig] = fig_dict[date_range][
                            fig
                        ].to_json()
                        fig_dict[date_range][fig].write_html(
                            f"figures/{fig}_{date_range}.html"
                        )
            with open("figures/fig_dict.json", "w") as f:
                json.dump(fig_dict_json, f)

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
