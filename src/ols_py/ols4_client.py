from __future__ import annotations

from typing import Any, Mapping, Optional, TypeVar

import pydantic
from pydantic import validate_call

from . import schemas
from .client import OlsClient
from .instances import EBI_OLS4
from .schemas.requests import get_query_dict

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
        :param base_url: Base API URL for the OLS instance, up to and including /api/
        """
        super().__init__(base_url=base_url)

    @validate_call
    def search(
        self,
        query: str,
        params: Optional[schemas.requests.SearchParams] = None,
        add_wildcards: bool = False,
    ) -> schemas.responses.SearchResponse:
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
        if params is None:
            request_params = {"q": query}
        else:
            request_params = {"q": query, **get_query_dict(params)}
        resp = self.get_with_schema(
            schemas.responses.SearchResponse, "/search", params=request_params
        )
        return resp

    @validate_call
    def select(
        self,
        query: str,
        params: Optional[schemas.requests.SelectParams] = None,
        add_wildcards: bool = False,
    ) -> schemas.responses.SearchResponse:
        """
        Search for ``query`` using the /select API endpoint, which
        is supposed to be tuned to return good results for autocomplete.

        :param query: term(s) to search for
        :param params: dictionary of optional parameters
        :param add_wildcards: Add a wildcard * to each word in ``query`` -
           good for broad/flexible searches
        :return:
        """
        if add_wildcards:
            query = self._add_wildcards(query)
        if params is None:
            request_params = {"q": query}
        else:
            request_params = {"q": query, **get_query_dict(params)}
        resp = self.get_with_schema(
            schemas.responses.SearchResponse, "/search", params=request_params
        )
        return resp

    def get_term_in_defining_ontology(
        self,
        iri: Optional[str] = None,
        params: Optional[schemas.requests.TermInDefiningOntologyParams] = None,
    ) -> schemas.responses.TermInDefiningOntology:
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
                schemas.responses.TermInDefiningOntology, path=path
            )
        if params:
            path = "/terms/findByIdAndIsDefiningOntology"
            return self.get_with_schema(
                schemas.responses.TermInDefiningOntology, path=path, params=params
            )
        raise ValueError("One of iri or params arguments is required")

    def get_related_term_by_property(
        self, ontology_id: str, term_iri: str, property_iri: str
    ):
        """
        Use the /ontologies/{ontology_id}/terms/{term_iri}/{property_iri} endpoint to find
        related terms.

        From the OLS4 docs:
            In cases where a term has a direct relation to another term (single existential to a
            named class in OBO), for example a "part of" relation, the related terms can be
            accessed directly with this API.

        Example request:

        http://www.ebi.ac.uk/ols4/api/ontologies/uberon/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FUBERON_0000016/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FBFO_0000050
        """
        term_iri = self._quote_iri(term_iri)
        property_iri = self._quote_iri(property_iri)
        path = f"/ontologies/{ontology_id}/terms/{term_iri}/{property_iri}"
        return self.get_with_schema(schemas.responses.MultipleTerms, path=path)
