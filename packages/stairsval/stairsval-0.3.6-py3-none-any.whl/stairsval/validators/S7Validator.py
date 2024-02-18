import pandas as pd
from rich.console import Console
from stairs_mro.networks.DefectRes import DefectRes
from stairs_mro.networks.WorkResNet import WorkResNet

from stairsval.core.aggregator import Aggregator
from stairsval.core.dataset_processors.S7KSG import S7KSG
from stairsval.core.expert_metrics_estimator import ExpertMetricsEstimator
from stairsval.validation_checks.ResourcesChecker import ResourcesChecker
from stairsval.validation_checks.TimeChecker import TimeChecker
from stairsval.validators.BaseValidator import BaseValidator


class S7PlanValidator:
    def __init__(
        self,
        plan,
        val_df_res_work: pd.DataFrame,
        val_df_res_defect: pd.DataFrame,
        journal: dict,
        work_res_model: dict,
        defect_model: dict,
    ):
        self.console = Console()
        self.ksg_data = S7KSG(ksg_data=plan).collect()
        self.aggregator = Aggregator()
        self.resources_validator = None
        self.work_res_model = work_res_model
        self.defect_model = defect_model
        self.val_df_res_work = val_df_res_work
        self.val_df_res_defect = val_df_res_defect
        self.journal = journal

    def validate(self):
        pass

    def common_validate(self):
        (
            df_validation_table_res,
            fig_dict_res,
            norm_perc_res_val,
            not_perc_res_val,
        ) = ResourcesChecker(res=[], journal=self.journal).common_validation(
            self.ksg_data,
            (self.val_df_res_work, self.val_df_res_defect),
            plan_type="s7",
        )

        model_work = WorkResNet(structure=[])
        model_work.load(self.work_res_model)

        model_defect = DefectRes(structure=[])
        model_defect.load(self.defect_model)

        proximity_model = (model_work, model_defect)
        df_vedom, not_perc_vedom, norm_perc_vedom = self.aggregator.get_res_ved_stat(
            proximity_model, self.ksg_data, plan_type="s7"
        )
        (
            df_validation_table_time,
            fig_dict_time,
            norm_perc_time,
            not_perc_time,
        ) = TimeChecker(journal=self.journal).common_validation(
            self.ksg_data, (self.val_df_res_work, self.val_df_res_defect), "s7"
        )
        return (
            df_validation_table_res,
            fig_dict_res,
            norm_perc_res_val,
            not_perc_res_val,
            df_vedom,
            not_perc_vedom,
            norm_perc_vedom,
            df_validation_table_time,
            fig_dict_time,
            norm_perc_time,
            not_perc_time,
        )


class S7Validator(BaseValidator):
    """Validator for S7 plans."""

    def __init__(
        self,
        project_ksg,
        work_res_model: dict,
        defect_model: dict,
        history_adapter=None,
    ):
        super().__init__(project_ksg, history_adapter)
        self.plan_type = "s7"
        self.work_res_model = work_res_model
        self.defect_model = defect_model

    def specific_validation(self):
        return self.common_validation()

    def common_validation(self, cut_to_n_works: int = None):
        if cut_to_n_works:
            self._trim_plan_to_n_works(cut_to_n_works)
        (
            df_validation_table_res,
            fig_dict_res,
            norm_perc_res_val,
            not_perc_res_val,
            df_vedom,
            not_perc_vedom,
            norm_perc_vedom,
            df_validation_table_time,
            fig_dict_time,
            norm_perc_time,
            not_perc_time,
        ) = S7PlanValidator(
            plan=self.project_ksg,
            work_res_model=self.work_res_model,
            defect_model=self.defect_model,
            val_df_res_work=self.history_adapter.get_work_res_data_no_nan_new2(),
            val_df_res_defect=self.history_adapter.get_work_defect_res_data_no_nan_new2(),
            journal=self.history_adapter.get_journal_mapped(),
        ).common_validate()

        work_res_stat = dict()
        work_res_stat["Percentage of Normal Resource Volume Values"] = round(
            norm_perc_res_val
        )
        work_res_stat["Percentage of Atypical Resource Volume Values"] = 100 - round(
            norm_perc_res_val
        )
        work_res_stat["Percentage of Normal Resources According to Statements"] = round(
            norm_perc_vedom
        )
        work_res_stat["Percentage of Atypical Resources According to Statements"] = (
            100 - round(norm_perc_vedom)
        )
        work_res_stat["Percentage of Normal Values Across All Resources"] = round(
            (
                work_res_stat["Percentage of Normal Resource Volume Values"]
                + work_res_stat[
                    "Percentage of Normal Resources According to Statements"
                ]
            )
            / 2
        )
        work_res_stat["Percentage of Atypical Values Across All Resources"] = (
            100 - work_res_stat["Percentage of Normal Values Across All Resources"]
        )
        work_res_stat["Percentage of Normal Work Time Values"] = round(norm_perc_time)
        work_res_stat["Percentage of Atypical Work Time Values"] = 100 - round(
            norm_perc_time
        )
        work_res_stat["Percentage of Normal Values Across All Works"] = round(
            norm_perc_time
        )
        work_res_stat["Percentage of Atypical Values Across All Works"] = 100 - round(
            norm_perc_time
        )
        work_res_stat["Percentage of Normal Plan Values"] = round(
            (
                work_res_stat["Percentage of Normal Values Across All Resources"]
                + work_res_stat["Percentage of Normal Values Across All Works"]
            )
            / 2
        )
        work_res_stat["Percentage of Atypical Plan Values"] = (
            100 - work_res_stat["Percentage of Normal Plan Values"]
        )
        work_res_stat["Percentage of Plan Values Not Covered by Validation"] = round(
            (not_perc_res_val + not_perc_vedom + not_perc_time) / 3
        )
        work_res_stat["Percentage of Plan Values Covered by Validation"] = 100 - round(
            (not_perc_res_val + not_perc_vedom + not_perc_time) / 3
        )

        result_dict = dict()
        result_dict["Common validation"] = {
            "Resources Validation Table": df_validation_table_res,
            "Data for Resource Charts": fig_dict_res,
            "Resource Journal": df_vedom,
            "Work Time Validation Table": df_validation_table_time,
            "Data for Time Charts": fig_dict_time,
            "Final Plan Statistics": work_res_stat,
        }
        return result_dict

    def calculate_expert_metrics(self):
        metrics_calculator = ExpertMetricsEstimator(self.project_ksg)
        metrics = metrics_calculator.calculate_metrics()
        formal_metrics = metrics_calculator.calculate_formal_metrics()
        return metrics, formal_metrics
