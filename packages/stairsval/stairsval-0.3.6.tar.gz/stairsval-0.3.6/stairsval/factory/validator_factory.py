from enum import Enum, auto

from stairsval.validators.GPNValidator import GPNValidator
from stairsval.validators.S7Validator import S7Validator


class PlanType(Enum):
    GPN = auto()
    S7 = auto()


class ValidatorFactory:
    @staticmethod
    def create_validator(plan_type, *args, **kwargs):
        if not isinstance(plan_type, PlanType):
            raise ValueError("Invalid plan type provided!")

        if plan_type == PlanType.GPN:
            return GPNValidator(*args, **kwargs)
        elif plan_type == PlanType.S7:
            return S7Validator(*args, **kwargs)
        else:
            raise ValueError(f"No validator defined for plan type {plan_type}")
