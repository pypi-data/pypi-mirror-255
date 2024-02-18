from stairsval.core.dataset_processors.BaseDataset import BaseDataset
from stairsval.core.dataset_processors.ObjectNameProcessor import ObjectNameProcessor


class KSGDataset(BaseDataset):
    def __init__(self, ksg_data, connector, level):
        self.ksg_data = ksg_data
        self.connector = connector
        self.level = level

    def collect(self):
        dict_class = ObjectNameProcessor(connector=self.connector, level=self.level)
        act = []
        for w in self.ksg_data["schedule"]["works"]:
            act.append(w["display_name"])
        res = []
        for w in self.ksg_data["schedule"]["works"]:
            for r in w["workers"]:
                if r["name"] not in res:
                    res.append(r["name"])
        act_dict = dict_class.create_granulary_dict(act, "act")
        res_dict = dict_class.create_granulary_dict(res, "res")
        plan_dict = {}
        for act in self.ksg_data["schedule"]["works"]:
            name = act["display_name"]
            smr_name = act["display_name"]
            if name in act_dict:
                smr_name = act_dict[name][0]
            if smr_name in plan_dict:
                plan_dict[smr_name].append(name)
            else:
                plan_dict[smr_name] = [name]
        delete_act = []
        for el in plan_dict:
            if len(plan_dict[el]) > 1:
                for c in plan_dict[el][1:]:
                    delete_act.append(c)
        new_act = []
        new_wg = []
        deleted_id = []
        for i, w in enumerate(self.ksg_data["schedule"]["works"]):
            if (float(w["volume"]) != 0.0) and (w["display_name"] not in delete_act):
                new_act.append(w)
                work_id = w["id"]
                for node in self.ksg_data["wg"]["nodes"]:
                    if node["work_unit"]["id"] == work_id:
                        new_wg.append(node)
                        break

            else:
                deleted_id.append(w["id"])
        self.ksg_data["schedule"]["works"] = new_act
        self.ksg_data["wg"]["nodes"] = new_wg
        for w in self.ksg_data["wg"]["nodes"]:
            new_des = []
            for el in w["parent_edges"]:
                if el[0] not in deleted_id:
                    new_des.append(el)
            w["parent_edges"] = new_des
        for w in self.ksg_data["schedule"]["works"]:
            if w["display_name"] in act_dict:
                w["display_name"] = act_dict[w["display_name"]][0]
            for r in w["workers"]:
                if r["name"] in res_dict:
                    r["name"] = res_dict[r["name"]][0]
        return self.ksg_data
