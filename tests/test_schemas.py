from ols_py.schemas import SearchParams


def test_convert_list_of_strings():
    """
    Check a single string is automatically converted
    to list for fields annotated as list[str]
    """
    params = SearchParams(q="dummy", ontology="upheno")
    assert isinstance(params.ontology, list)
    assert params.ontology[0] == "upheno"


def test_search_params_valid():
    """
    Test we can create a SearchParams object from valid values
    """
    params = SearchParams(
        q="patella",
        ontology=["upheno", "mondo"],
        type="individual",
        # Leave out slim: should be optional
        fieldList=["iri", "obo_id", "description"],
        queryFields=["label", "synonym"],
        exact=False,
        groupField=False,
        obsoletes=False,
        # Leave out childrenOf, allChildrenOf
        rows=10,
        start=1,
    )


def test_search_params_get_query_dict():
    """
    Test we convert option lists to comma-separated strings
    """
    params = SearchParams(
        q="dummy",
        ontology=["mondo", "upheno"],
        fieldList="iri",
    )
    query_dict = params.get_query_dict()
    assert query_dict["ontology"] == "mondo,upheno"
    # Single values should be untouched
    assert query_dict["fieldList"] == "iri"
