import datetime

import pandas as pd

from stairsval.core.dataset_processors.BaseDataset import BaseDataset


class PlanDataset(BaseDataset):
    def __init__(self, ksg_data):
        self.ksg_data = ksg_data

    def collect(self):
        model_dataset = pd.DataFrame()
        all_descendants = []

        activity_ids = set()
        start = datetime.datetime.today()
        for i, w in enumerate(self.ksg_data["schedule"]["works"]):
            activity_id = w["id"]
            if activity_id in activity_ids:
                raise Exception(
                    f"ERROR: Duplicated activity_id detected: {activity_id}"
                )
            activity_ids.add(activity_id)

            current_descendant_activities = self.ksg_data["wg"]["nodes"][i].get(
                "parent_edges", []
            )
            all_descendants.extend(current_descendant_activities)

            name = w["display_name"] + "_act_fact"
            days = w["start_end_time"][1]["value"] - w["start_end_time"][0]["value"]
            vol = float(w["volume"])
            res_data = dict()
            for r in w["workers"]:
                res_data[r["name"]] = r["_count"]
            if not res_data:
                raise Exception(
                    'ERROR: One or more activities has no resources. Check "workers" fields'
                )
            vol_per = vol / days
            start_d = start + datetime.timedelta(days=w["start_end_time"][0]["value"])
            end_d = start + datetime.timedelta(days=w["start_end_time"][1]["value"])
            delta = datetime.timedelta(days=1)
            while start_d <= end_d:
                formatted_date = start_d.strftime("%d.%m.%Y")
                model_dataset.loc[formatted_date, name] = vol_per
                for k in res_data.keys():
                    model_dataset.loc[formatted_date, k + "_res_fact"] = (
                        res_data[k] / days
                    )
                start_d += delta
        model_dataset.fillna(0, inplace=True)
        return model_dataset

    def get_act_names(self):
        act = []
        for w in self.ksg_data["schedule"]["works"]:
            act.append(w["display_name"])
        return act

    def get_res_names(self):
        res = []
        for w in self.ksg_data["schedule"]["works"]:
            for r in w["workers"]:
                if r["name"] not in res:
                    res.append(r["name"])
        return res

    def get_pools(self):
        model_dataset = pd.DataFrame()
        start = datetime.datetime.today()
        for i, w in enumerate(self.ksg_data["schedule"]["works"]):
            name = w["display_name"]
            # Keep start_d and end_d as datetime objects
            start_d = start + datetime.timedelta(days=w["start_end_time"][0]["value"])
            end_d = start + datetime.timedelta(days=w["start_end_time"][1]["value"])
            vol = float(w["volume"])
            # Subtract the datetime objects
            days = (end_d - start_d).days + 1
            vol_per = vol / days
            delta = datetime.timedelta(days=1)
            while start_d <= end_d:
                formatted_date = start_d.strftime(
                    "%d.%m.%Y"
                )  # Convert to string format here
                model_dataset.loc[formatted_date, name] = vol_per
                start_d += delta
        model_dataset.fillna(0, inplace=True)
        work_pools = []
        for i in model_dataset.index:
            pool = []
            for c in model_dataset.columns:
                if model_dataset.loc[i, c] != 0:
                    pool.append(c)
            if pool not in work_pools:
                work_pools.append(pool)

        return work_pools
