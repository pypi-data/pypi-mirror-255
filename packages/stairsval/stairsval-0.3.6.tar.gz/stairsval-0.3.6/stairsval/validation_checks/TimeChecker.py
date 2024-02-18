import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .AbstractChecker import AbstractChecker
from .JournalChecker import JournalChecker


class TimeChecker(AbstractChecker):
    def __init__(self, journal: dict = None):
        super().__init__()
        self.journal = journal

    def validate(
        self, df_wind_model: pd.DataFrame, df_wind_val: pd.DataFrame, act: list
    ):
        df_wind_model = df_wind_model.drop_duplicates()
        df_stat = pd.DataFrame()
        dict_fig = {}
        final_df = pd.DataFrame()
        j = 0
        for c in act:
            dict_fig[c] = []
            volumes = []
            for i in df_wind_model.index:
                if df_wind_model.loc[i, c] != 0:
                    c_act = [c]
                    volume = [df_wind_model.loc[i, ci] for ci in c_act]
                    delta = [self.percent_delta * volume_i for volume_i in volume]
                    sample = df_wind_val.copy()
                    for k, ci in enumerate(c_act):
                        sample = sample.loc[
                            (sample[ci] >= volume[k] - delta[k])
                            & (sample[ci] <= volume[k] + delta[k])
                        ]
                    if sample.shape[0] > 3:
                        df_stat, dict_for_sample = self.handle_sample(
                            i,
                            c,
                            df_wind_model,
                            sample,
                            df_wind_val,
                            df_stat,
                            j,
                        )
                        if volume not in volumes:
                            dict_fig[c].append(
                                {
                                    "volume": [round(v, 1) for v in volume],
                                    "fig_data": dict_for_sample,
                                    "color": dict_for_sample["Color"],
                                }
                            )
                            volumes.append(volume)
                    else:
                        journal_validation = JournalChecker(journal=self.journal)
                        color, q1, q99, prod = journal_validation.validate_time(
                            c_act, df_wind_model, i
                        )
                        if color == "grey":
                            df_stat.loc[j, "Work"] = c
                            df_stat.loc[j, "Time label"] = color
                        else:
                            (
                                blue_points,
                                black_points,
                                star,
                            ) = journal_validation.process_key_time(
                                c_act, df_wind_model, i, prod
                            )
                            fig_data = {
                                "Blue points": blue_points,
                                "Black points": black_points,
                                "Star": star,
                                "Color": color,
                                "Q1": q1,
                                "Q99": q99,
                            }
                            if volume not in volumes:
                                dict_fig[c].append(
                                    {
                                        "volume": [round(v, 1) for v in volume],
                                        "fig_data": fig_data,
                                        "color": color,
                                    }
                                )
                                volumes.append(volume)
                            df_stat.loc[j, "Work"] = c
                            df_stat.loc[j, "Time label"] = color

                    j += 1

        not_grey = df_stat.loc[df_stat["Time label"] != "grey"]
        not_perc = ((df_stat.shape[0] - not_grey.shape[0]) / df_stat.shape[0]) * 100
        norm_df = df_stat.loc[df_stat["Time label"] == "green"]
        norm_perc = 0
        if not_perc != 100:
            norm_perc = ((norm_df.shape[0]) / not_grey.shape[0]) * 100

        final_df = self.finalize_dataframe(act, final_df, not_grey)
        return final_df, dict_fig, norm_perc, not_perc

    def handle_sample(self, i, c, df_wind_model, sample, df_wind_val, df_stat, j):
        value = df_wind_model.loc[i, c.split("_act_fact")[0] + "_real_time_act"]
        q1, q99 = np.quantile(
            sample[c.split("_act_fact")[0] + "_real_time_act"].values,
            [self.lower_quantile, self.upper_quantile],
        )
        q1 = int(q1)
        q99 = int(q99)
        if value < q1 or value > q99:
            color = "red"
        else:
            color = "green"
        df_stat.loc[j, "Work"] = c
        df_stat.loc[j, "Time label"] = color
        sample_dict = self.create_figure_dict(
            c, color, sample, df_wind_val, df_wind_model, i, q1, q99
        )
        return df_stat, sample_dict

    @staticmethod
    def create_figure_dict(
        c,
        color,
        sample,
        df_wind_val: pd.DataFrame,
        df_wind_model: pd.DataFrame,
        i,
        q1,
        q99,
    ):
        blue_points = {
            "x": list(df_wind_val[c].values),
            "y": list(df_wind_val[c.split("_act_fact")[0] + "_real_time_act"].values),
        }
        black_points = {
            "x": list(sample[c].values),
            "y": list(sample[c.split("_act_fact")[0] + "_real_time_act"].values),
        }
        star = {
            "x": df_wind_model.loc[i, c],
            "y": df_wind_model.loc[i, c.split("_act_fact")[0] + "_real_time_act"],
        }
        return {
            "Blue points": blue_points,
            "Black points": black_points,
            "Star": star,
            "Color": color,
            "Q1": q1,
            "Q99": q99,
        }

    @staticmethod
    def finalize_dataframe(act: list, final_df, not_grey):
        for i, c in enumerate(act):
            final_df.loc[i, "Name"] = c
            sample = not_grey.loc[not_grey["Work"] == c]
            count_dict = sample["Time label"].value_counts().to_dict()
            if "red" in count_dict and "green" not in count_dict:
                final_df.loc[i, "Time per Volume Unit"] = 0
            elif "green" not in count_dict and "red" not in count_dict:
                final_df.loc[i, "Time per Volume Unit"] = None
            else:
                final_df.loc[i, "Time per Volume Unit"] = (
                    count_dict["green"] / sample.shape[0]
                ) * 100
        return final_df

    def common_validation(self, ksg_data: dict, val_data, plan_type: str):
        df_validation_table = pd.DataFrame()
        fig_dict = dict()
        norm_perc = 0
        not_perc = 0
        i = 0
        if plan_type == "gpn":
            for w in ksg_data["schedule"]["works"]:
                i += 1
                work_name = w["display_name"]
                time = w["start_end_time"][1]["value"] - w["start_end_time"][0]["value"]
                work_vol = w["volume"]
                down_v = work_vol - 0.5 * work_vol
                up_v = work_vol + 0.5 * work_vol
                val_sample = val_data.loc[
                    (val_data["Work"] == work_name)
                    & (val_data["Volume"] >= down_v)
                    & (val_data["Volume"] <= up_v)
                    & (val_data["Time"] != 0)
                ]
                if val_sample.shape[0] > 3:
                    q1, q99 = np.quantile(
                        val_sample["Time"].values,
                        [self.lower_quantile, self.upper_quantile],
                    )
                    if (time > q1) and (time < q99):
                        df_validation_table.loc[i, "Work name"] = work_name
                        df_validation_table.loc[i, "Validation Results"] = "green"
                        key = work_name
                        counts, bins, _ = plt.hist(val_sample["Time"].values)
                        fig_dict[key] = {
                            "Line": time,
                            "color": "green",
                            "Hight": counts,
                            "Bins": bins,
                            "Q1": q1,
                            "Q99": q99,
                        }
                    else:
                        df_validation_table.loc[i, "Work name"] = work_name
                        df_validation_table.loc[i, "Validation Results"] = "red"
                        key = work_name
                        counts, bins, _ = plt.hist(val_sample["Time"].values)
                        fig_dict[key] = {
                            "Line": time,
                            "color": "red",
                            "Hight": counts,
                            "Bins": bins,
                            "Q1": q1,
                            "Q99": q99,
                        }
                else:
                    df_validation_table.loc[i, "Work name"] = work_name
                    df_validation_table.loc[i, "Validation Results"] = None
        elif plan_type == "s7":
            for w in ksg_data["schedule"]["works"]:
                i += 1
                work_name = w["name"]
                time = w["start_end_time"][1]["value"] - w["start_end_time"][0]["value"]
                res_type = "res_parent"
                act_name = None
                defect_name = None
                if ":" in work_name:
                    act_name = work_name.split(":")[0]
                    defect_name = work_name.split(":")[-1]
                    res_type = "res_child"

                if ":" in work_name:
                    val_sample = val_data[1].loc[
                        (val_data[1]["class_child"] == defect_name)
                        & (val_data[1]["event_name_parent"] == act_name)
                    ]
                else:
                    val_sample = val_data[0].loc[
                        (val_data[0]["event_name_parent"] == work_name)
                    ]
                if val_sample.shape[0] > 3:
                    val_sample["Time"] = (
                        val_sample[res_type + "_users"]
                        / val_sample[res_type + "_hours"]
                    )
                    q1, q99 = np.quantile(
                        val_sample["Time"].values,
                        [self.lower_quantile, self.upper_quantile],
                    )
                    if (time >= q1) and (time <= q99):
                        df_validation_table.loc[i, "Work name"] = work_name
                        df_validation_table.loc[i, "Validation Results"] = "green"
                        key = work_name
                        counts, bins, _ = plt.hist(val_sample["Time"].values)
                        fig_dict[key] = {
                            "Line": time,
                            "color": "green",
                            "Hight": counts,
                            "Bins": bins,
                            "Q1": q1,
                            "Q99": q99,
                        }
                    else:
                        df_validation_table.loc[i, "Work name"] = work_name
                        df_validation_table.loc[i, "Validation Results"] = "red"
                        key = work_name
                        counts, bins, _ = plt.hist(val_sample["Time"].values)
                        fig_dict[key] = {
                            "Line": time,
                            "color": "red",
                            "Hight": counts,
                            "Bins": bins,
                            "Q1": q1,
                            "Q99": q99,
                        }
                else:
                    df_validation_table.loc[i, "Work name"] = work_name
                    df_validation_table.loc[i, "Validation Results"] = None
        not_perc = (
            (
                df_validation_table.loc[
                    df_validation_table["Validation Results"].isnull()
                ].shape[0]
            )
            / df_validation_table.shape[0]
        ) * 100
        if not_perc == 100:
            norm_perc = 0
        else:
            not_non = df_validation_table.loc[
                df_validation_table["Validation Results"].notnull()
            ]
            norm_perc = (
                (not_non.loc[not_non["Validation Results"] == "green"].shape[0])
                / not_non.shape[0]
            ) * 100
        return df_validation_table, fig_dict, norm_perc, not_perc
