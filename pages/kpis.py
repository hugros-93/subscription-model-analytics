from dash import dcc, html
import dash_bootstrap_components as dbc

from utils.dash import get_please_load_data_message, DashboardColors

title = "KPIs"


def make_layout(kpis_data):
    if not kpis_data:
        return html.Div([html.H2(title), get_please_load_data_message()])
    else:
        for kpi in kpis_data:
            kpis_data[kpi]["layout"]["height"] = 150
            kpis_data[kpi]["layout"]["margin"] = {"l": 30, "r": 30, "b": 30, "t": 50}
        return dcc.Loading(
            type="circle",
            color=DashboardColors.gray,
            children=html.Div(
                [
                    html.H2(title),
                    html.H4("Active users"),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Graph(
                                    figure=kpis_data["active_users_now"],
                                    style={
                                        "border-radius": "15px",
                                        "background-color": "white",
                                    },
                                    config={"displayModeBar": False},
                                ),
                                width=6,
                                align="center",
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    figure=kpis_data["active_users_end_last_week"],
                                    style={
                                        "border-radius": "15px",
                                        "background-color": "white",
                                    },
                                    config={"displayModeBar": False},
                                )
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    figure=kpis_data["active_users_end_last_month"],
                                    style={
                                        "border-radius": "15px",
                                        "background-color": "white",
                                    },
                                    config={"displayModeBar": False},
                                )
                            ),
                        ],
                        align="center",
                    ),
                    html.Br(),
                    html.H4("New users"),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Graph(
                                    figure=kpis_data["new_users_this_week"],
                                    style={
                                        "border-radius": "15px",
                                        "background-color": "white",
                                    },
                                    config={"displayModeBar": False},
                                )
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    figure=kpis_data["new_users_last_week"],
                                    style={
                                        "border-radius": "15px",
                                        "background-color": "white",
                                    },
                                    config={"displayModeBar": False},
                                )
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    figure=kpis_data["new_users_this_month"],
                                    style={
                                        "border-radius": "15px",
                                        "background-color": "white",
                                    },
                                    config={"displayModeBar": False},
                                )
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    figure=kpis_data["new_users_last_month"],
                                    style={
                                        "border-radius": "15px",
                                        "background-color": "white",
                                    },
                                    config={"displayModeBar": False},
                                )
                            ),
                        ]
                    ),
                    html.Br(),
                    html.H4("Churn"),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Graph(
                                    figure=kpis_data["churn_this_week"],
                                    style={
                                        "border-radius": "15px",
                                        "background-color": "white",
                                    },
                                    config={"displayModeBar": False},
                                )
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    figure=kpis_data["churn_last_week"],
                                    style={
                                        "border-radius": "15px",
                                        "background-color": "white",
                                    },
                                    config={"displayModeBar": False},
                                )
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    figure=kpis_data["churn_this_month"],
                                    style={
                                        "border-radius": "15px",
                                        "background-color": "white",
                                    },
                                    config={"displayModeBar": False},
                                )
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    figure=kpis_data["churn_last_month"],
                                    style={
                                        "border-radius": "15px",
                                        "background-color": "white",
                                    },
                                    config={"displayModeBar": False},
                                )
                            ),
                        ]
                    ),
                    html.Br(),
                ],
                style={"height": 300},
            ),
        )
