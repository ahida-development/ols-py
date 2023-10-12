from typing import get_args

import ols_py.schemas.requests
import ols_py.schemas.responses
from ols_py.schemas.requests import SearchParams, get_query_dict


def test_search_params_valid():
    """
    Test we can create a SearchParams dict from valid values
    """
    params: SearchParams = {
        "ontology": ["upheno", "mondo"],
        "type": "individual",
        # Leave out slim: should be optional
        "fieldList": ["iri", "obo_id", "description"],
        "queryFields": ["label", "synonym"],
        "exact": False,
        "groupField": False,
        "obsoletes": False,
        # Leave out childrenOf, allChildrenOf
        "rows": 10,
        "start": 1,
    }


def test_search_params_get_query_dict():
    """
    Test we convert option lists to comma-separated strings
    """
    params = SearchParams(
        q="dummy",
        ontology=["mondo", "upheno"],
        fieldList=["iri"],
    )
    query_dict = get_query_dict(params)
    assert query_dict["ontology"] == "mondo,upheno"
    # Single values should be untouched
    assert query_dict["fieldList"] == "iri"


def test_search_fields():
    """
    Check fields match between SearchReturnFields and SearchResultItem
    """
    return_fields = set(get_args(ols_py.schemas.requests.SearchReturnFields))
    result_item_fields = set(
        ols_py.schemas.responses.SearchResultItem.model_json_schema()[
            "properties"
        ].keys()
    )
    # Result items have an extra id field, and we also remap 'synonym'
    #   to synonyms
    assert result_item_fields - return_fields == {"id", "synonyms"}
