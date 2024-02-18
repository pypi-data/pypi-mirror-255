import pickle
import os
from typing import Generator
from stairsval.core.database.Adapter import DBAdapter

import pandas as pd

GRANULARY: dict[str, str] = {
    "column": "granulary_name",
    "table": "granulary_works",
    "id": "id_granulary_work",
    "res_table": "granulary_resources",
}


class LocalScheduleLoader(DBAdapter):
    # name level constants
    GRANULARY: dict[str, str] = {
        "column": "granulary_name",
        "table": "granulary_works",
        "id": "id_granulary_work",
        "res_table": "granulary_resources",
    }

    def __init__(self, plan_number, *args, **kwargs):
        """

        Args:
            connect: connect object for database.
                     can be a reference to a database service, as well as a sql connect object or None

        """
        super().__init__(*args, **kwargs)
        self.plan_number = plan_number

    def get_all_works_name(self, *args, **kwargs) -> pd.DataFrame:
        """
        Returns all works names

        Returns:
            pandas dataframe
        """
        file_path = f"tests/test_data/gpn/db_outputs/{self.plan_number}/act_names.csv"
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            raise FileNotFoundError(f"No file found at {file_path}")

    def get_all_resources_name(self, *args, **kwargs) -> pd.DataFrame:
        """
        Returns all resources names

        Returns:
            pandas dataframe
        """
        file_path = f"tests/test_data/gpn/db_outputs/{self.plan_number}/res_names.csv"
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            raise FileNotFoundError(f"No file found at {file_path}")

    def get_time_data(self, *args, **kwargs) -> pd.DataFrame:
        """
        Returns all resources names

        Returns:
            pandas dataframe
        """
        file_path = f"tests/test_data/gpn/db_outputs/{self.plan_number}/time_data.csv"
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            raise FileNotFoundError(f"No file found at {file_path}")

    def from_names(self, *args, **kwargs,
    ) -> Generator[pd.DataFrame, None, None]:
        """
        Returns all schedules that include jobs and resources from the lists

        Args:
            [...]

        Returns:
            Pandas dataframe generator
        """
        file_path = f"tests/test_data/gpn/db_outputs/{self.plan_number}/data.pkl"
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                schedules = pickle.load(f)
            for schedule in schedules:
                yield schedule
        else:
            raise FileNotFoundError(f"No file found at {file_path}")
