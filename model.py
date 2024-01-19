import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np

import plotly.express as px


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
        self.min_start_date = dataset["start_date"].min() - timedelta(days=31)
        self.max_end_date = dataset["end_date"].max() + timedelta(days=31)

        # Date range - days
        self.list_date_range_day = [
            self.min_start_date + timedelta(days=i)
            for i in range(0, (self.max_end_date - self.min_start_date).days)
        ]

        # Date range - weeks
        self.min_start_date_week = self.min_start_date - timedelta(
            days=(self.min_start_date.weekday() - 0) % 7
        )
        self.max_end_date_week = self.max_end_date - timedelta(
            days=(self.max_end_date.weekday() - 0) % 7
        )
        self.list_date_range_week = [
            self.min_start_date_week + timedelta(days=7 * i)
            for i in range(
                0, int((self.max_end_date_week - self.min_start_date_week).days / 7)
            )
        ]

        # Date range - months
        self.min_start_date_month = self.min_start_date.replace(day=1)
        self.max_end_date_month = self.max_end_date.replace(day=1)
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

    def get_active_users(self):
        active_user_data = self.dataset.copy()

        self.active_user_data_dict = {}
        self.active_user_data_aggregated_dict = {}

        for date_range in self.date_range_dict:
            # Active users and growth accounting
            data_date_range = pd.DataFrame(self.date_range_dict[date_range], columns=[date_range])
            active_user_data_date_range = pd.merge(data_date_range, active_user_data, how="cross")
            active_user_data_date_range = active_user_data_date_range.sort_values(['user_id', date_range])

            active_user_data_date_range["is_active"] = active_user_data_date_range.apply(
                lambda x: 1
                if x["start_date"] <= x[date_range] < x["end_date"]
                else 0,
                axis=1,
            )

            active_user_data_date_range = active_user_data_date_range.groupby([date_range, 'user_id'])['is_active'].max().reset_index()           
            active_user_data_date_range['is_active_previous'] = active_user_data_date_range.groupby('user_id')['is_active'].shift(1, fill_value=0)
            active_user_data_date_range['was_active'] = active_user_data_date_range.groupby('user_id')['is_active'].cumsum()
            active_user_data_date_range['was_active'] = active_user_data_date_range['was_active'].apply(lambda x: 1 if x > 1 else 0)

            print(active_user_data_date_range)


            active_user_data_date_range['status'] = active_user_data_date_range.apply(
                lambda x:
                    'new_active' if x['is_active'] == 1 and x['is_active_previous'] == 0 and x['was_active'] == 0 else
                    'resurrected' if x['is_active'] == 1 and x['is_active_previous'] == 0 and x['was_active'] == 1 else
                    'churn' if x['is_active'] == 0 and x['is_active_previous'] == 1 else
                    None,
                    axis = 1
            )

            self.active_user_data_dict[date_range] = active_user_data_date_range

            # Aggregated
            aggregated_active = pd.DataFrame(
                active_user_data_date_range.groupby(by=date_range)["is_active"].sum()
            )
            aggregated_active.columns = ["number_active_users"]

            active_user_data_date_range['new_active'] = active_user_data_date_range['status'].apply(lambda x: 1 if x == 'new_active' else 0)
            active_user_data_date_range['resurrected'] = active_user_data_date_range['status'].apply(lambda x: 1 if x == 'resurrected' else 0)
            active_user_data_date_range['churn'] = active_user_data_date_range['status'].apply(lambda x: -1 if x == 'churn' else 0)

            aggregated_new_active = pd.DataFrame(
                active_user_data_date_range.groupby(by=date_range)["new_active"].sum()
            )
            aggregated_new_active.columns = ["new_active"]

            aggregated_resurrected = pd.DataFrame(
                active_user_data_date_range.groupby(by=date_range)["resurrected"].sum()
            )
            aggregated_resurrected.columns = ["resurrected"]

            aggregated_churn = pd.DataFrame(
                active_user_data_date_range.groupby(by=date_range)["churn"].sum()
            )
            aggregated_churn.columns = ["churn"]

            active_user_data_date_range_aggregated = pd.concat([aggregated_active, aggregated_new_active, aggregated_resurrected, aggregated_churn], axis = 1)
            
            self.active_user_data_aggregated_dict[date_range] = active_user_data_date_range_aggregated


if __name__ == "__main__":
    # Load file
    FILENAME = "dataset.csv"
    dataset = pd.read_csv(FILENAME)
    dataset["start_date"] = pd.to_datetime(dataset["start_date"])
    dataset["end_date"] = pd.to_datetime(dataset["end_date"])

    new_dataset = dataset.copy()
    dataset["start_date"] = dataset["start_date"] + timedelta(days=5*300)
    dataset["end_date"] = dataset["end_date"] + timedelta(days=5*300)

    dataset = pd.concat([dataset, new_dataset], axis = 0)

    # Create data model
    model = DataModel(dataset)
    model.get_active_users()

    # Get data
    date_range = 'week'
    df = model.active_user_data_dict[date_range]
    df_aggregated = model.active_user_data_aggregated_dict[date_range]

    # Plot
    px.area(df_aggregated, x=df_aggregated.index, y="number_active_users").show()
    px.bar(df_aggregated, x=df_aggregated.index, y=["new_active", "churn", "resurrected"]).show()
    
