from dash import dcc, html
import dash_bootstrap_components as dbc

from utils.dash import get_please_load_data_message, DashboardColors

title = "Growth"


def make_layout(charts_data):
    if not charts_data:
        return html.Div([html.H2(title), get_please_load_data_message()])
    else:
        for date_range in ["month", "week", "day"]:
            charts_data[date_range]["active_users"]["layout"]["height"] = 400
            charts_data[date_range]["growth_accounting"]["layout"]["height"] = 400
        return html.Div(
            [
                html.H2(title),
                dbc.Tabs(
                    [
                        dbc.Tab(
                            dcc.Loading(
                                type="circle",
                                color=DashboardColors.gray,
                                children=html.Div(
                                    [
                                        html.Br(),
                                        dcc.Graph(
                                            figure=charts_data[date_range][
                                                "active_users"
                                            ],
                                            style={
                                                "border-radius": "15px",
                                                "background-color": "white",
                                            },
                                            config={"displayModeBar": False},
                                        ),
                                        html.Br(),
                                        dcc.Graph(
                                            figure=charts_data[date_range][
                                                "growth_accounting"
                                            ],
                                            style={
                                                "border-radius": "15px",
                                                "background-color": "white",
                                            },
                                            config={"displayModeBar": False},
                                        ),
                                    ]
                                ),
                            ),
                            label=date_range.capitalize(),
                            tab_id=date_range,
                        )
                        for date_range in ["month", "week", "day"]
                    ],
                    active_tab="month",
                ),
            ]
        )
