from __future__ import annotations

from typing import Optional, Type, TypeVar
from urllib.parse import quote_plus

import pydantic
import requests

from . import schemas

S = TypeVar("S", bound=pydantic.BaseModel, covariant=True)


class OlsClient:
    """
    Client for communicating with an OLS instance.
    """

    base_url: str

    def __init__(self, base_url: str):
        """
        :param base_url: Base API URL for the OLS instance
        """
        if not base_url.endswith("/"):
            base_url = base_url + "/"
        self.base_url = base_url
        self._session = requests.Session()
        self._session.headers.update({"accept": "application/json"})
        # TODO: do we need to set access-control-allow-origin header?

    def _create_url(self, path: str) -> str:
        # Remove leading /
        path = path.lstrip("/")
        return self.base_url + path

    @staticmethod
    def _quote_iri(iri: str) -> str:
        """
        Quote an IRI as a double URL-encoded URL string, so it can
        be used in a URL path
        :param iri: IRI, e.g. http://purl.obolibrary.org/obo/GO_0043226
        :return: Percent-encoded string, e.g. http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FGO_0043226
        """
        return quote_plus(quote_plus(iri))

    def get(self, path: str, params: Optional[dict] = None) -> dict:
        """
        Perform a GET request to the API.

        :param path: API path (excluding base url)
        :param params: Query parametersgg
        :return: JSON data, as a dict
        """
        url = self._create_url(path)
        resp = self._session.get(url=url, params=params)
        resp.raise_for_status()
        json_data: dict = resp.json()
        return json_data

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
        :raises pydantic.ValidationError: if response data fails
           to validate.
        """
        resp = self.get(path=path, params=params)
        obj = schema(**resp)
        return obj

    def get_ontologies(self) -> schemas.OntologyList:
        ontology_list = self.get_with_schema(schemas.OntologyList, "/ontologies")
        return ontology_list

    def get_ontology(self, ontology_id: str) -> schemas.OntologyItem:
        path = f"/ontologies/{ontology_id}/"
        ontology_item = self.get_with_schema(schemas.OntologyItem, path)
        return ontology_item

    def get_term(self, ontology_id: str, iri: str) -> schemas.Term:
        iri = self._quote_iri(iri)
        path = f"/ontologies/{ontology_id}/terms/{iri}"
        term = self.get_with_schema(schemas.Term, path)
        return term

    def _get_term_relatives(
        self, relatives: schemas.RelativeTypes, ontology_id: str, term_id: str
    ) -> schemas.TermRelatives:
        """
        Common method for getting a term's parents, children, ancestors etc.
        """
        path = f"/ontologies/{ontology_id}/{relatives}"
        return self.get_with_schema(schemas.TermRelatives, path, params={"id": term_id})

    def get_term_parents(self, ontology_id: str, term_id: str) -> schemas.TermRelatives:
        """
        Get parents for a term.
        :param ontology_id: Name of ontology, e.g. "go"
        :param term_id: Term ID (URI, short form or obo ID)
        :return: response object. the actual terms are in a list at
          ``response.embedded.terms``
        """
        return self._get_term_relatives(
            "parents", ontology_id=ontology_id, term_id=term_id
        )

    def get_term_children(
        self, ontology_id: str, term_id: str
    ) -> schemas.TermRelatives:
        """
        Get children for a term.
        :param ontology_id: Name of ontology, e.g. "go"
        :param term_id: Term ID (URI, short form or obo ID)
        :return: response object. the actual terms are in a list at
          ``response.embedded.terms``
        """
        return self._get_term_relatives(
            "children", ontology_id=ontology_id, term_id=term_id
        )

    def get_term_ancestors(
        self, ontology_id: str, term_id: str
    ) -> schemas.TermRelatives:
        """
        Get ancestors for a term.
        :param ontology_id: Name of ontology, e.g. "go"
        :param term_id: Term ID (URI, short form or obo ID)
        :return: response object. the actual terms are in a list at
          ``response.embedded.terms``
        """
        return self._get_term_relatives(
            "ancestors", ontology_id=ontology_id, term_id=term_id
        )

    def get_term_descendants(
        self, ontology_id: str, term_id: str
    ) -> schemas.TermRelatives:
        """
        Get descendants for a term.
        :param ontology_id: Name of ontology, e.g. "go"
        :param term_id: Term ID (URI, short form or obo ID)
        :return: response object. the actual terms are in a list at
          ``response.embedded.terms``
        """
        return self._get_term_relatives(
            "descendants", ontology_id=ontology_id, term_id=term_id
        )

    def get_term_hierarchical_ancestors(
        self, ontology_id: str, term_id: str
    ) -> schemas.TermRelatives:
        """
        Get hierarchical ancestors for a term.
        :param ontology_id: Name of ontology, e.g. "go"
        :param term_id: Term ID (URI, short form or obo ID)
        :return: response object. the actual terms are in a list at
          ``response.embedded.terms``
        """
        return self._get_term_relatives(
            "hierarchicalAncestors", ontology_id=ontology_id, term_id=term_id
        )

    def get_term_hierarchical_descendants(
        self, ontology_id: str, term_id: str
    ) -> schemas.TermRelatives:
        """
        Get hierarchical descendants for a term.
        :param ontology_id: Name of ontology, e.g. "go"
        :param term_id: Term ID (URI, short form or obo ID)
        :return: response object. the actual terms are in a list at
          ``response.embedded.terms``
        """
        return self._get_term_relatives(
            "hierarchicalAncestors", ontology_id=ontology_id, term_id=term_id
        )

    @staticmethod
    def _add_wildcards(query: str) -> str:
        with_wildcards = [f"{term}*" for term in query.split(" ")]
        return " ".join(with_wildcards)

    def search(
        self, query: str, params: dict, add_wildcards: bool = False
    ) -> schemas.SearchResponse:
        """
        Search for ``query`` using the /search API endpoint.

        :param query: term(s) to search for
        :param params: dictionary of search parameters
        :param add_wildcards: Add a wildcard * to each word in ``query`` -
           good for broad/flexible searches
        :return:
        """
        if add_wildcards:
            query = self._add_wildcards(query)
        validated_params = schemas.SearchParams(q=query, **params)
        query_params = validated_params.get_query_dict()
        resp = self.get_with_schema(
            schemas.SearchResponse, "/search", params=query_params
        )
        return resp
