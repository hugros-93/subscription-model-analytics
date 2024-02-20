from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd

from utils.dash import get_please_load_data_message, get_table


def make_layout(input_data):
    if not input_data:
        return html.Div([html.H2("Data"), get_please_load_data_message()])
    else:

        input_data = pd.read_json(input_data, orient="split")

        input_data["start_date"] = input_data["start_date"].apply(
            lambda x: pd.to_datetime(x).strftime("%Y-%m-%d %H:%M:%S")
        )
        input_data["end_date"] = input_data["end_date"].apply(
            lambda x: (
                pd.to_datetime(x).strftime("%Y-%m-%d %H:%M:%S") if x != None else None
            )
        )

        input_data.columns = [
            c.replace("_", " ").capitalize() for c in input_data.columns
        ]

        return html.Div(
            [
                html.H2("Data"),
                html.Div(
                    [
                        html.H4("Input data"),
                        get_table(input_data, filter_action="none"),
                    ],
                    className="div-white-border-radius",
                    style={"padding": "20px"},
                ),
            ]
        )
