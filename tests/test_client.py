from unittest import mock

import pydantic
import pytest
import requests

from ols_py.client import OlsClient
from ols_py.schemas import ApiRoot, OlsErrorSchema

EBI_BASE_URL = "https://www.ebi.ac.uk/ols/api/"


@pytest.fixture
def ebi_client():
    return OlsClient(base_url=EBI_BASE_URL)


class DummySchema(pydantic.BaseModel):
    """
    Very simple schema used for mock testing
    """

    number: int


# TODO: can't seem to get an actual JSON response for errors,
#   just getting HTML
@pytest.mark.skip
def test_ols_error():
    """
    Perform a bad request so we can check that the
    error response cane be parsed with our schema
    """
    resp = requests.get(
        EBI_BASE_URL + "/ontologies/foobar", headers={"accept": "application/json"}
    )
    print(resp.content)
    validation_errors = OlsErrorSchema().validate(resp.json())
    assert validation_errors


def test_get_base_api(ebi_client):
    """
    Test that we get the expected data when
    calling the root / API path (links to other resources)
    """
    resp = ebi_client.get("/")
    data = ApiRoot(**resp)
    assert data.links.ontologies.href


def test_client_base_url():
    """
    Check we always add a / to the end of base_url
    """
    with_slash = "www.example.com/api/"
    client = OlsClient(base_url=with_slash)
    assert client.base_url == with_slash
    no_slash = "www.example.com/api"
    client2 = OlsClient(base_url=no_slash)
    assert client2.base_url == with_slash


def test_get_ontologies(ebi_client):
    data = ebi_client.get_ontologies()
    assert len(data.embedded.ontologies) > 0


def test_get_ontology(ebi_client):
    item = ebi_client.get_ontology("efo")
    assert item.ontologyId == "efo"
    assert item.numberOfTerms > 0


def test_get_term(ebi_client):
    term = ebi_client.get_term(
        ontology_id="go", iri="http://purl.obolibrary.org/obo/GO_0043226"
    )
    assert term.ontology_name == "go"
    assert term.iri == "http://purl.obolibrary.org/obo/GO_0043226"
    assert term.label == "organelle"


def test_get_with_schema_valid_data():
    """
    Test we just get the data returned and no exceptions
    when data matches the schema
    """
    client = OlsClient(EBI_BASE_URL)
    # Return data from the get request that matches the schema
    client.get = mock.MagicMock(return_value={"number": 3})
    data = client.get_with_schema(DummySchema, "/")
    assert data.number == 3


def test_get_with_schema_invalid_data():
    """
    Test we get a ValidationError when the data returned
    by the API doesn't match our schema
    """
    client = OlsClient(EBI_BASE_URL)
    # Return data from the get request that doesn't match the
    # schema
    client.get = mock.MagicMock(return_value={"number": "word"})
    with pytest.raises(pydantic.ValidationError):
        resp = client.get_with_schema(DummySchema, "/")
        print(resp)


def test_quote_iri():
    """
    Make sure we are correctly double URL encoding IRIs for
    when they need to be used in paths etc.
    """
    iri = "http://purl.obolibrary.org/obo/GO_0043226"
    expected = "http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FGO_0043226"
    assert OlsClient._quote_iri(iri) == expected
