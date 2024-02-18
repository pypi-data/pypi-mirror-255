import pandas as pd
import pickle

from stairsval.core.database.Adapter import DBAdapter
from stairsval.core.database.DataSource import DataSource


class DBWrapper(DataSource):
    def __init__(self, connector=None, level=None):
        # Default value for connector if not provided
        if connector is None:
            connector = DBAdapter()
        # Default value for level if not provided
        if level is None:
            level = connector.GRANULARY

        self.adapter = connector
        self.level = level

    def get_data(self, pools, res_names):
        if self.adapter.__class__.__name__ == "LocalScheduleLoader":
            return self.adapter.from_names()

        validation_dataset_list = []
        dfs = self.adapter.get_works_by_pulls(
            work_pulls=pools,
            resource_list=res_names,
            key=self.level,
            res_key=self.adapter.GRANULARY,
        )

        for df in dfs:
            if df is not None:
                df.fillna(0, inplace=True)
            validation_dataset_list.append(df)
        # saving for tests
        # with open('5_data.pkl', 'wb') as f:
        #     pickle.dump(validation_dataset_list, f)
        return validation_dataset_list

    def get_act_names(self):
        df = self.adapter.get_all_works_name()
        # saving for tests
        # df.to_csv("5_act_names.csv")
        return df

    def get_res_names(self):
        df = self.adapter.get_all_resources_name()
        # saving for tests
        # df.to_csv("5_res_names.csv")
        return df

    def get_time_data(self, acts):
        if self.adapter.__class__.__name__ == "LocalScheduleLoader":
            return self.adapter.get_time_data()

        frames = []
        for p in self.adapter.from_names(
            works=acts, key=self.level, objects_limit=-1, ceil_limit=-1
        ):
            frames.append(p)
        validation_dataset = pd.DataFrame()
        for df in frames:
            validation_dataset = pd.concat([validation_dataset, df])
        validation_dataset = validation_dataset[
            ["granulary_name", "physical_volume", "start_date", "finish_date"]
        ]
        validation_dataset.dropna(inplace=True)
        validation_dataset = validation_dataset.loc[
            validation_dataset["granulary_name"].isin(acts)
        ]
        validation_dataset.reset_index(inplace=True, drop=True)
        validation_dataset[["start_date", "finish_date"]] = validation_dataset[
            ["start_date", "finish_date"]
        ].apply(pd.to_datetime)
        validation_dataset["Time"] = (
            validation_dataset["finish_date"] - validation_dataset["start_date"]
        )
        validation_dataset["Time"] = validation_dataset["Time"].dt.days
        validation_dataset = validation_dataset.drop(
            columns=["start_date", "finish_date"]
        )
        validation_dataset.columns = ["Work", "Volume", "Time"]
        # saving for tests
        # validation_dataset.to_csv("5_time_data.csv")
        return validation_dataset
