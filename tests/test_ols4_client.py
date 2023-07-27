import pytest

from ols_py.instances import EBI_OLS4
from ols_py.ols4_client import Ols4Client


@pytest.fixture
def ols4_client():
    return Ols4Client(base_url=EBI_OLS4)


def test_search(ols4_client):
    """
    Test we can get search results from the search endpoint.

    Structure of responses is different in OLS4
    """
    resp = ols4_client.search(query="patella", params={"ontology": "mondo", "rows": 10})
    assert len(resp.response.docs) > 0
    first_result = resp.response.docs[0]
    assert first_result.iri


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
            "fieldList": ["iri", "label", "obo_id", "synonyms"],
            # Use exact, we just want to make sure we get bos taurus so
            #   we can check its synonyms
            "exact": True,
            "childrenOf": ["http://purl.obolibrary.org/obo/NCBITaxon_9903"],
        },
    )
    first_result = resp.response.docs[0]
    assert "cow" in first_result.synonyms


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
    assert resp_from_obo.embedded.terms[0].iri == iri
    # Short form should work
    short_form = "MONDO_0018660"
    resp_from_short_form = ols4_client.get_term_in_defining_ontology(
        params={"short_form": short_form}
    )
    assert resp_from_short_form.page.totalElements == 1
    assert str(resp_from_short_form.embedded.terms[0].iri) == iri
