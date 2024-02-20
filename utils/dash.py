from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc


class DashboardColors:
    black = "black"
    white = "white"

    gray = "gray"
    background_gray = "#e4e6e6"

    green = "#00b050"
    light_green = "#90e990"
    yellow = "#ffc82f"
    orange = "#f37021"
    red = "#ff0000"

    palette_category = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]

    palette_green = [
        "#efffad",
        "#cbf266",
        "#99e866",
        "#66cc66",
        "#00b050",
        "#009933",
        "#00792b",
        "#004700",
    ]

    palette_blue = [
        "#e2f2ff",
        "#99ccff",
        "#6699ff",
        "#3366cc",
        "#253fc8",
        "#140a9a",
        "#0c065c",
        "#1b232a",
    ]


def get_header_buttons():
    return dbc.Col(
        html.Div(
            [
                dcc.Loading(
                    id="loading-state-load-data",
                    type="circle",
                    color=DashboardColors.white,
                    children=dcc.Upload(
                        dbc.Button(
                            "Load data",
                            id="button-load-data",
                            color="primary",
                            className="me-1",
                            n_clicks=0,
                            disabled=False,
                        ),
                        id="upload-file",
                    ),
                ),
                html.P(id="output-load-data"),
                dbc.Modal(
                    [
                        dbc.ModalBody("Data successfully loaded!"),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Close",
                                id="button-modal-load-data",
                                className="ms-auto",
                                n_clicks=0,
                            )
                        ),
                    ],
                    id="modal-load-data",
                    is_open=False,
                ),
            ],
            className="d-grid gap-2 d-md-flex justify-content-md-end",
        ),
        width=True,
    )


def get_navigation(pages):
    nav_pages = [
        dbc.NavLink(
            page, href=pages[page]["href"], style={"color": DashboardColors.white}, active="exact"
        )
        for page in pages
    ]

    nav = dbc.Col([dbc.Nav(nav_pages, vertical=False, pills=True)])
    return nav


def get_filters(dict_filter_choices):
    return [
        dbc.Col(
            [
                html.H6(dict_filter_choices[x]["display_name"]),
                dcc.Dropdown(
                    dict_filter_choices[x]["data"],
                    value=dict_filter_choices[x]["data"][2],
                    id=f"dropdown-filter-{x}",
                    style={"line-height": "30px"},
                ),
            ]
        )
        for x in dict_filter_choices
    ]


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
            "color": DashboardColors.white,
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
        [dcc.Markdown("Please load data by clicking on the `Load data` button.")],
        className="div-white-border-radius",
        style={"padding": "20px", "background": DashboardColors.white},
    )
