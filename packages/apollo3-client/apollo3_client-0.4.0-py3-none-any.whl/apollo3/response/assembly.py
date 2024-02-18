from typing import Dict


class Assembly:
    def __init__(self, id: str, name: str):
        self._id = id
        self._name = name

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @staticmethod
    def parse(assembly: Dict):
        if assembly["status"] == 0:
            return Assembly(assembly["_id"], assembly["name"])
        return None

    def __str__(self):
        return f"({self.id}, {self.name})"
