import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

from utils.dash import DashboardColors


class DataModel:
    def __init__(self, dataset):
        # Dataset
        self.dataset = dataset

        # List IDs and unique count
        self.list_users = pd.unique(dataset["user_id"])
        self.list_subscriptions = pd.unique(dataset.index)
        self.nb_users = len(self.list_users)
        self.nb_subscriptions = len(self.list_subscriptions)

        # Start and end dates
        self.min_start_date = dataset["start_date"].min() - timedelta(days=1)
        self.max_end_date = datetime.today() + relativedelta(days=1)

        # Date range - days
        self.list_date_range_day = [
            self.min_start_date + timedelta(days=i)
            for i in range(0, (self.max_end_date - self.min_start_date).days)
        ]

        # Date range - weeks
        self.min_start_date_week = self.min_start_date - timedelta(
            days=(self.min_start_date.weekday()) % 7
        )
        self.max_end_date_week = (
            self.max_end_date
            - timedelta(days=(self.max_end_date.weekday()) % 7)
            + timedelta(days=7)
        )
        self.list_date_range_week = [
            self.min_start_date_week + timedelta(days=7 * i)
            for i in range(
                0, int((self.max_end_date_week - self.min_start_date_week).days / 7)
            )
        ]

        # Date range - months
        self.min_start_date_month = self.min_start_date.replace(day=1)
        self.max_end_date_month = self.max_end_date.replace(day=1) + relativedelta(
            months=1
        )
        self.list_date_range_month = [
            self.min_start_date_month + relativedelta(months=i)
            for i in range(
                0,
                relativedelta(self.max_end_date_month, self.min_start_date_month).months
                + 12
                * relativedelta(
                    self.max_end_date_month, self.min_start_date_month
                ).years,
            )
        ]

        # Date range dict
        self.date_range_dict = {
            "day": self.list_date_range_day,
            "week": self.list_date_range_week,
            "month": self.list_date_range_month,
        }

    def fit(self):
        active_user_data = self.dataset.copy()
        active_user_data["end_date"] = active_user_data["end_date"].fillna(
            self.max_end_date
        )

        self.active_user_data_dict = {}
        self.active_user_data_aggregated_dict = {}

        self.retention_data_dict = {}
        self.retention_data_aggregated_dict = {}

        for date_range in self.date_range_dict:
            # Cross join date range and subscriptions
            data_date_range = pd.DataFrame(
                self.date_range_dict[date_range], columns=[date_range]
            )
            active_user_data_date_range = pd.merge(
                data_date_range, active_user_data, how="cross"
            )
            active_user_data_date_range = active_user_data_date_range.sort_values(
                ["user_id", date_range]
            )

            # Active subscription in each date range
            active_user_data_date_range["is_active"] = (
                active_user_data_date_range.apply(
                    lambda x: (
                        1 if x["start_date"] <= x[date_range] < x["end_date"] else 0
                    ),
                    axis=1,
                )
            )
            active_user_data_date_range = (
                active_user_data_date_range.groupby([date_range, "user_id"])[
                    "is_active"
                ]
                .max()
                .reset_index()
            )

            # Status over time ()
            active_user_data_date_range["is_active_previous"] = (
                active_user_data_date_range.groupby("user_id")["is_active"].shift(
                    1, fill_value=0
                )
            )
            active_user_data_date_range["was_active"] = (
                active_user_data_date_range.groupby("user_id")["is_active"].cumsum()
            )
            active_user_data_date_range["was_active"] = active_user_data_date_range[
                "was_active"
            ].apply(lambda x: 1 if x > 1 else 0)
            active_user_data_date_range["status"] = active_user_data_date_range.apply(
                lambda x: (
                    "new_active"
                    if x["is_active"] == 1
                    and x["is_active_previous"] == 0
                    and x["was_active"] == 0
                    else (
                        "resurrected"
                        if x["is_active"] == 1
                        and x["is_active_previous"] == 0
                        and x["was_active"] == 1
                        else (
                            "churn"
                            if x["is_active"] == 0 and x["is_active_previous"] == 1
                            else None
                        )
                    )
                ),
                axis=1,
            )

            # Active users - aggregated
            aggregated_active = pd.DataFrame(
                active_user_data_date_range.groupby(by=date_range)["is_active"].sum()
            )
            aggregated_active.columns = ["number_active_users"]

            # New users - aggregated
            active_user_data_date_range["new_active"] = active_user_data_date_range[
                "status"
            ].apply(lambda x: 1 if x == "new_active" else 0)
            aggregated_new_active = pd.DataFrame(
                active_user_data_date_range.groupby(by=date_range)["new_active"].sum()
            )
            aggregated_new_active.columns = ["new_active"]

            # Resurected users - aggregated
            active_user_data_date_range["resurrected"] = active_user_data_date_range[
                "status"
            ].apply(lambda x: 1 if x == "resurrected" else 0)
            aggregated_resurrected = pd.DataFrame(
                active_user_data_date_range.groupby(by=date_range)["resurrected"].sum()
            )
            aggregated_resurrected.columns = ["resurrected"]

            # Churn - aggregated
            active_user_data_date_range["churn"] = active_user_data_date_range[
                "status"
            ].apply(lambda x: -1 if x == "churn" else 0)
            aggregated_churn = pd.DataFrame(
                active_user_data_date_range.groupby(by=date_range)["churn"].sum()
            )
            aggregated_churn.columns = ["churn"]

            # All aggregated
            active_user_data_date_range_aggregated = pd.concat(
                [
                    aggregated_active,
                    aggregated_new_active,
                    aggregated_resurrected,
                    aggregated_churn,
                ],
                axis=1,
            )

            # Retention - start date
            retention_data = active_user_data_date_range.loc[
                :,
                ["user_id", date_range, "is_active"],
            ]
            retention_start_date = (
                retention_data.loc[retention_data["is_active"] == 1]
                .groupby(by="user_id")[date_range]
                .min()
                .reset_index()
            )
            retention_start_date.columns = ["user_id", f"start_{date_range}"]
            retention_start_date[f"start_{date_range}"] = retention_start_date[
                f"start_{date_range}"
            ].apply(
                lambda x: (
                    x - timedelta(days=1)
                    if date_range == "day"
                    else (
                        x - timedelta(days=7)
                        if date_range == "week"
                        else (x - timedelta(days=1)).replace(day=1)
                    )
                )
            )
            retention_data_start_period = retention_start_date.copy()
            retention_data_start_period["is_active"] = 1
            retention_data_start_period.columns = retention_data.columns
            retention_data = pd.concat(
                [retention_data, retention_data_start_period], axis=0
            )

            retention_data = pd.merge(
                retention_data, retention_start_date, how="left", on="user_id"
            )

            # Retention - add total
            retention_start_date_total = (
                retention_start_date.groupby(by=f"start_{date_range}")["user_id"]
                .nunique()
                .reset_index()
            )
            retention_start_date_total.columns = [f"start_{date_range}", "total"]
            retention_data = pd.merge(
                retention_data,
                retention_start_date_total,
                on=f"start_{date_range}",
                how="left",
            )
            retention_data["percentage"] = retention_data.apply(
                lambda x: (
                    100 * x["is_active"] / x["total"] if x["total"] != 0 else None
                ),
                axis=1,
            )

            if date_range == "month":
                retention_data[f"{date_range}_number"] = retention_data.apply(
                    lambda x: (
                        relativedelta(x[date_range], x[f"start_{date_range}"]).years
                        * 12
                        + relativedelta(x[date_range], x[f"start_{date_range}"]).months
                        if x[f"start_{date_range}"] <= x[date_range]
                        else None
                    ),
                    axis=1,
                )
            elif date_range == "week":
                retention_data[f"{date_range}_number"] = retention_data.apply(
                    lambda x: (
                        int((x[date_range] - x[f"start_{date_range}"]).days / 7)
                        if x[f"start_{date_range}"] <= x[date_range]
                        else None
                    ),
                    axis=1,
                )
            elif date_range == "day":
                retention_data[f"{date_range}_number"] = retention_data.apply(
                    lambda x: (
                        (x[date_range] - x[f"start_{date_range}"]).days
                        if x[f"start_{date_range}"] <= x[date_range]
                        else None
                    ),
                    axis=1,
                )

            retention_data = retention_data[retention_data[f"{date_range}_number"] >= 0]

            # Retention - pivot - numbers
            retention_data_pivot_number = retention_data.pivot_table(
                index=f"start_{date_range}",
                columns=f"{date_range}_number",
                values=["is_active"],
                aggfunc="sum",
                dropna=False,
            ).reset_index()

            retention_data_pivot_number_complete = pd.DataFrame(
                [
                    [d] + [None for _ in retention_data_pivot_number.values[0][1:]]
                    for d in self.date_range_dict[date_range]
                    if d not in pd.unique(retention_data[f"start_{date_range}"])
                ],
                columns=retention_data_pivot_number.columns,
            )

            retention_data_pivot_number = pd.concat(
                [retention_data_pivot_number, retention_data_pivot_number_complete],
                axis=0,
            ).reset_index(drop=True)

            retention_data_pivot_number.columns = (
                retention_data_pivot_number.columns.droplevel(0)
            )
            retention_data_pivot_number.columns = [
                x if i != 0 else f"start_{date_range}"
                for i, x in enumerate(retention_data_pivot_number.columns)
            ]
            retention_data_pivot_number = retention_data_pivot_number.set_index(
                f"start_{date_range}"
            ).sort_index(ascending=False)
            retention_data_pivot_number.columns = [
                i for i, _ in enumerate(retention_data_pivot_number.columns)
            ]

            # Retention - pivot - retention
            retention_data_pivot_percentage = (
                (
                    retention_data.pivot_table(
                        index=f"start_{date_range}",
                        columns=f"{date_range}_number",
                        values=["percentage"],
                        aggfunc="sum",
                        dropna=False,
                    )
                )
                .round()
                .reset_index()
            )

            retention_data_pivot_percentage_complete = pd.DataFrame(
                [
                    [d] + [None for _ in retention_data_pivot_percentage.values[0][1:]]
                    for d in self.date_range_dict[date_range]
                    if d not in pd.unique(retention_data[f"start_{date_range}"])
                ],
                columns=retention_data_pivot_percentage.columns,
            )

            retention_data_pivot_percentage = pd.concat(
                [
                    retention_data_pivot_percentage,
                    retention_data_pivot_percentage_complete,
                ],
                axis=0,
            ).reset_index(drop=True)

            retention_data_pivot_percentage.columns = (
                retention_data_pivot_percentage.columns.droplevel(0)
            )
            retention_data_pivot_percentage.columns = [
                x if i != 0 else f"start_{date_range}"
                for i, x in enumerate(retention_data_pivot_percentage.columns)
            ]
            retention_data_pivot_percentage = retention_data_pivot_percentage.set_index(
                f"start_{date_range}"
            ).sort_index(ascending=False)
            retention_data_pivot_percentage.columns = [
                i for i, _ in enumerate(retention_data_pivot_percentage.columns)
            ]

            # Store in dict
            self.active_user_data_dict[date_range] = active_user_data_date_range
            self.active_user_data_aggregated_dict[date_range] = (
                active_user_data_date_range_aggregated
            )
            self.retention_data_dict[date_range] = retention_data
            self.retention_data_aggregated_dict[date_range] = [
                retention_data_pivot_number,
                retention_data_pivot_percentage,
            ]

    def get_kpis(self):
        # Dict charts
        dict_kpis = {}

        # Data
        active_users_day = self.active_user_data_aggregated_dict["day"]
        active_users_week = self.active_user_data_aggregated_dict["week"]
        active_users_month = self.active_user_data_aggregated_dict["month"]

        # KPIs
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        this_week = today - timedelta(days=(today.weekday()) % 7)
        last_week = this_week - timedelta(days=7)
        this_month = today.replace(day=1)
        last_month = this_month - relativedelta(month=1)

        active_users_now = active_users_day["number_active_users"][today]
        active_users_end_last_week = active_users_day["number_active_users"][this_week]
        active_users_end_last_month = active_users_day["number_active_users"][
            this_month
        ]

        dict_kpis["active_users_now"] = go.Figure(
            go.Indicator(
                mode="number",
                value=active_users_now,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Current"},
                number_font={"color": DashboardColors.gray},
            )
        )

        dict_kpis["active_users_end_last_week"] = go.Figure(
            go.Indicator(
                mode="number",
                value=active_users_end_last_week,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "End of last week"},
                number_font={"color": DashboardColors.gray},
            )
        )

        dict_kpis["active_users_end_last_month"] = go.Figure(
            go.Indicator(
                mode="number",
                value=active_users_end_last_month,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "End of last month"},
                number_font={"color": DashboardColors.gray},
            )
        )

        new_users_this_week = (
            active_users_week["new_active"][this_week]
            + active_users_week["resurrected"][this_week]
        )
        new_users_last_week = (
            active_users_week["new_active"][last_week]
            + active_users_week["resurrected"][last_week]
        )

        new_users_this_month = (
            active_users_month["new_active"][this_month]
            + active_users_month["resurrected"][this_month]
        )
        new_users_last_month = (
            active_users_month["new_active"][last_month]
            + active_users_month["resurrected"][last_month]
        )

        dict_kpis["new_users_this_week"] = go.Figure(
            go.Indicator(
                mode="number",
                value=new_users_this_week,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Current week"},
                number_font={"color": DashboardColors.green},
            )
        )

        dict_kpis["new_users_last_week"] = go.Figure(
            go.Indicator(
                mode="number",
                value=new_users_last_week,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Last week"},
                number_font={"color": DashboardColors.green},
            )
        )

        dict_kpis["new_users_this_month"] = go.Figure(
            go.Indicator(
                mode="number",
                value=new_users_this_month,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Current month"},
                number_font={"color": DashboardColors.green},
            )
        )

        dict_kpis["new_users_last_month"] = go.Figure(
            go.Indicator(
                mode="number",
                value=new_users_last_month,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Last month"},
                number_font={"color": DashboardColors.green},
            )
        )

        churn_this_week = -active_users_week["churn"][this_week]
        churn_last_week = -active_users_week["churn"][last_week]

        churn_this_month = -active_users_month["churn"][this_month]
        churn_last_month = -active_users_month["churn"][last_month]

        dict_kpis["churn_this_week"] = go.Figure(
            go.Indicator(
                mode="number",
                value=churn_this_week,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Current week"},
                number_font={"color": DashboardColors.red},
            )
        )

        dict_kpis["churn_last_week"] = go.Figure(
            go.Indicator(
                mode="number",
                value=churn_last_week,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Last week"},
                number_font={"color": DashboardColors.red},
            )
        )

        dict_kpis["churn_this_month"] = go.Figure(
            go.Indicator(
                mode="number",
                value=churn_this_month,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Current month"},
                number_font={"color": DashboardColors.red},
            )
        )

        dict_kpis["churn_last_month"] = go.Figure(
            go.Indicator(
                mode="number",
                value=churn_last_month,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Last month"},
                number_font={"color": DashboardColors.red},
            )
        )

        return dict_kpis

    def get_charts(self, date_range):
        # Dict charts
        dict_chart = {}

        # Data
        active_users = self.active_user_data_aggregated_dict[date_range]
        retention_aggregated_count = self.retention_data_aggregated_dict[date_range][0]
        retention_aggregated_percentage = self.retention_data_aggregated_dict[
            date_range
        ][1]
        retention_data = self.retention_data_dict[date_range]

        # Active users
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=active_users.index,
                y=active_users["number_active_users"],
                fill="tozeroy",
                hovertemplate="<b>%{x}</b>: %{y} users<extra></extra>",
                marker_color=DashboardColors.gray,
                marker_symbol="square",
                mode="lines",
            )
        )
        fig.update_layout(
            title="Active users",
            xaxis_title=date_range.capitalize(),
            yaxis_title="Number of active users",
        )
        dict_chart["active_users"] = fig

        # Growth accounting
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=active_users.index,
                y=active_users["new_active"],
                name="New active",
                hovertemplate="<b>%{x}</b>: %{y} users<extra></extra>",
                marker_color=DashboardColors.green,
            )
        )
        fig.add_trace(
            go.Bar(
                x=active_users.index,
                y=active_users["resurrected"],
                name="Resurrected",
                hovertemplate="<b>%{x}</b>: %{y} users<extra></extra>",
                marker_color=DashboardColors.light_green,
            )
        )
        fig.add_trace(
            go.Bar(
                x=active_users.index,
                y=active_users["churn"],
                name="Churn",
                hovertemplate="<b>%{x}</b>: %{y} users<extra></extra>",
                marker_color=DashboardColors.red,
            )
        )
        fig.update_layout(
            title="Growth accounting",
            xaxis_title=date_range.capitalize(),
            yaxis_title="Number of users",
            barmode="relative",
        )
        dict_chart["growth_accounting"] = fig

        if date_range in ("week", "month"):

            # Churn
            churn_data = active_users.loc[:, ["churn", "number_active_users"]]
            churn_data["number_active_users_previous"] = churn_data[
                "number_active_users"
            ].shift(periods=1)
            churn_data["churn"] = -churn_data["churn"]
            churn_data["churn_percentage"] = churn_data.apply(
                lambda x: (
                    round(100 * x["churn"] / x["number_active_users_previous"], 1)
                    if x["number_active_users_previous"] != 0
                    and x["number_active_users_previous"] != None
                    else None
                ),
                axis=1,
            )

            fig_churn_count = go.Figure()
            fig_churn_count.add_trace(
                go.Bar(
                    x=churn_data.index,
                    y=churn_data["churn"],
                    name="Churn",
                    hovertemplate="<b>%{x}</b>: %{y} users<extra></extra>",
                    marker_color=DashboardColors.red,
                )
            )
            fig_churn_count.update_layout(
                title="Churn users",
                xaxis_title=date_range.capitalize(),
                yaxis_title="Number of churn users",
            )
            dict_chart["churn_count"] = fig_churn_count

            fig_churn_percentage = go.Figure()
            fig_churn_percentage.add_trace(
                go.Scatter(
                    x=churn_data.index,
                    y=churn_data["churn_percentage"],
                    hovertemplate="<b>%{x}</b>: %{y}% churn<extra></extra>",
                    marker_color=DashboardColors.red,
                    marker_symbol="square",
                    mode="markers+lines",
                )
            )
            fig_churn_percentage.update_layout(
                title="Churn users",
                xaxis_title=date_range.capitalize(),
                yaxis_title="Percentage of churn users",
            )
            dict_chart["churn_percentage"] = fig_churn_percentage

            # Retention
            fig_count = go.Figure()
            fig_count.add_trace(
                go.Heatmap(
                    x=retention_aggregated_count.columns,
                    y=[
                        x.strftime("%Y-%m-%d") for x in retention_aggregated_count.index
                    ],
                    z=retention_aggregated_count.values,
                    hovertemplate="<b>Start: %{y}<br>"
                    + f"{date_range.capitalize()}: "
                    + "%{x}</b><br>%{z} users<extra></extra>",
                    text=retention_aggregated_count.values,
                    texttemplate="%{z}",
                    colorscale="Greens",
                    hoverongaps=False,
                    xgap=1,
                    ygap=1,
                )
            )
            fig_count.update_layout(
                title="Retention",
                xaxis_title=date_range.capitalize(),
                yaxis_title=f"Start {date_range.capitalize()}",
                yaxis_autorange="reversed",
                xaxis_side="top",
            )

            fig_percentage = go.Figure()
            fig_percentage.add_trace(
                go.Heatmap(
                    x=retention_aggregated_percentage.columns,
                    y=[
                        x.strftime("%Y-%m-%d")
                        for x in retention_aggregated_percentage.index
                    ],
                    z=retention_aggregated_percentage.values,
                    hovertemplate="<b>Start: %{y}<br>"
                    + f"{date_range.capitalize()}: "
                    + "%{x}</b><br>%{z}%<extra></extra>",
                    text=retention_aggregated_percentage.values,
                    texttemplate="%{z}",
                    colorscale="Blues",
                    hoverongaps=False,
                    xgap=1,
                    ygap=1,
                )
            )
            fig_percentage.update_layout(
                title="Retention (%)",
                xaxis_title=date_range.capitalize(),
                yaxis_title=f"Start {date_range.capitalize()}",
                yaxis_autorange="reversed",
                xaxis_side="top",
            )

            retention_data = retention_data.loc[
                :, [f"start_{date_range}", date_range, "is_active"]
            ]
            for start_date_range in pd.unique(retention_data[f"start_{date_range}"]):
                for d in self.date_range_dict[date_range]:
                    retention_data = pd.concat(
                        [
                            retention_data,
                            pd.DataFrame(
                                [[start_date_range, d, 0]],
                                columns=retention_data.columns,
                            ),
                        ],
                        axis=0,
                    )
            retention_data = (
                retention_data.groupby([f"start_{date_range}", date_range])
                .sum()["is_active"]
                .reset_index()
            )

            retention_data = (
                retention_data.groupby([f"start_{date_range}", date_range])["is_active"]
                .sum()
                .reset_index()
                .sort_values([f"start_{date_range}", date_range])
                .rename(columns={"is_active": "number_active_users"})
            )

            retention_data.loc[
                retention_data[f"start_{date_range}"] == retention_data[date_range],
                "number_active_users",
            ] = 0

            fig_retention_curves = go.Figure()

            for i, cohort in enumerate(
                pd.unique(retention_data[f"start_{date_range}"])
            ):
                data_cohort = retention_data.loc[
                    retention_data[f"start_{date_range}"] == cohort, :
                ]
                if date_range == "month":
                    cohort_names = pd.to_datetime(str(cohort)).strftime("%b %Y")
                else:
                    cohort_names = pd.to_datetime(str(cohort)).strftime("%m/%d/%Y")
                fig_retention_curves.add_trace(
                    go.Scatter(
                        x=data_cohort[date_range],
                        y=data_cohort["number_active_users"],
                        name=cohort_names,
                        text=data_cohort[f"start_{date_range}"].apply(
                            lambda x: (
                                x.strftime("%b %Y")
                                if date_range == "month"
                                else x.strftime("%m/%d/%Y")
                            )
                        ),
                        hovertemplate="<b>Cohort: %{text}</b><br><b>%{x}</b>: %{y} users<extra></extra>",
                        stackgroup="one",
                        mode="lines",
                        marker_color=DashboardColors.palette_category[
                            i % len(DashboardColors.palette_category)
                        ],
                        line_width=0,
                    )
                )
            fig_retention_curves.update_layout(
                title="Retention curves",
                xaxis_title=date_range.capitalize(),
                yaxis_title="Number of active users",
            )

            dict_chart["retention"] = [fig_retention_curves, fig_count, fig_percentage]

        return dict_chart
