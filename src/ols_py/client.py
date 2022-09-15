from typing import Optional

import furl
import marshmallow
import requests


class OlsClient:
    def __init__(self, base_url: str):
        self.base_url = furl.furl(base_url)
        self._session = requests.Session()
        self._session.headers = {"accept": "application/json"}
        # TODO: do we need to set access-control-allow-origin header?

    def get(self, path: str, params: Optional[dict] = None):
        url = self.base_url / path
        resp = self._session.get(url=url.url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_with_schema(
        self, schema: marshmallow.Schema, path: str, params: Optional[dict] = None
    ):
        resp = self.get(path=path, params=params)
        errors = schema.validate(resp)
        if errors:
            raise ValueError(f"Schema failed to parse: {errors}")
        return resp
