import pandas as pd
import random
from datetime import datetime, timedelta
import uuid


class DataGenerator:
    def __init__(self, number_users, min_start_date, max_end_date):
        self.number_users = number_users
        self.min_start_date = min_start_date
        self.max_end_date = max_end_date

    def create_dataset(self):
        data = []
        for _ in range(self.number_users):
            # IDs
            user_id = uuid.uuid4()
            subscription_id = uuid.uuid4()

            # Start date
            date_range_start = (
                min(self.max_end_date, datetime.today()) - self.min_start_date
            )
            random_start_days = random.randint(0, date_range_start.days)
            start_date = self.min_start_date + timedelta(days=random_start_days)

            # End date
            date_range_end = self.max_end_date - start_date
            random_end_days = random.randint(0, date_range_end.days)
            end_date = start_date + timedelta(days=random_end_days)

            data.append([user_id, subscription_id, start_date, end_date])

        list_columns = ["user_id", "subscription_id", "start_date", "end_date"]
        dataset = pd.DataFrame(data, columns=list_columns)

        for c in ["start_date", "end_date"]:
            dataset[c] = dataset[c].apply(
                lambda x: None if x >= datetime.today() else x
            )

        self.dataset = dataset

    def export_csv(self, filename):
        self.dataset.to_csv(filename, index=False)


if __name__ == "__main__":

    # Parameters
    NUMBER_USERS = 1000
    START_DATE = datetime(2022, 1, 1)
    END_DATE = datetime(2025, 1, 1)

    # Generation
    generator = DataGenerator(NUMBER_USERS, START_DATE, END_DATE)
    generator.create_dataset()

    # Export
    FILENAME = "data/dataset.csv"
    generator.export_csv(FILENAME)
