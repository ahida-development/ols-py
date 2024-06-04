import json
from unittest import mock

import pydantic
import pytest
import requests

from ols_py.client import Ols4Client
from ols_py.instances import EBI_OLS4
from ols_py.schemas.responses import OlsErrorSchema


@pytest.fixture
def ols4_client() -> Ols4Client:
    return Ols4Client(base_url=EBI_OLS4)


class DummySchema(pydantic.BaseModel):
    """
    Very simple schema used for mock testing
    """

    number: int


def test_ols_error():
    """
    Perform a bad request so we can check that the
    error response can be parsed with our schema
    """
    resp = requests.get(
        EBI_OLS4 + "/ontologies/foobar", headers={"accept": "application/json"}
    )
    # OLS4 currently returns binary data instead of JSON?
    parsed_json = json.loads(resp.content.decode("utf8"))
    error = OlsErrorSchema(**parsed_json)
    assert error


def test_client_base_url():
    """
    Check we always add a / to the end of base_url
    """
    with_slash = "www.example.com/api/"
    client = Ols4Client(base_url=with_slash)
    assert client.base_url == with_slash
    no_slash = "www.example.com/api"
    client2 = Ols4Client(base_url=no_slash)
    assert client2.base_url == with_slash


def test_get_api_info(ols4_client):
    """
    Test we can get the API entry point

    Example request

    curl -L 'http://www.ebi.ac.uk/ols4/api/' -i -H 'Accept: application/json'
    """
    resp = ols4_client.get_api_info()
    assert resp.links.ontologies.href


def test_get_ontologies(ols4_client):
    """
    Test we can get a list of ontologies from OLS4

    Example request:

    curl -L 'http://www.ebi.ac.uk/ols4/api/ontologies?page=1&size=1' -i
    """
    ontologies = ols4_client.get_ontologies(page=1, size=1)
    ontology = ontologies.embedded.ontologies[0]
    assert ontology.ontologyId


def test_get_ontologies_paginated(ols4_client):
    data = ols4_client.get_ontologies(page=2, size=5)
    assert data.page.size == 5
    assert data.page.number == 2


def test_get_many_ontologies(ols4_client):
    """
    Try to get a lot of ontologies, to test whether they all validate against
    our schema
    """
    ontologies = ols4_client.get_ontologies(size=200)
    ontology = ontologies.embedded.ontologies[0]
    assert len(ontologies.embedded.ontologies) == 200
    assert ontology.ontologyId


def test_get_single_ontology(ols4_client):
    """
    Test we can get the details for a single ontology

    Example request:

    curl -L 'http://www.ebi.ac.uk/ols4/api/ontologies/efo' -i -H 'Accept: application/json'
    """
    ontology = ols4_client.get_ontology("efo")
    assert ontology.ontologyId


def test_get_ontology_terms(ols4_client):
    """
    List terms (or classes) in OLS from a particular ontology

    Example request:

    curl -L 'http://www.ebi.ac.uk/ols4/api/ontologies/efo/terms' -i -H 'Accept: application/json'
    """
    resp = ols4_client.get_terms(ontology_id="efo", params={"size": 20})
    terms = resp.embedded.terms
    assert len(terms) == 20


def test_get_single_ontology_term(ols4_client):
    """
    Get a single term from an ontology by IRI

    Example request:

    curl -L 'http://www.ebi.ac.uk/ols4/api/ontologies/go/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FGO_0043226' -i -H 'Accept: application/json'
    """
    iri = "http://purl.obolibrary.org/obo/GO_0043226"
    resp = ols4_client.get_terms(ontology_id="go", params={"iri": iri})
    terms = resp.embedded.terms
    assert len(terms) == 1
    assert str(terms[0].iri) == iri


@pytest.mark.parametrize(
    "relatives",
    [
        "parents",
        "children",
        "ancestors",
        "descendants",
        "hierarchical_ancestors",
        "hierarchical_descendants",
    ],
)
def test_get_term_relatives(relatives, ols4_client):
    """
    Test the different methods for retrieving a term's ancestors/descendants

    Example requests:

    curl -L 'http://www.ebi.ac.uk/ols4/api/ontologies/go/parents?id=GO:0043226' -i -H 'Accept: application/json'
    curl -L 'http://www.ebi.ac.uk/ols4/api/ontologies/go/children?id=GO:0043226' -i -H 'Accept: application/json'
    curl -L 'http://www.ebi.ac.uk/ols4/api/ontologies/go/ancestors?id=GO:0043226' -i -H 'Accept: application/json'
    curl -L 'http://www.ebi.ac.uk/ols4/api/ontologies/go/descendants?id=GO:0043226' -i -H 'Accept: application/json'
    curl -L 'http://www.ebi.ac.uk/ols4/api/ontologies/go/hierarchicalDescendants?id=GO:0043226' -i -H 'Accept: application/json'
    curl -L 'http://www.ebi.ac.uk/ols4/api/ontologies/go/hierarchicalAncestors?id=GO:0043226' -i -H 'Accept: application/json'
    """
    method = getattr(ols4_client, f"get_term_{relatives}")
    resp = method(ontology_id="go", term_id="GO:0043226")
    assert len(resp.embedded.terms) > 0
    relative = resp.embedded.terms[0]
    assert relative.iri


def test_get_term_relatives_params(ols4_client):
    """
    Check we can get more than 20 terms using the params for relative term lookups
    """
    mp_root = "http://purl.obolibrary.org/obo/MP_0000001"
    resp = ols4_client.get_term_children(
        ontology_id="mp", term_id=mp_root, params={"size": 50}
    )
    # Should be able to get all children of the root
    assert len(resp.embedded.terms) == resp.page.totalElements


# TODO: not working in OLS4 yet?
def test_get_related_term_by_property(ols4_client):
    # Pancreas
    target_term = "http://purl.obolibrary.org/obo/UBERON_0001264"
    # Endocrine pancreas
    source_term = "http://purl.obolibrary.org/obo/UBERON_0000016"
    # 'part of' relation
    property = "http://purl.obolibrary.org/obo/BFO_0000050"
    resp = ols4_client.get_related_term_by_property(
        "uberon", term_iri=source_term, property_iri=property
    )
    terms = resp.embedded.terms
    assert len(terms) >= 1
    assert target_term in [t.iri for t in terms]


def test_get_with_schema_valid_data(ols4_client):
    """
    Test we just get the data returned and no exceptions
    when data matches the schema
    """
    # Return data from the get request that matches the schema
    ols4_client.get = mock.MagicMock(return_value={"number": 3})
    data = ols4_client.get_with_schema(DummySchema, "/")
    assert data.number == 3


def test_get_with_schema_invalid_data(ols4_client):
    """
    Test we get a ValidationError when the data returned
    by the API doesn't match our schema
    """
    # Return data from the get request that doesn't match the
    # schema
    ols4_client.get = mock.MagicMock(return_value={"number": "word"})
    with pytest.raises(pydantic.ValidationError):
        resp = ols4_client.get_with_schema(DummySchema, "/")
        print(resp)


@pytest.mark.parametrize(
    "id_type,value",
    [
        ("iri", "http://www.ebi.ac.uk/efo/EFO_0000001"),
        ("short_form", "EFO_0000001"),
        ("obo_id", "EFO:0000001"),
    ],
)
def test_find_terms(id_type, value, ols4_client):
    """
    Test searching form terms across ontologies
    """
    resp = ols4_client.find_terms({id_type: value})
    terms = resp.embedded.terms
    assert str(terms[0].iri) == "http://www.ebi.ac.uk/efo/EFO_0000001"


def test_get_property(ols4_client):
    property_iri = "http://purl.obolibrary.org/obo/BFO_0000050"
    resp = ols4_client.get_property(ontology_id="efo", iri=property_iri)
    assert str(resp.iri) == property_iri


def test_get_individual(ols4_client):
    individual_iri = "http://purl.obolibrary.org/obo/IAO_0000002"
    resp = ols4_client.get_individual(ontology_id="iao", iri=individual_iri)
    assert str(resp.iri) == individual_iri


def test_search(ols4_client):
    """
    Test we can get search results from the search endpoint.

    Structure of responses is different in OLS4
    """
    resp = ols4_client.search(query="patella", params={"ontology": "mondo", "rows": 10})
    assert len(resp.response.docs) > 0
    first_result = resp.response.docs[0]
    assert first_result.iri


def test_select(ols4_client):
    """
    Test we can get search results from the select endpoint.
    """
    resp = ols4_client.select(query="patella", params={"ontology": "mondo", "rows": 10})
    assert len(resp.response.docs) > 0
    first_result = resp.response.docs[0]
    assert first_result.iri


def test_search_add_wildcards(ols4_client):
    """
    Test that add_wildcards option performs search with wildcards added
    to each term
    """
    resp = ols4_client.search(
        query="hi dys", params={"ontology": "mondo", "rows": 5}, add_wildcards=True
    )
    manual_resp = ols4_client.search(
        query="hi* dys*", params={"ontology": "mondo", "rows": 5}
    )
    assert resp.response.numFound == manual_resp.response.numFound


def test_search_returns_synonyms(ols4_client):
    """
    Test we can get synonyms via the fieldList parameter

    (this got lost during the OLS3 -> OLS4 upgrade but should be working again)
    """
    resp = ols4_client.search(
        query="Bos taurus",
        params={
            "ontology": "ncbitaxon",
            "rows": 10,
            "queryFields": ["label"],
            "fieldList": ["iri", "label", "obo_id", "synonym"],
            # Use exact, we just want to make sure we get bos taurus so
            #   we can check its synonyms
            "exact": True,
            "childrenOf": ["http://purl.obolibrary.org/obo/NCBITaxon_9903"],
        },
    )
    first_result = resp.response.docs[0]
    assert "cow" in first_result.synonyms


def test_search_retrieve_annotation(ols4_client):
    """
    Test we can include a specific annotation in fieldList
    and have it returned in the search results
    """
    apoptotic_iri = "http://purl.obolibrary.org/obo/GO_0006915"
    resp = ols4_client.search(
        query="apoptotic process",
        params={
            "ontology": "go",
            "rows": 10,
            "queryFields": ["label"],
            "fieldList": ["iri", "label", "has_alternative_id_annotation"],
        },
    )
    docs = resp.response.docs
    apoptopic = [d for d in docs if d.iri == apoptotic_iri][0]
    assert hasattr(apoptopic, "has_alternative_id_annotation")
    assert "GO:0006917" in apoptopic.has_alternative_id_annotation


def test_search_validate_params(ols4_client):
    """
    Test we get validation errors from PyDantic when providing incorrect
    search params
    """
    with pytest.raises(pydantic.ValidationError, match="params.type"):
        resp = ols4_client.search(query="cow", params={"type": "klass"})


def test_quote_iri():
    """
    Make sure we are correctly double URL encoding IRIs for
    when they need to be used in paths etc.
    """
    iri = "http://purl.obolibrary.org/obo/GO_0043226"
    expected = "http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FGO_0043226"
    assert Ols4Client._quote_iri(iri) == expected


def test_add_wildcards():
    """
    Check we add a wildcard * to each word in the query
    """
    query = "multiple terms"
    result = Ols4Client._add_wildcards(query)
    assert result == "multiple* terms*"


def test_get_term_in_defining_ontology(ols4_client):
    """
    Test various forms of ID that are/aren't working in OLs4
    """
    iri = "http://purl.obolibrary.org/obo/MONDO_0018660"
    resp = ols4_client.get_term_in_defining_ontology(iri=iri)
    term = resp.embedded.terms[0]
    assert str(term.iri) == iri
    assert term.ontology_name == "mondo"
    # OBO ID search should be working now
    obo_id = "MONDO:0018660"
    resp_from_obo = ols4_client.get_term_in_defining_ontology(params={"obo_id": obo_id})
    assert resp_from_obo.page.totalElements == 1
    assert str(resp_from_obo.embedded.terms[0].iri) == iri
    # Short form should work
    short_form = "MONDO_0018660"
    resp_from_short_form = ols4_client.get_term_in_defining_ontology(
        params={"short_form": short_form}
    )
    assert resp_from_short_form.page.totalElements == 1
    assert str(resp_from_short_form.embedded.terms[0].iri) == iri
