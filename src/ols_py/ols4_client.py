from __future__ import annotations

from typing import Any, Mapping, Optional, TypeVar

import pydantic

from . import ols4_schemas, schemas
from .client import OlsClient
from .instances import EBI_OLS4

S = TypeVar("S", bound=pydantic.BaseModel, covariant=True)
ParamsMapping = Mapping[str, Any]


class Ols4Client(OlsClient):
    """
    Client for communicating with an OLS4 instance.

    The response structure has changed for some endpoints, so
    we need to override some methods
    """

    base_url: str

    def __init__(self, base_url: str = EBI_OLS4):
        """
        :param base_url: Base API URL for the OLS instance
        """
        super().__init__(base_url=base_url)

    def search(
        self, query: str, params: dict, add_wildcards: bool = False
    ) -> ols4_schemas.responses.SearchResponse:
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
        validated_params = schemas.requests.SearchParams(q=query, **params)
        query_params = validated_params.get_query_dict()
        resp = self.get_with_schema(
            ols4_schemas.responses.SearchResponse, "/search", params=query_params
        )
        return resp

    def get_term_in_defining_ontology(
        self,
        iri: Optional[str] = None,
        params: Optional[schemas.requests.TermInDefiningOntologyParams] = None,
    ) -> ols4_schemas.responses.TermInDefiningOntology:
        """
        Use the /terms/findByIdAndIsDefiningOntology/ to find a term in
        its defining ontology. This allows you to look up a term by IRI
        alone.

        :param iri: IRI for the term. You can either provide this, or use the ``params``
           argument (not both).
        :param params: GET parameters. the /findByIdAndIsDefiningOntology/ endpoint
           allows "iri", "short_form", "obo_id", or "id"
        :return: JSON data. Terms are at resp.embedded.terms
        :raises ValueError: if both/neither IRI and params arguments were given.
        """
        if iri and params:
            raise ValueError("Pass either iri or params arguments, not both")
        if iri:
            iri_encoded = self._quote_iri(iri)
            path = f"/terms/findByIdAndIsDefiningOntology/{iri_encoded}"
            return self.get_with_schema(
                ols4_schemas.responses.TermInDefiningOntology, path=path
            )
        if params:
            path = "/terms/findByIdAndIsDefiningOntology"
            return self.get_with_schema(
                ols4_schemas.responses.TermInDefiningOntology, path=path, params=params
            )
        raise ValueError("One of iri or params arguments is required")
