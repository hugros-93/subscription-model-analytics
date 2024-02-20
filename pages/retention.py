from dash import dcc, html
import dash_bootstrap_components as dbc

from utils.dash import get_please_load_data_message, DashboardColors

title = "Retention"


def make_layout(charts_data):
    if not charts_data:
        return html.Div([html.H2(title), get_please_load_data_message()])
    else:
        for date_range in ["month", "week"]:
            charts_data[date_range]["retention"][0]["layout"]["height"] = 400
            for i in [1, 2]:
                if date_range == "month":
                    charts_data[date_range]["retention"][i]["layout"]["height"] = 600
                else:
                    charts_data[date_range]["retention"][i]["layout"]["height"] = 1200
                charts_data[date_range]["retention"][i]["layout"]["yaxis"][
                    "automargin"
                ] = True

        return html.Div(
            [
                html.H2(title),
                dbc.CardHeader(
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
                                                    "retention"
                                                ][0],
                                                style={
                                                    "border-radius": "15px",
                                                    "background-color": DashboardColors.white,
                                                },
                                                config={"displayModeBar": False},
                                            ),
                                            html.Br(),
                                            dcc.Graph(
                                                figure=charts_data[date_range][
                                                    "retention"
                                                ][1],
                                                style={
                                                    "border-radius": "15px",
                                                    "background-color": DashboardColors.white,
                                                },
                                                config={"displayModeBar": False},
                                            ),
                                            html.Br(),
                                            dcc.Graph(
                                                figure=charts_data[date_range][
                                                    "retention"
                                                ][2],
                                                style={
                                                    "border-radius": "15px",
                                                    "background-color": DashboardColors.white,
                                                },
                                                config={"displayModeBar": False},
                                            ),
                                        ]
                                    ),
                                ),
                                label=date_range.capitalize(),
                                tab_id=date_range,
                            )
                            for date_range in ["month", "week"]
                        ],
                        active_tab="month",
                    )
                ),
            ]
        )
