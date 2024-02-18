from typing import Dict, List


class Change:
    def __init__(self, assembly_id: str, change_type: str, feature_id: str, user: str):
        self._assembly_id = assembly_id
        self._change_type = change_type
        self._feature_id = feature_id
        self._user = user

    @property
    def assembly_id(self):
        return self._assembly_id

    @assembly_id.setter
    def assembly_id(self, assembly_id):
        self._assembly_id = assembly_id

    @property
    def change_type(self):
        return self._change_type

    @change_type.setter
    def change_type(self, change_type):
        self._change_type = change_type

    @property
    def feature_id(self):
        return self._feature_id

    @feature_id.setter
    def feature_id(self, feature_id):
        self._feature_id = feature_id

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, user):
        self._user = user

    def __eq__(self, other):
        return isinstance(other, Change) and self.feature_id == other.feature_id

    def __hash__(self):
        return hash(self.feature_id)

    @staticmethod
    def parse(change: Dict) -> List["Change"]:
        # TODO: DeleteFeatureChange
        changes = []
        for c in change.get("changes", []):
            if c["typeName"] == "AddFeatureChange":
                feature_id = c["addedFeature"]["_id"]
            elif c["typeName"] in [
                "DiscontinuousLocationEndChange",
                "DiscontinuousLocationStartChange",
                "FeatureAttributeChange",
                "LocationEndChange",
                "LocationStartChange",
            ]:
                feature_id = c["featureId"]
            else:
                feature_id = None
            if feature_id is not None:
                changes.append(
                    Change(c["assembly"], c["typeName"], feature_id, change["user"])
                )
        return changes

    def __str__(self):
        return (
            f"({self.assembly_id}, {self.change_type}, {self.feature_id}, {self.user})"
        )
