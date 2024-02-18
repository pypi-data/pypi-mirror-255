import datetime

import pandas as pd

from stairsval.core.dataset_processors.BaseDataset import BaseDataset


class ValidationDataset(BaseDataset):
    def __init__(
        self,
        data_source,
        pools,
        act_names,
        res_names,
    ):
        self.data_source = data_source
        self.pools = pools
        self.act_names = act_names
        self.res_names = res_names

    def collect(self):
        validation_dataset_list = self.data_source.get_data(
            pools=self.pools, res_names=self.res_names
        )
        validation_dataset = pd.DataFrame()
        for df in validation_dataset_list:
            validation_dataset = pd.concat([validation_dataset, df])

        validation_dataset.fillna(0, inplace=True)
        df_pools = {}
        for pool in self.pools:
            df_pools[str(pool)] = []
            for _, df in validation_dataset.groupby("object_name"):
                work_set = set(df["granulary_name"].values)
                if set(pool).issubset(work_set):
                    df = df[["is_work", "granulary_name"] + list(df.columns[13:])]
                    df = df.groupby("granulary_name").sum()
                    df = df.reset_index()
                    df_work = df.loc[df["is_work"] == True]
                    sum_work = df.loc[df["granulary_name"].isin(pool)][
                        ["granulary_name"]
                        + [c for c in df.columns if isinstance(c, datetime.date)]
                    ]  # это я беру имя работ + даты, всё остальное мне не нужно
                    sum_work = sum_work.loc[
                        :, (sum_work != 0).all(axis=0)
                    ]  # тут удаляю работы, у которых все объёмы за все даты нулевые
                    if len(sum_work.columns) > 1:
                        d1 = dict(df_work[df_work.columns[2:]].sum())
                        d2 = dict(sum_work[sum_work.columns[1:]].sum())
                        shared_items = {k: d2[k] for k in d2 if d1[k] == d2[k]}
                        if len(shared_items) != 0:
                            res = df.loc[df["is_work"] == False][
                                ["granulary_name"] + list(shared_items.keys())
                            ]
                            sum_work = sum_work[
                                ["granulary_name"] + list(shared_items.keys())
                            ]
                            sum_work = pd.concat([sum_work, res])
                            df_pools[str(pool)].append(sum_work)
        final_df = pd.DataFrame()
        for p in df_pools:
            for df in df_pools[p]:
                df = df.transpose()
                df.columns = df.iloc[0]
                df.drop(index=df.index[0], axis=0, inplace=True)
                df = df.rename_axis(None, axis=1)
                df.reset_index(drop=True, inplace=True)
                final_df.reset_index(drop=True, inplace=True)
                final_df = pd.concat([final_df, df], ignore_index=True)

        base = datetime.datetime.today()
        date_list = [
            (base + datetime.timedelta(days=x)).strftime("%d.%m.%Y")
            for x in range(final_df.shape[0])
        ]
        final_df.index = date_list
        final_df.fillna(0, inplace=True)
        for c in self.act_names:
            if c not in final_df.columns:
                final_df[c] = 0
        for r in self.res_names:
            if r not in final_df.columns:
                final_df[r] = 0

        new_cols = []
        for c in final_df.columns:
            if c in self.act_names:
                new_cols.append(c + "_act_fact")
            else:
                new_cols.append(c + "_res_fact")
        final_df.columns = new_cols
        return final_df
