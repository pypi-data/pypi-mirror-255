class StatisticCalculator:
    def __init__(
        self,
        norm_res,
        norm_ved,
        norm_volume,
        norm_time,
        norm_seq,
        not_res,
        not_ved,
        not_volume,
        not_time,
        not_seq,
    ):
        self.norm_res = norm_res
        self.norm_ved = norm_ved
        self.norm_volume = norm_volume
        self.norm_time = norm_time
        self.norm_seq = norm_seq
        self.not_res = not_res
        self.not_ved = not_ved
        self.not_volume = not_volume
        self.not_time = not_time
        self.not_seq = not_seq

    def get_statistic_for_properties_and_all_stat(self):
        result_dict = dict()
        result_dict["Percentage of Normal Resource Volume Values"] = round(
            self.norm_res
        )
        if self.not_res != 100:
            result_dict["Percentage of Atypical Resource Volume Values"] = 100 - round(
                self.norm_res
            )
        else:
            result_dict["Percentage of Atypical Resource Volume Values"] = 0

        result_dict["Percentage of Normal Resources According to Journal"] = round(
            self.norm_ved
        )
        if self.not_ved != 100:
            result_dict["Percentage of Atypical Resources According to Journal"] = (
                100 - round(self.norm_ved)
            )
        else:
            result_dict["Percentage of Atypical Resources According to Journal"] = 100

        result_dict["Percentage of Normal Work Time Values"] = round(self.norm_time)
        if self.not_time != 100:
            result_dict["Percentage of Atypical Work Time Values"] = 100 - round(
                self.norm_time
            )
        else:
            result_dict["Percentage of Atypical Work Time Values"] = 0

        result_dict["Percentage of Normal Work Volume Values"] = round(self.norm_volume)
        if self.not_volume != 100:
            result_dict["Percentage of Atypical Work Volume Values"] = 100 - round(
                self.norm_volume
            )
        else:
            result_dict["Percentage of Atypical Work Volume Values"] = 0

        result_dict["Percentage of Normal Work Connection Values"] = round(
            self.norm_seq
        )
        if self.not_seq != 100:
            result_dict["Percentage of Atypical Work Connection Values"] = 100 - round(
                self.norm_seq
            )
        else:
            result_dict["Percentage of Atypical Work Connection Values"] = 0

        result_dict["Percentage of Normal Values Across All Works"] = round(
            (self.norm_time + self.norm_volume + self.norm_seq) / 3
        )
        result_dict["Percentage of Critical Values Across All Works"] = 100 - round(
            (self.norm_time + self.norm_volume + self.norm_seq) / 3
        )

        result_dict["Percentage of Normal Values Across All Resources"] = round(
            (self.norm_res + self.norm_ved) / 2
        )
        result_dict["Percentage of Critical Values Across All Resources"] = 100 - round(
            (self.norm_res + self.norm_ved) / 2
        )

        return result_dict

    def get_plan_statistic(self):
        norm_value = round(
            (
                self.norm_res
                + self.norm_ved
                + self.norm_volume
                + self.norm_time
                + self.norm_seq
            )
            / 5
        )
        crit_value = 100 - norm_value
        not_val = round(
            (
                self.not_res
                + self.not_ved
                + self.not_volume
                + self.not_time
                + self.not_seq
            )
            / 5
        )
        tested_val = 100 - not_val
        dict_result = {
            "Percentage of Normal Plan Values": norm_value,
            "Percentage of Atypical Plan Values": crit_value,
            "Percentage of Plan Values Not Covered by Validation": not_val,
            "Percentage of Plan Values Covered by Validation": tested_val,
        }

        return dict_result
