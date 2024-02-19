from dash import dcc, html
import dash_bootstrap_components as dbc

from utils.dash import get_please_load_data_message, DashboardColors

def make_layout(charts_data):
    if not charts_data:
        return html.Div([html.H2("Growth"), get_please_load_data_message()])
    else:
        for i in [1, 2]:
            charts_data["retention"][i]['layout']['height'] = 800
            charts_data["retention"][i]['layout']['yaxis']['automargin'] = True

        return dcc.Loading(
            type="circle",
            color=DashboardColors.gray,
            children=html.Div(
            [
                html.H2("Retention"),
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
