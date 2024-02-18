from datetime import datetime


class ExpertMetricsEstimator:
    def __init__(self, project_data):
        self.project = project_data

    def _get_all_descendant_acts(self, index=2):
        return [
            edge[index]
            for node in self.project["wg"]["nodes"]
            for edge in node["parent_edges"]
        ]

    def _calculate_percentage(self, condition, index=1):
        all_descendant_acts = self._get_all_descendant_acts(index)
        matching_count = sum(1 for desc in all_descendant_acts if condition(desc))
        return matching_count / len(all_descendant_acts) if all_descendant_acts else 0

    def follower_preds(self):
        descendant_percentage = self._calculate_percentage(
            lambda x: x not in self._get_all_descendant_acts(0), 0
        )
        return True if descendant_percentage <= 0.05 else False

    def outrun(self):
        fss_percentage = self._calculate_percentage(lambda x: x == "FFS")
        return True if fss_percentage <= 0.05 else False

    def finish_start(self):
        fs_ffs_percentage = self._calculate_percentage(lambda x: x in ["FS", "FFS"])
        return True if fs_ffs_percentage >= 0.85 else False

    def others(self):
        other_percentage = self._calculate_percentage(lambda x: x not in ["FS", "FFS"])
        return True if other_percentage <= 0.15 else False

    def crit_index(self):
        if "plan_deadline" not in self.project:
            return None

        acts_start_date = datetime.strptime(
            self.project["works"][0]["start_end_time"][0].split()[0], "%Y-%m-%d"
        )
        acts_deadline_date = datetime.strptime(
            self.project["plan_deadline"].split()[0], "%Y-%m-%d"
        )
        acts_end_date = datetime.strptime(
            self.project["works"][-1]["start_end_time"][-1].split()[0], "%Y-%m-%d"
        )
        ldeadline = (acts_deadline_date - acts_start_date).days
        lcp = (acts_end_date - acts_start_date).days
        index = ldeadline / lcp
        return True if index >= 1 else False

    def calculate_metrics(self):
        return {
            "follower_preds": self.follower_preds(),
            "outrun": self.outrun(),
            "finish_start": self.finish_start(),
            "others": self.others(),
            "crit_index": self.crit_index(),
        }

    def calculate_formal_metrics(self):
        # Filter out work names "start of projects" and "start" in schedule
        relevant_works = [
            work
            for work in self.project["schedule"]["works"]
            if work.get("name") not in ["start of projects", "start"]
        ]

        # Filter out work names "start of projects" and "start" in work units
        relevant_nodes = [
            node
            for node in self.project["wg"]["nodes"]
            if node.get("work_unit", {}).get("name")
            not in ["start of projects", "start"]
        ]

        # Check if all relevant works have non-empty 'workers' fields
        all_have_workers = all(
            "workers" in work and work["workers"] for work in relevant_works
        )

        # Check if all relevant work units have non-empty 'volume' fields
        all_have_volume = all(
            "work_unit" in node
            and "volume" in node["work_unit"]
            and node["work_unit"]["volume"]
            for node in relevant_nodes
        )

        # Check if at least one relevant work unit has a non-empty 'parent_edges' field
        at_least_one_has_parents = any(
            "parent_edges" in node and node["parent_edges"] for node in relevant_nodes
        )

        return {
            "all_have_workers": all_have_workers,
            "all_have_volume": all_have_volume,
            "at_least_one_has_parents": at_least_one_has_parents,
        }
