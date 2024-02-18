from dash import dcc, html
import dash_bootstrap_components as dbc

from utils.dash import get_please_load_data_message, DashboardColors

def make_layout(charts_data):
    if not charts_data:
        return html.Div([html.H2("Analytics"), get_please_load_data_message()])
    else:
        charts_data["retention"][1]['layout']['height'] = 800
        charts_data["retention"][2]['layout']['height'] = 800

        charts_data["retention"][1]['layout']['yaxis']['automargin'] = True
        charts_data["retention"][2]['layout']['yaxis']['automargin'] = True

        return dcc.Loading(
            type="circle",
            color=DashboardColors.gray,
            children=html.Div(
            [
                html.H2("Analytics"),
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
                ),
                html.Br(),
                dcc.Graph(
                    figure=charts_data["retention"][0],
                    style={
                        "border-radius": "15px",
                        "background-color": "white",
                    },
                    config={"displayModeBar": False},
                ),
                html.Br(),
                dcc.Graph(
                    figure=charts_data["retention"][1],
                    style={
                        "border-radius": "15px",
                        "background-color": "white",
                    },
                    config={"displayModeBar": False},
                ),
                html.Br(),
                dcc.Graph(
                    figure=charts_data["retention"][2],
                    style={
                        "border-radius": "15px",
                        "background-color": "white",
                    },
                    config={"displayModeBar": False},
                ),
            ]
        ))
