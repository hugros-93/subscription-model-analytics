from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

class DashboardColors:
    black = 'black'
    white = 'white'
    gray = 'gray'



def get_header_buttons():
    return dbc.Col(
            html.Div(
                [
                    dcc.Loading(
                        id="loading-state-load-data",
                        type="circle",
                        color=DashboardColors.white,
                        children=dbc.Button(
                            "Load data",
                            id="button-load-data",
                            color="primary",
                            className="me-1",
                            n_clicks=0,
                            disabled=False,
                        ),
                    )
                ],
                className="d-grid gap-2 d-md-flex justify-content-md-end",
            ),
            width=True,
        )

def get_navigation(pages):
    nav_pages = [
        dbc.NavLink(
            page, href=pages[page]["href"], style={"color": "white"}, active="exact"
        )
        for page in pages
    ]

    nav = dbc.Col(
            [dbc.Nav(nav_pages, vertical=False, pills=True)]
        )
    return nav

def create_conditional_style(df):
    PIXEL_FOR_CHAR = 10
    style = []
    for col in df.columns:
        name_length = len(col)
        pixel = 50 + round(name_length * PIXEL_FOR_CHAR)
        pixel = str(pixel) + "px"
        style.append({"if": {"column_id": col}, "minWidth": pixel})

    return style

def get_table(df, filter_action="native"):
    style_cell_conditional = create_conditional_style(df)

    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        editable=False,
        fixed_rows={"headers": True},
        page_size=50,
        filter_action=filter_action,
        sort_action="native",
        sort_mode="multi",
        style_table={"height": 400},
        style_cell_conditional=style_cell_conditional,
        style_header={
            "color": "white",
            "backgroundColor": DashboardColors.black,
            "fontWeight": "bold",
        },
        style_data={
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_cell={
            "textAlign": "center",
            "font_size": "12px",
            "whiteSpace": "normal",
            "height": "auto",
        },
    )

def get_please_load_data_message():
    return html.Div(
        [dcc.Markdown("Please click on the `Load data` button first.")],
        className="div-white-border-radius",
        style={"padding": "20px", "background": DashboardColors.white},
    )
