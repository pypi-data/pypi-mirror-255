import json
from abc import ABC, abstractmethod

import pandas as pd
import pkg_resources
from pandas import DataFrame


class FieldDevHistoryAdapter(ABC):
    @abstractmethod
    def get_journal_mapped(self) -> dict:
        pass

    @abstractmethod
    def get_links_history_messoyakha_with_new_granular_v2(self) -> DataFrame:
        pass

    @abstractmethod
    def get_precalculated_brave_coefficients(self) -> DataFrame:
        pass

    @abstractmethod
    def get_work_defect_res_data_no_nan_new2(self) -> DataFrame:
        pass

    @abstractmethod
    def get_work_res_data_no_nan_new2(self) -> DataFrame:
        pass


class LocalFieldDevHistoryAdapter(FieldDevHistoryAdapter):
    def __init__(self):
        self.journal_mapped = "../../../tables/journal_mapped.json"
        self.journal_mapped_path = pkg_resources.resource_filename(
            __name__, self.journal_mapped
        )
        self.links_history_messoyakha_with_new_granular_v2 = (
            "../../../tables/links_history_messoyakha_with_new_granular_v2.csv"
        )
        self.links_history_messoyakha_with_new_granular_v2_path = (
            pkg_resources.resource_filename(
                __name__, self.links_history_messoyakha_with_new_granular_v2
            )
        )
        self.precalculated_brave_coefficients = (
            "../../../tables/precalculated_brave_coefficients.csv"
        )
        self.precalculated_brave_coefficients_path = pkg_resources.resource_filename(
            __name__, self.precalculated_brave_coefficients
        )
        self.work_defect_res_data_no_nan_new2 = (
            "../../../tables/work_defect_res_data_no_nan_new2.csv"
        )
        self.work_defect_res_data_no_nan_new2_path = pkg_resources.resource_filename(
            __name__, self.work_defect_res_data_no_nan_new2
        )
        self.work_res_data_no_nan_new2 = "../../../tables/work_res_data_no_nan_new2.csv"
        self.work_res_data_no_nan_new2_path = pkg_resources.resource_filename(
            __name__, self.work_res_data_no_nan_new2
        )

    def get_journal_mapped(self) -> dict:
        file = open(self.journal_mapped_path, encoding="utf8")
        journal_data = json.load(file)
        return journal_data

    def get_links_history_messoyakha_with_new_granular_v2(self) -> DataFrame:
        return pd.read_csv(
            self.links_history_messoyakha_with_new_granular_v2_path, sep=";"
        )

    def get_precalculated_brave_coefficients(self) -> DataFrame:
        return pd.read_csv(self.precalculated_brave_coefficients_path, index_col=0)

    def get_work_defect_res_data_no_nan_new2(self) -> DataFrame:
        return pd.read_csv(self.work_defect_res_data_no_nan_new2_path)

    def get_work_res_data_no_nan_new2(self) -> DataFrame:
        return pd.read_csv(self.work_res_data_no_nan_new2_path)
