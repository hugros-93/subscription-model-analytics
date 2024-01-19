import pandas as pd
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go


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

    def fit(self):
        active_user_data = self.dataset.copy()

        self.active_user_data_dict = {}
        self.active_user_data_aggregated_dict = {}

        self.retention_data_dict = {}
        self.retention_data_aggregated_dict = {}

        for date_range in self.date_range_dict:
            
            # Cross join date range and subscriptions
            data_date_range = pd.DataFrame(self.date_range_dict[date_range], columns=[date_range])
            active_user_data_date_range = pd.merge(data_date_range, active_user_data, how="cross")
            active_user_data_date_range = active_user_data_date_range.sort_values(['user_id', date_range])

            # Active subscription in each date range
            active_user_data_date_range["is_active"] = active_user_data_date_range.apply(
                lambda x: 1
                if x["start_date"] <= x[date_range] < x["end_date"]
                else 0,
                axis=1,
            )
            active_user_data_date_range = active_user_data_date_range.groupby([date_range, 'user_id'])['is_active'].max().reset_index()  

            # Status over time ()
            active_user_data_date_range['is_active_previous'] = active_user_data_date_range.groupby('user_id')['is_active'].shift(1, fill_value=0)
            active_user_data_date_range['was_active'] = active_user_data_date_range.groupby('user_id')['is_active'].cumsum()
            active_user_data_date_range['was_active'] = active_user_data_date_range['was_active'].apply(lambda x: 1 if x > 1 else 0)
            active_user_data_date_range['status'] = active_user_data_date_range.apply(
                lambda x:
                    'new_active' if x['is_active'] == 1 and x['is_active_previous'] == 0 and x['was_active'] == 0 else
                    'resurrected' if x['is_active'] == 1 and x['is_active_previous'] == 0 and x['was_active'] == 1 else
                    'churn' if x['is_active'] == 0 and x['is_active_previous'] == 1 else
                    None,
                    axis = 1
            )

            # Active users - aggregated
            aggregated_active = pd.DataFrame(
                active_user_data_date_range.groupby(by=date_range)["is_active"].sum()
            )
            aggregated_active.columns = ["number_active_users"]

            # New users - aggregated
            active_user_data_date_range['new_active'] = active_user_data_date_range['status'].apply(lambda x: 1 if x == 'new_active' else 0)
            aggregated_new_active = pd.DataFrame(
                active_user_data_date_range.groupby(by=date_range)["new_active"].sum()
            )
            aggregated_new_active.columns = ["new_active"]

            # Resurected users - aggregated
            active_user_data_date_range['resurrected'] = active_user_data_date_range['status'].apply(lambda x: 1 if x == 'resurrected' else 0)
            aggregated_resurrected = pd.DataFrame(
                active_user_data_date_range.groupby(by=date_range)["resurrected"].sum()
            )
            aggregated_resurrected.columns = ["resurrected"]
            
            # Churn - aggregated
            active_user_data_date_range['churn'] = active_user_data_date_range['status'].apply(lambda x: -1 if x == 'churn' else 0)
            aggregated_churn = pd.DataFrame(
                active_user_data_date_range.groupby(by=date_range)["churn"].sum()
            )
            aggregated_churn.columns = ["churn"]

            # All aggregated
            active_user_data_date_range_aggregated = pd.concat([aggregated_active, aggregated_new_active, aggregated_resurrected, aggregated_churn], axis = 1)

            # Retention - start date
            retention_data = active_user_data_date_range.loc[active_user_data_date_range['is_active'] == 1, ['user_id', date_range, 'is_active']]
            retention_start_date = retention_data.groupby(by='user_id')[date_range].min().reset_index()
            retention_start_date.columns = ['user_id', f'start_{date_range}']

            # Retention - join
            retention_data = pd.merge(retention_start_date, retention_data, how='left', on='user_id')

            # Retention - add total
            retention_start_date_total = retention_start_date.groupby(by=f'start_{date_range}')['user_id'].nunique().reset_index()
            retention_start_date_total.columns = [f'start_{date_range}', 'total']
            data_date_range.columns = [f'start_{date_range}']
            retention_start_date_total = pd.merge(data_date_range, retention_start_date_total, on=f'start_{date_range}', how='left').fillna(0)
            retention_data = pd.merge(retention_data, retention_start_date_total, on=f'start_{date_range}', how='left').fillna(0)
            retention_data['percentage'] = retention_data.apply(lambda x: x['is_active'] / x['total'], axis = 1)

            # Retention - pivot
            retention_data_pivot_number = retention_data.pivot_table(index=f'start_{date_range}', columns=date_range, values=['is_active'], aggfunc='sum').fillna(0).reset_index()
            retention_data_pivot_percentage = retention_data.pivot_table(index=f'start_{date_range}', columns=date_range, values=['percentage'], aggfunc='sum').fillna(0).reset_index()

            # Store in dict
            self.active_user_data_dict[date_range] = active_user_data_date_range
            self.active_user_data_aggregated_dict[date_range] = active_user_data_date_range_aggregated
            self.retention_data_dict[date_range] = retention_data
            self.retention_data_aggregated_dict[date_range] = [retention_data_pivot_number, retention_data_pivot_percentage]


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
    active_users = model.active_user_data_dict[date_range]
    active_users_aggregated = model.active_user_data_aggregated_dict[date_range]

    retention_aggregated_count = model.retention_data_aggregated_dict[date_range][0]
    retention_aggregated_percentage = model.retention_data_aggregated_dict[date_range][1]

    # Plot
    px.area(active_users_aggregated, x=active_users_aggregated.index, y="number_active_users").show()
    px.bar(active_users_aggregated, x=active_users_aggregated.index, y=["new_active", "churn", "resurrected"]).show()
    px.imshow(retention_aggregated_count.values[1:], aspect='auto', color_continuous_scale='Greens').show()
    px.imshow(retention_aggregated_percentage.values[1:], aspect='auto', color_continuous_scale='Blues').show()
