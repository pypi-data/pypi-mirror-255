from typing import List, Set, Union

import requests

from apollo3.response import Assembly, Change

APOLLO3_API_URL = "http://localhost:3999"


class Apollo3Client:
    def __init__(
        self,
        api_url: Union[str, None] = None,
        username: Union[str, None] = None,
        password: Union[str, None] = None,
    ):
        self._api_url = api_url or APOLLO3_API_URL
        self._username = username
        self._password = password
        self._token = self._get_token()

    def _get_token(self) -> str:
        if self._username is None and self._password is None:
            try:
                response = requests.get(
                    f"{self._api_url}/auth/login", params={"type": "guest"}
                )
                response.raise_for_status()
                return response.json()["token"]
            except requests.exceptions.RequestException as e:
                raise ValueError(f"Login API call failed: {e}") from e
        else:
            raise ValueError("Root authentication is not yet supported.")

    def assemblies_obj(self) -> List[Assembly]:
        try:
            return [
                Assembly.parse(assembly)
                for assembly in self.assemblies()
                if Assembly.parse(assembly) is not None
            ]
        except Exception as e:
            raise ValueError(f"An unexpected error occurred: {e}")

    def assemblies(self):
        response = requests.get(f"{self._api_url}/assemblies", headers=self._header())
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(
                f"GET assemblies API call failed. Status code: {response.status_code}"
            )

    def changes_obj(self, assembly_id: Union[str, None] = None) -> Set[Change]:
        # TODO: DeleteFeatureChange
        try:
            return {
                item
                for c in self.changes(assembly_id)
                for item in Change.parse(c)
                if item is not None
            }
        except Exception as e:
            raise ValueError(f"An unexpected error occurred: {e}")

    def changes(self, assembly_id: Union[str, None] = None):
        params = {}
        if assembly_id is not None:
            params["assembly"] = assembly_id

        response = requests.get(
            f"{self._api_url}/changes", headers=self._header(), params=params
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(
                f"GET changes API call failed. Status code: {response.status_code}"
            )

    def feature(self, feature_id: str):
        response = requests.get(
            f"{self._api_url}/features/{feature_id}", headers=self._header()
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(
                f"GET features API call failed. Status code: {response.status_code}"
            )

    def _header(self):
        return {"Authorization": f"Bearer {self._token}"}
