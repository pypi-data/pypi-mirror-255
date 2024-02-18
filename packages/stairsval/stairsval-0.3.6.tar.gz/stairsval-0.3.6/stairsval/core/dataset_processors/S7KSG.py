from stairsval.core.dataset_processors.BaseDataset import BaseDataset


class S7KSG(BaseDataset):
    def __init__(self, ksg_data):
        self.ksg_data = ksg_data

    def collect(self):
        new_act = []
        new_wg = []
        deleted_id = []
        for i, w in enumerate(self.ksg_data["schedule"]["works"]):
            if float(w["volume"]) != 0.0:
                new_act.append(w)
                new_wg.append(self.ksg_data["wg"]["nodes"][i])
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
        return self.ksg_data
