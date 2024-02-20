from dash import dcc, html
import dash_bootstrap_components as dbc

from utils.dash import DashboardColors


def make_layout():
    return html.Div(
        [
            html.H2("Readme"),
            html.Div(
                [dcc.Markdown("Readme text here.")],
                className="div-white-border-radius",
                style={"padding": "20px", "background": DashboardColors.white},
            ),
        ]
    )
