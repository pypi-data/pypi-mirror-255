import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .AbstractChecker import AbstractChecker
from .JournalChecker import JournalChecker


class ResourcesChecker(AbstractChecker):
    def __init__(self, res: list, journal: dict = None):
        super().__init__()
        self.res = res
        self.journal = journal

    def validate(
        self, model_dataset: pd.DataFrame, df_wind_val: pd.DataFrame, act: list
    ):
        model_dataset = model_dataset.drop_duplicates()
        act = [c + "_act_fact" for c in act]
        df_perc_agg = pd.DataFrame()
        df_style = pd.DataFrame()
        df_volume = pd.DataFrame()
        fig_dict = dict()
        for i in model_dataset.index:
            c_pair = [ci for ci in act if model_dataset.loc[i, ci] != 0]
            c_act = c_pair
            volume = [model_dataset.loc[i, ci] for ci in c_act]
            delta = [self.percent_delta * volume_i for volume_i in volume]
            not_c = [ci for ci in act if ci not in c_act]
            zero_ind = df_wind_val[not_c][(df_wind_val[not_c] == 0).all(axis=1)].index
            sample_non = df_wind_val.loc[zero_ind, :]

            non_zero = sample_non[c_act][(sample_non[c_act] != 0).all(axis=1)].index
            sample_non = pd.DataFrame(sample_non.loc[non_zero, :])
            sample = pd.DataFrame()
            for j, ci in enumerate(c_act):
                sample = sample_non.loc[
                    (sample_non[ci] >= volume[j] - delta[j])
                    & (sample_non[ci] <= volume[j] + delta[j])
                ]
            sample = pd.DataFrame(sample)

            if sample.shape[0] > 4:
                for r in self.res:
                    value = model_dataset.loc[i, r]
                    q1, q99 = np.quantile(
                        sample[r].values, [self.lower_quantile, self.upper_quantile]
                    )
                    if value < q1 or value > q99:
                        df_style.loc[i, r] = "red"
                        df_volume.loc[i, r] = value
                        for ci in c_act:
                            key, blue_points, black_points, star = self._process_key(
                                c_act, r, ci, sample, sample_non, model_dataset, i
                            )

                            color = "red"
                            fig_dict[key] = {
                                "Blue points": blue_points,
                                "Black points": black_points,
                                "Star": star,
                                "Color": color,
                            }
                    else:
                        df_style.loc[i, r] = "green"
                        df_volume.loc[i, r] = value
                        for ci in c_act:
                            key, blue_points, black_points, star = self._process_key(
                                c_act, r, ci, sample, sample_non, model_dataset, i
                            )

                            color = "green"
                            fig_dict[key] = {
                                "Blue points": blue_points,
                                "Black points": black_points,
                                "Star": star,
                                "Color": color,
                            }
                df_style.loc[i, "Name"] = str(c_act)
                df_volume.loc[i, "Name"] = str(c_act)
            elif sample.shape[0] <= 4:
                journal_validation = JournalChecker(journal=self.journal)
                df_style.loc[i, "Name"] = str(c_act)
                df_volume.loc[i, "Name"] = str(c_act)
                for r in self.res:
                    value = model_dataset.loc[i, r]
                    df_volume.loc[i, r] = value
                    color, q1, q99 = journal_validation.validate_resources(
                        c_act, r, model_dataset, i
                    )
                    df_style.loc[i, r] = color
                    if color != "grey":
                        for ci in c_act:
                            (
                                key,
                                blue_points,
                                black_points,
                                star,
                            ) = journal_validation.process_key_resources(
                                c_act, r, ci, model_dataset, i
                            )
                            fig_dict[key] = {
                                "Blue points": blue_points,
                                "Black points": black_points,
                                "Star": star,
                                "Color": color,
                            }

        new_df_color = df_style[(df_style != "grey").all(1)]
        not_perc = (
            (
                (df_style.shape[0] * df_style.shape[1])
                - (new_df_color.shape[0] * new_df_color.shape[1])
            )
            / (df_style.shape[0] * df_style.shape[1])
        ) * 100
        j = 0

        for c in act:
            new_sample = new_df_color.loc[new_df_color["Name"].str.count(c) != 0]
            if new_sample.shape[0] != 0:
                for r in self.res:
                    df_perc_agg.loc[j, "Resource name"] = r
                    df_perc_agg.loc[j, "Work name"] = c
                    value_dict = new_sample[r].value_counts().to_dict()
                    if "green" in list(value_dict.keys()):
                        df_perc_agg.loc[j, "Ratio"] = round(
                            ((value_dict["green"]) / new_sample.shape[0]) * 100
                        )
                    else:
                        df_perc_agg.loc[j, "Ratio"] = 0
                    j += 1
            else:
                for r in self.res:
                    df_perc_agg.loc[j, "Resource name"] = r
                    df_perc_agg.loc[j, "Work name"] = c
                    df_perc_agg.loc[j, "Ratio"] = 0
                    j += 1

        norm_perc = df_perc_agg["Ratio"].mean()
        df_final_volume = pd.DataFrame()
        df_final_style = pd.DataFrame()
        for i, p in enumerate(list(df_volume["Name"].unique())):
            sample1 = df_volume.loc[df_volume["Name"] == p]
            sample2 = df_style.loc[df_style["Name"] == p]
            date = str(sample1.index[0]) + " " + str(sample1.index[-1])
            df_final_volume.loc[i, "Name"] = p
            df_final_volume.loc[i, "Dates"] = date
            df_final_volume.loc[i, self.res] = sample1.loc[sample1.index[0], self.res]
            df_final_style.loc[i, "Name"] = p
            df_final_style.loc[i, "Dates"] = date
            df_final_style.loc[i, self.res] = sample2.loc[sample2.index[0], self.res]

        return (
            df_perc_agg,
            df_final_volume,
            df_final_style,
            fig_dict,
            not_perc,
            norm_perc,
        )

    def common_validation(self, ksg_data: dict, val_data, plan_type: str):
        df_validation_table = pd.DataFrame()
        fig_dict = dict()
        i = 0
        if plan_type == "gpn":
            for w in ksg_data["schedule"]["works"]:
                work_name = w["display_name"]
                for r in w["workers"]:
                    i += 1
                    res_name = r["name"]
                    res_volume = r["_count"]
                    val_sample = val_data.loc[val_data[work_name + "_act_fact"] != 0]
                    if val_sample.shape[0] > 3:
                        q1, q99 = np.quantile(
                            val_sample[res_name + "_res_fact"].values,
                            [self.lower_quantile, self.upper_quantile],
                        )
                        if (res_volume >= q1) and (res_volume <= q99):
                            df_validation_table.loc[i, "Work names"] = work_name
                            df_validation_table.loc[i, "Resources"] = res_name
                            df_validation_table.loc[i, "Validation Results"] = "green"
                            key = work_name + " " + res_name
                            counts, bins, _ = plt.hist(
                                val_sample[res_name + "_res_fact"].values
                            )
                            fig_dict[key] = {
                                "Line": res_volume,
                                "color": "green",
                                "Hight": counts,
                                "Bins": bins,
                                "Q1": q1,
                                "Q99": q99,
                            }
                        else:
                            df_validation_table.loc[i, "Work names"] = work_name
                            df_validation_table.loc[i, "Resources"] = res_name
                            df_validation_table.loc[i, "Validation Results"] = "red"
                            key = work_name + " " + res_name
                            counts, bins, _ = plt.hist(
                                val_sample[res_name + "_res_fact"].values
                            )
                            fig_dict[key] = {
                                "Line": res_volume,
                                "color": "red",
                                "Hight": counts,
                                "Bins": bins,
                                "Q1": q1,
                                "Q99": q99,
                            }
                    else:
                        df_validation_table.loc[i, "Work names"] = work_name
                        df_validation_table.loc[i, "Resources"] = res_name
                        df_validation_table.loc[i, "Validation Results"] = None
        elif plan_type == "s7":
            for w in ksg_data["schedule"]["works"]:
                work_name = w["name"]
                act_name = None
                defect_name = None
                res_type = "res_parent"
                if ":" in work_name:
                    act_name = work_name.split(":")[0]
                    defect_name = work_name.split(":")[-1]
                    res_type = "res_child"
                for r in w["workers"]:
                    i += 1
                    res_name = r["name"]
                    res_volume = r["_count"]
                    if ":" in work_name:
                        val_sample = val_data[1].loc[
                            (val_data[1]["class_child"] == defect_name)
                            & (val_data[1]["res_child"] == res_name)
                            & (val_data[1]["event_name_parent"] == act_name)
                        ]
                    else:
                        val_sample = val_data[0].loc[
                            (val_data[0]["res_parent"] == res_name)
                            & (val_data[0]["event_name_parent"] == work_name)
                        ]
                    if val_sample.shape[0] > 3:
                        q1, q99 = np.quantile(
                            val_sample[res_type + "_users"].values,
                            [self.lower_quantile, self.upper_quantile],
                        )
                        if (res_volume >= q1) and (res_volume <= q99):
                            df_validation_table.loc[i, "Work names"] = work_name
                            df_validation_table.loc[i, "Resources"] = res_name
                            df_validation_table.loc[i, "Validation Results"] = "green"
                            key = work_name + " " + res_name
                            counts, bins, _ = plt.hist(
                                val_sample[res_type + "_users"].values
                            )
                            fig_dict[key] = {
                                "Line": res_volume,
                                "color": "green",
                                "Hight": counts,
                                "Bins": bins,
                                "Q1": q1,
                                "Q99": q99,
                            }
                        else:
                            df_validation_table.loc[i, "Work names"] = work_name
                            df_validation_table.loc[i, "Resources"] = res_name
                            df_validation_table.loc[i, "Validation Results"] = "red"
                            key = work_name + " " + res_name
                            counts, bins, _ = plt.hist(
                                val_sample[res_type + "_users"].values
                            )
                            fig_dict[key] = {
                                "Line": res_volume,
                                "color": "red",
                                "Hight": counts,
                                "Bins": bins,
                                "Q1": q1,
                                "Q99": q99,
                            }
                    else:
                        df_validation_table.loc[i, "Work names"] = work_name
                        df_validation_table.loc[i, "Resources"] = res_name
                        df_validation_table.loc[i, "Validation Results"] = None
                else:
                    df_validation_table.loc[i, "Work names"] = work_name
                    df_validation_table.loc[i, "Resources"] = None
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

    @staticmethod
    def _process_key(c_act, r, ci, sample, sample_non, model_dataset, i):
        key = str(c_act) + " " + r + " " + ci
        blue_points = {
            "x": list(sample_non[ci].values),
            "y": list(sample_non[r].values),
        }
        black_points = {
            "x": list(sample[ci].values),
            "y": list(sample[r].values),
        }
        star = {
            "x": model_dataset.loc[i, ci],
            "y": model_dataset.loc[i, r],
        }
        return key, blue_points, black_points, star
