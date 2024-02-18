import warnings
from abc import ABC, abstractmethod

import pandas as pd

warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=RuntimeWarning)


class AbstractChecker(ABC):
    def __init__(
        self,
        percent_delta: float = 0.5,
        lower_quantile: float = 0.01,
        upper_quantile: float = 0.99,
    ):
        self.percent_delta = percent_delta
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile

    @abstractmethod
    def validate(
        self, model_dataset: pd.DataFrame, df_wind_val: pd.DataFrame, act: list
    ):
        pass
