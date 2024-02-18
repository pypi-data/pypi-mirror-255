import json
from abc import ABC, abstractmethod

import pandas as pd
import pkg_resources
from pandas import DataFrame


class MschmAdapter(ABC):
    @abstractmethod
    def get_s7_model(self, model_name: str) -> dict:
        pass


class LocalMschmAdapter(MschmAdapter):
    def get_s7_model(self, name: str) -> dict:
        model_path_full = str()
        match name:
            case "defect_res":
                model_path = "../../../tests/test_data/local_models/defect_res_bn_new2.json"
                model_path_full = pkg_resources.resource_filename(
                    __name__, model_path
                )
            case "work_res_net":
                model_path = "../../../tests/test_data/local_models/work_res_bn_no_nan_new2.json"
                model_path_full = pkg_resources.resource_filename(
                    __name__, model_path
                )
        file = open(model_path_full, encoding="utf8")
        model_dict = json.load(file)
        return model_dict
