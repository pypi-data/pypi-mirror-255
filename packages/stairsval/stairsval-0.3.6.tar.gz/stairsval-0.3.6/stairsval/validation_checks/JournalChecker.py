import datetime
import math

import numpy as np
import pandas as pd


class JournalChecker:
    def __init__(self, journal: dict, work_day: int = 11) -> None:
        self.journal = journal
        self.work_day = work_day

    def validate_resources(
        self, pool: list, res_name: str, model_dataset: pd.DataFrame, index: datetime
    ):
        res_volume = model_dataset.loc[index, res_name]
        sum_res = 0
        for w in pool:
            work_volume = model_dataset.loc[index, w]
            if w.split("_act_fact")[0] not in self.journal:
                return "grey", 0, 0
            else:
                if (
                    res_name.split("_res_fact")[0]
                    in self.journal[w.split("_act_fact")[0].split("_act_fact")[0]][
                        "resources"
                    ]
                ):
                    model = self.journal[w.split("_act_fact")[0].split("_act_fact")[0]][
                        "resources"
                    ][res_name.split("_res_fact")[0]]
                    sum_res += (
                        (work_volume * model["number"])
                        / model["productivity"]
                        / self.work_day
                    )
        q1 = sum_res - sum_res * 0.5
        q99 = sum_res + sum_res * 0.5
        if (res_volume < q1) | (res_volume > q99):
            return "red", q1, q99
        else:
            return "green", q1, q99

    def validate_time(self, c_act: list, df_wind_model: pd.DataFrame, index: int):
        if c_act[0].split("_act_fact")[0] not in self.journal:
            return "grey", 0, 0, 0
        else:
            act_volume = df_wind_model.loc[index, c_act[0]]
            res_for_act = []
            avg_productivity = 0
            df_wind_model_column_names = df_wind_model.columns
            act_resources = self.journal[c_act[0].split("_act_fact")[0]]["resources"]
            for r in act_resources:
                if r + "_res_fact" in df_wind_model_column_names:
                    number = self.journal[c_act[0].split("_act_fact")[0]]["resources"][
                        r
                    ]["number"]
                    value_to_append = (
                        df_wind_model.loc[index, r + "_res_fact"]
                    ) / number

                    if value_to_append != 0:
                        res_for_act.append(value_to_append)

                    avg_productivity += self.journal[c_act[0].split("_act_fact")[0]][
                        "resources"
                    ][r]["productivity"]

            if not res_for_act:
                return "grey", 0, 0, 0

            avg_productivity /= len(res_for_act)
            min_res = np.min(res_for_act) * 11
            prod = avg_productivity * min_res
            time = act_volume / prod
            q1 = time - time * 0.5
            q99 = time + time * 0.5
            act_time = df_wind_model.loc[
                index, c_act[0].split("_act_fact")[0] + "_real_time_act"
            ]
            if (act_time < q1) | (act_time > q99):
                return "red", q1, q99, prod
            else:
                return "green", q1, q99, prod

    def process_key_resources(self, c_act, r, ci, model_dataset, i):
        key = str(c_act) + " " + r + " " + ci
        work_volume = model_dataset.loc[i, ci]
        res_volume = model_dataset.loc[i, r]
        power = self._check_volume_power(work_volume)
        step = 10 ** (power - 1)
        low_bound = work_volume - step
        up_bound = work_volume + step
        X = list(np.linspace(low_bound, work_volume, 15)) + list(
            np.linspace(work_volume, up_bound, 15)
        )
        if (
            r.split("_res_fact")[0]
            not in self.journal[ci.split("_act_fact")[0]]["resources"]
        ):
            Y = [0] * len(X)
            blue_points = {
                "x": list(X),
                "y": list(Y),
            }
            black_points = {
                "x": [work_volume],
                "y": [0],
            }
            star = {
                "x": work_volume,
                "y": res_volume,
            }
            return key, blue_points, black_points, star
        else:
            model = self.journal[ci.split("_act_fact")[0]]["resources"][
                r.split("_res_fact")[0]
            ]
            Y = []
            for xi in X:
                Y.append((xi * model["number"]) / model["productivity"] / self.work_day)
            blue_points = {
                "x": list(X),
                "y": list(Y),
            }
            black_points = {
                "x": [work_volume],
                "y": [
                    (work_volume * model["number"])
                    / model["productivity"]
                    / self.work_day
                ],
            }
            star = {
                "x": work_volume,
                "y": res_volume,
            }
            return key, blue_points, black_points, star

    def process_key_time(self, c_act, df_wind_model, i, prod):
        work_volume = df_wind_model.loc[i, c_act[0]]
        power = self._check_volume_power(work_volume)
        step = 10 ** (power - 1)
        low_bound = work_volume - step
        up_bound = work_volume + step
        X = list(np.linspace(low_bound, work_volume, 15)) + list(
            np.linspace(work_volume, up_bound, 15)
        )
        Y = []
        for xi in X:
            Y.append(xi / prod)
        blue_points = {
            "x": list(X),
            "y": list(Y),
        }
        black_points = {
            "x": [work_volume],
            "y": [work_volume / prod],
        }
        star = {
            "x": work_volume,
            "y": df_wind_model.loc[
                i, c_act[0].split("_act_fact")[0] + "_real_time_act"
            ],
        }
        return blue_points, black_points, star

    @staticmethod
    def _check_volume_power(volume):
        power = math.log10(volume)
        return math.floor(power) if power < 0 else math.ceil(power)
