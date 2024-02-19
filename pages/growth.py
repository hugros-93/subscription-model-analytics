from dash import dcc, html
import dash_bootstrap_components as dbc

from utils.dash import get_please_load_data_message, DashboardColors

def make_layout(charts_data):
    if not charts_data:
        return html.Div([html.H2("Growth"), get_please_load_data_message()])
    else:
        return dcc.Loading(
            type="circle",
            color=DashboardColors.gray,
            children=html.Div(
            [
                html.H2("Growth"),
                dcc.Graph(
                    figure=charts_data["active_users"],
                    style={
                        "border-radius": "15px",
                        "background-color": "white",
                    },
                    config={"displayModeBar": False},
                ),
                html.Br(),
                dcc.Graph(
                    figure=charts_data["growth_accounting"],
                    style={
                        "border-radius": "15px",
                        "background-color": "white",
                    },
                    config={"displayModeBar": False},
                )
            ]
        ))
