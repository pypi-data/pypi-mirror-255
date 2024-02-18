from abc import ABC, abstractmethod


class BaseDataset(ABC):
    @abstractmethod
    def collect(self):
        pass
