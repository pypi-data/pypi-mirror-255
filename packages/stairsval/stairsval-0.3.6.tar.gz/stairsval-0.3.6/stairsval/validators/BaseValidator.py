from abc import ABC, abstractmethod
from copy import deepcopy


class BaseValidator(ABC):
    """Abstract Base Validator class."""

    def __init__(self, project_ksg, history_adapter=None):
        self.project_ksg = deepcopy(project_ksg)
        self.history_adapter = history_adapter

        self._preprocess_project()

    @abstractmethod
    def common_validation(self, *args, **kwargs):
        """Common validation logic for all plans."""
        pass

    @abstractmethod
    def specific_validation(self):
        """Method to be overridden for plan-specific validation."""
        pass

    def _remove_extra_works(self, names_to_remove):
        removed_ids = {
            work["id"]
            for work in self.project_ksg["schedule"]["works"]
            if work.get("display_name") in names_to_remove
        }

        self.project_ksg["schedule"]["works"] = [
            work
            for work in self.project_ksg["schedule"]["works"]
            if work.get("display_name") not in names_to_remove
        ]

        self.project_ksg["wg"]["nodes"] = [
            node
            for node in self.project_ksg["wg"]["nodes"]
            if node.get("work_unit", {}).get("display_name") not in names_to_remove
        ]

        for node in self.project_ksg["wg"]["nodes"]:
            if "parent_edges" in node:
                node["parent_edges"] = [
                    edge for edge in node["parent_edges"] if edge[0] not in removed_ids
                ]

    def _preprocess_project(self):
        names_to_remove = {"start of project", "start", "finish of project"}
        self._remove_extra_works(names_to_remove)

    def _trim_plan_to_n_works(self, n):
        if n >= len(self.project_ksg["schedule"]["works"]):
            return self.project_ksg

        plan_copy = deepcopy(self.project_ksg)
        keep_ids = set(work["id"] for work in plan_copy["schedule"]["works"][:n])

        plan_copy["schedule"]["works"] = plan_copy["schedule"]["works"][:n]

        plan_copy["wg"]["nodes"] = [
            node
            for node in plan_copy["wg"]["nodes"]
            if node["work_unit"]["id"] in keep_ids
        ]

        for node in plan_copy["wg"]["nodes"]:
            if "parent_edges" in node:
                node["parent_edges"] = [
                    edge for edge in node["parent_edges"] if edge[0] in keep_ids
                ]

        return plan_copy
