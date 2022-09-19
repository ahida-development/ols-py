from typing import Optional, Type, TypeVar

import furl
import pydantic
import requests

S = TypeVar("S", bound=pydantic.BaseModel, covariant=True)


class OlsClient:
    """
    Client for communicating with an OLS instance.
    """

    def __init__(self, base_url: str):
        """
        :param base_url: Base API URL for the OLS instance
        """
        self.base_url = furl.furl(base_url)
        self._session = requests.Session()
        self._session.headers = {"accept": "application/json"}
        # TODO: do we need to set access-control-allow-origin header?

    def get(self, path: str, params: Optional[dict] = None) -> dict:
        """
        Perform a GET request to the API.

        :param path: API path (excluding base url)
        :param params: Query parameters
        :return: JSON data, as a dict
        """
        url = self.base_url / path
        resp = self._session.get(url=url.url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_with_schema(
        self, schema: Type[S], path: str, params: Optional[dict] = None
    ) -> S:
        """
        Get data from ``path`` and parse it with ``schema`` to return
        a pydantic object.

        :param schema: Pydantic class/model inheriting from BaseModel
        :param path: API path (excluding the base API url)
        :param params: Query parameters
        :return: Pydantic model instance created from ``schema``
        :raises: ``pydantic.ValidationError`` if response data fails
           to validate.
        """
        resp = self.get(path=path, params=params)
        obj = schema(**resp)
        return obj
