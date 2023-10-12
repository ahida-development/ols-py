import pytest

from ols_py.instances import EBI_OLS4
from ols_py.ols4_client import Ols4Client


@pytest.fixture
def ols4_client():
    return Ols4Client(base_url=EBI_OLS4)


def test_get_ontologies(ols4_client):
    """
    Test we can get a list of ontologies from OLS4

    Example request:

    curl -L 'http://www.ebi.ac.uk/ols4/api/ontologies?page=1&size=1' -i
    """
    ontologies = ols4_client.get_ontologies(page=1, size=1)
    ontology = ontologies.embedded.ontologies[0]
    assert ontology.ontologyId


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


def test_get_api_info(ols4_client):
    """
    Test we can get the API entry point

    Example request

    curl -L 'http://www.ebi.ac.uk/ols4/api/' -i -H 'Accept: application/json'
    """
    resp = ols4_client.get_api_info()
    assert resp.links.ontologies.href


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
