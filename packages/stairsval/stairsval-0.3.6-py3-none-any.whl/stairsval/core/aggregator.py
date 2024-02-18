import numpy as np
import pandas as pd


class Aggregator:
    def __init__(self, brave_crit_value: float = 0.45):
        self.CRIT_VALUE = brave_crit_value

    @staticmethod
    def get_all_seq_statistic(start_end_data, model_data):
        works_dict = {
            act["id"]: act["display_name"] for act in model_data["schedule"]["works"]
        }
        pairs_labels = {
            (act["display_name"], works_dict[el[0]]): el[2]
            for i, act in enumerate(model_data["schedule"]["works"])
            if model_data["wg"]["nodes"][i]["parent_edges"]
            for el in model_data["wg"]["nodes"][i]["parent_edges"]
        }

        pairs = list(pairs_labels.keys())
        if not pairs:
            return pd.DataFrame(), pd.DataFrame(), 0, 0

        freq_dict = {}

        def check_dates(row):
            s1 = row["first_day_x"]
            f1 = row["last_day_x"]
            s2 = row["first_day_y"]
            f2 = row["last_day_y"]

            fs = int(f1 < s2)
            ss = int(s1 == s2)
            ff = int(f1 == f2)
            mix = int(s2 < f1)
            total = fs + ss + ff + mix

            return pd.Series(
                [fs, ss, ff, mix, total], index=["FS", "SS", "FF", "FFS", "count"]
            )

        for w1, w2 in pairs:
            ind1 = start_end_data.loc[(start_end_data["granular_name"] == w1)]
            ind2 = start_end_data.loc[(start_end_data["granular_name"] == w2)]
            merged_data = pd.merge(
                ind1, ind2, how="inner", on="upper_works", suffixes=("_x", "_y")
            )
            counts = pd.Series(
                [0, 0, 0, 0, 0], index=["FS", "SS", "FF", "FFS", "count"]
            )
            if merged_data.shape[0] != 0:
                counts = merged_data.apply(check_dates, axis=1)

            total_fs = counts["FS"].sum()
            total_ss = counts["SS"].sum()
            total_ff = counts["FF"].sum()
            total_ffs = counts["FFS"].sum()
            total_count = counts["count"].sum()

            if total_count > 0:
                freq_dict[w1, w2] = {
                    "count": total_count,
                    "FS": total_fs,
                    "SS": total_ss,
                    "FF": total_ff,
                    "FFS": total_ffs,
                }

        bar_records = []
        color_records = []
        links = ["FFS", "FS", "SS", "FF"]

        for i, ((w1, w2), label) in enumerate(pairs_labels.items()):
            pair_data = freq_dict.get((w1, w2), {})
            total_count = pair_data.get("count", 0)
            if total_count == 0:
                color_record = {
                    "Work name 1": w1,
                    "Work name 2": w2,
                    "color": "grey",
                }
                color_records.append(color_record)
                continue

            mix_val = pair_data.get("FFS", 0) / total_count
            fs_val = pair_data.get("FS", 0) / total_count
            ss_val = pair_data.get("SS", 0) / total_count
            ff_val = pair_data.get("FF", 0) / total_count
            links_perc = [mix_val, fs_val, ss_val, ff_val]
            max_label = links[np.argmax(links_perc)]

            bar_record = {
                "Work name 1": w1,
                "Work name 2": w2,
                "Plan connection": label,
                "FFS": mix_val * 100,
                "FS": fs_val * 100,
                "SS": ss_val * 100,
                "FF": ff_val * 100,
            }
            bar_records.append(bar_record)

            color_record = {
                "Work name 1": w1,
                "Work name 2": w2,
                "color": "green" if max_label == label else "red",
            }
            color_records.append(color_record)

        df_bar = pd.DataFrame.from_records(bar_records)
        df_color = pd.DataFrame.from_records(color_records)
        if df_color.empty:
            norm_perc = 0
            not_perc = 100
        else:
            perc_dict = df_color["color"].value_counts().to_dict()
            norm_perc = (perc_dict.get("green", 0) / df_color.shape[0]) * 100
            not_perc = (perc_dict.get("grey", 0) / df_color.shape[0]) * 100

        return df_bar, df_color, norm_perc, not_perc

    def get_res_ved_stat(self, proximity_model, ksg_for_val_data, plan_type):
        df_stat = pd.DataFrame(columns=["Work", "Resource", "Resource label"])

        def evaluate_resource(row):
            df_row = pd.DataFrame(columns=["Work", "Resource", "Resource label"])
            if plan_type == "gpn":
                res = row["workers"]
                act_name = row["display_name"]
                for i, r in enumerate(res):
                    df_row.loc[i, "Work"] = act_name
                    df_row.loc[i, "Resource"] = r["name"]
                    df_row.loc[i, "Resource label"] = None
                    if (
                        f"{act_name}_act_fact" in proximity_model.columns
                        and f"{r['name']}_res_fact" in proximity_model.index
                    ):
                        df_row.loc[i, "Resource label"] = (
                            "green"
                            if proximity_model.loc[
                                r["name"] + "_res_fact",
                                act_name + "_act_fact",
                            ]
                            >= self.CRIT_VALUE
                            else "red"
                        )
            elif plan_type == "s7":
                res = row["workers"]
                act_name = row["name"]
                if ":" in act_name:
                    name = act_name.replace(":", "_")
                    model = proximity_model[1].get_defect_res_probability(
                        evidence={"new_class_child": name}
                    )
                else:
                    model = proximity_model[0].get_res_probability(
                        evidence={"event_name_parent": act_name}
                    )
                for i, r in enumerate(res):
                    df_row.loc[i, "Work"] = act_name
                    df_row.loc[i, "Resource"] = r["name"]
                    df_row.loc[i, "Resource label"] = None
                    if len(model) != 0:
                        df_row.loc[i, "Resource label"] = (
                            "green" if model[r["name"]] >= self.CRIT_VALUE else "red"
                        )
            return df_row

        for work in ksg_for_val_data["schedule"]["works"]:
            df_result = evaluate_resource(work)
            df_stat = pd.concat([df_stat, df_result], ignore_index=True)

        not_grey = df_stat[df_stat["Resource label"].notnull()]
        df_stat_len = len(df_stat)
        if df_stat_len != 0:
            not_perc = (len(df_stat) - len(not_grey)) / df_stat_len * 100
        else:
            not_perc = 0
        if not_perc == 100:
            return df_stat, not_perc, 0
        if len(not_grey) != 0:
            norm_perc = (
                not_grey["Resource label"].value_counts().to_dict().get("green", 0)
                / len(not_grey)
            ) * 100
        else:
            norm_perc = 0

        return df_stat, not_perc, norm_perc
