from __future__ import annotations

from typing import Any, Mapping, Optional, Type, TypeVar
from urllib.parse import quote_plus

import pydantic
import requests

from . import schemas
from .schemas.requests import SearchParams, get_query_dict

S = TypeVar("S", bound=pydantic.BaseModel, covariant=True)
ParamsMapping = Mapping[str, Any]


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

    def get(self, path: str, params: Optional[ParamsMapping] = None) -> dict:
        """
        Perform a GET request to the API. Unlike most of
        the client methods, this just returns the JSON data as a dict,
        without validation/parsing. Useful if you want to test
        an API endpoint, or use an endpoint that's not implemented yet.

        :param path: API path (excluding base url)
        :param params: Query parameters
        :return: JSON data, as a dict
        :raises HTTPError: if response is not OK
        """
        url = self._create_url(path)
        resp = self._session.get(url=url, params=params)
        resp.raise_for_status()
        json_data: dict = resp.json()
        return json_data

    def get_with_schema(
        self, schema: Type[S], path: str, params: Optional[ParamsMapping] = None
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

    def get_api_info(self) -> schemas.responses.ApiInfo:
        """
        Get the list of endpoints supported by the API
        """
        resp = self.get_with_schema(schemas.responses.ApiInfo, path="/")
        return resp

    def get_ontologies(
        self, page: Optional[int] = None, size: Optional[int] = None
    ) -> schemas.responses.OntologyList:
        """
        Get the list of ontologies the OLS instance has.

        :param page: Page number of results (starting at 0)
        :param size: Number of results per page (API default is 20)
        """
        params = schemas.requests.PageParams(page=page, size=size).model_dump(
            exclude_none=True
        )
        ontology_list = self.get_with_schema(
            schemas.responses.OntologyList, "/ontologies", params=params
        )
        return ontology_list

    def get_ontology(self, ontology_id: str) -> schemas.responses.OntologyItem:
        """
        Get details for a single ontology

        :param ontology_id: Ontology ID/name, e.g. "mondo"
        """
        path = f"/ontologies/{ontology_id}/"
        ontology_item = self.get_with_schema(schemas.responses.OntologyItem, path)
        return ontology_item

    def get_term(self, ontology_id: str, iri: str) -> schemas.responses.Term:
        """
        Get a single term in a specific ontology

        :param ontology_id: Ontology ID/name, e.g. "mondo"
        :param iri: IRI for a single term
        :return: Term details
        """
        iri = self._quote_iri(iri)
        path = f"/ontologies/{ontology_id}/terms/{iri}"
        term = self.get_with_schema(schemas.responses.Term, path)
        return term

    def get_terms(
        self, ontology_id: str, params: Optional[schemas.requests.GetTermsParams] = None
    ) -> schemas.responses.MultipleTerms:
        """
        Get multiple terms in a specific ontology, possibly filtering by iri, short_form or obo_id.

        :param params: Optional params. Filter by iri, short_form or obo_id, or specify the
            number of results with ``page`` and ``size``
        """
        path = f"/ontologies/{ontology_id}/terms"
        return self.get_with_schema(
            schemas.responses.MultipleTerms, path, params=params
        )

    def find_terms(self, params: schemas.requests.GetTermsParams):
        """
        Search for terms across ontologies.

        Provide either `iri`, `short_form`, or `obo_id`

        :param params: Request params. You must provide one of `iri`, `short_form` or `obo_id`

        Example requests:

            curl -L 'http://www.ebi.ac.uk/ols4/api/terms/http%253A%252F%252Fwww.ebi.ac.uk%252Fefo%252FEFO_0000001' -i -H 'Accept: application/json'
            curl -L 'http://www.ebi.ac.uk/ols4/api/terms?iri=http://www.ebi.ac.uk/efo/EFO_0000001' -i -H 'Accept: application/json'
            curl -L 'http://www.ebi.ac.uk/ols4/api/terms?short_form=EFO_0000001' -i -H 'Accept: application/json'
            curl -L 'http://www.ebi.ac.uk/ols4/api/terms?obo_id=EFO:0000001' -i -H 'Accept: application/json'
            curl -L 'http://www.ebi.ac.uk/ols4/api/terms?id=EFO:0000001' -i -H 'Accept: application/json'
        """
        path = "/terms"
        return self.get_with_schema(
            schemas.responses.MultipleTerms, path, params=params
        )

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

    def _get_term_relatives(
        self, relatives: schemas.requests.RelativeTypes, ontology_id: str, term_id: str
    ) -> schemas.responses.MultipleTerms:
        """
        Common method for getting a term's parents, children, ancestors etc.
        """
        path = f"/ontologies/{ontology_id}/{relatives}"
        return self.get_with_schema(
            schemas.responses.MultipleTerms, path, params={"id": term_id}
        )

    def get_term_parents(
        self, ontology_id: str, term_id: str
    ) -> schemas.responses.MultipleTerms:
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

    def get_term_hierarchical_parents(
        self, ontology_id: str, term_id: str
    ) -> schemas.responses.MultipleTerms:
        """
        Get hierarchical parents for a term. See [get_term_parents()][ols_py.client.OlsClient.get_term_parents]
        """
        return self._get_term_relatives(
            "hierarchicalParents", ontology_id=ontology_id, term_id=term_id
        )

    def get_term_children(
        self, ontology_id: str, term_id: str
    ) -> schemas.responses.MultipleTerms:
        """
        Get children for a term. See [get_term_parents()][ols_py.client.OlsClient.get_term_parents]
        """
        return self._get_term_relatives(
            "children", ontology_id=ontology_id, term_id=term_id
        )

    def get_term_ancestors(
        self, ontology_id: str, term_id: str
    ) -> schemas.responses.MultipleTerms:
        """
        Get ancestors for a term. See [get_term_parents()][ols_py.client.OlsClient.get_term_parents]
        """
        return self._get_term_relatives(
            "ancestors", ontology_id=ontology_id, term_id=term_id
        )

    def get_term_descendants(
        self, ontology_id: str, term_id: str
    ) -> schemas.responses.MultipleTerms:
        """
        Get descendants for a term. See [get_term_parents()][ols_py.client.OlsClient.get_term_parents]
        """
        return self._get_term_relatives(
            "descendants", ontology_id=ontology_id, term_id=term_id
        )

    def get_term_hierarchical_ancestors(
        self, ontology_id: str, term_id: str
    ) -> schemas.responses.MultipleTerms:
        """
        Get hierarchical ancestors for a term. See [get_term_parents()][ols_py.client.OlsClient.get_term_parents]
        """
        return self._get_term_relatives(
            "hierarchicalAncestors", ontology_id=ontology_id, term_id=term_id
        )

    def get_term_hierarchical_descendants(
        self, ontology_id: str, term_id: str
    ) -> schemas.responses.MultipleTerms:
        """
        Get hierarchical descendants for a term. See [get_term_parents()][ols_py.client.OlsClient.get_term_parents]
        """
        return self._get_term_relatives(
            "hierarchicalAncestors", ontology_id=ontology_id, term_id=term_id
        )

    @staticmethod
    def _add_wildcards(query: str) -> str:
        with_wildcards = [f"{term}*" for term in query.split(" ")]
        return " ".join(with_wildcards)

    def search(
        self,
        query: str,
        params: SearchParams | None = None,
        add_wildcards: bool = False,
    ) -> schemas.responses.SearchResponse:
        """
        Search for ``query`` using the /search API endpoint.

        :param query: term(s) to search for
        :param params: dictionary of search parameters, or a SearchParams object (to validate
            and typecheck the params)
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

    def get_property(self, ontology_id: str, iri: str) -> schemas.responses.Term:
        """
        Get a property from a specific ontology.

        Example request:

            curl -L 'http://www.ebi.ac.uk/ols4/api/ontologies/efo/properties/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FBFO_0000050' -i -H 'Accept: application/json'
        """
        quoted_iri = self._quote_iri(iri)
        path = f"/ontologies/{ontology_id}/properties/{quoted_iri}"
        resp = self.get_with_schema(schemas.responses.Term, path=path)
        return resp

    def get_individual(self, ontology_id: str, iri: str) -> schemas.responses.Term:
        """
        Get an individual from a specific ontology.

        Example request:

            curl -L 'http://www.ebi.ac.uk/ols4/api/ontologies/iao/individuals/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FIAO_0000002' -i -H 'Accept: application/json'
        """
        quoted_iri = self._quote_iri(iri)
        path = f"/ontologies/{ontology_id}/individuals/{quoted_iri}"
        resp = self.get_with_schema(schemas.responses.Term, path=path)
        return resp
