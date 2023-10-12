from __future__ import annotations

from typing import Literal, NotRequired, Optional, TypedDict

from pydantic import BaseModel, NonNegativeInt, PositiveInt

from .common import AnnotationFieldName, EntityType


class PageParams(BaseModel):
    """
    Pagination params accepted by endpoints that return multiple
    resources
    """

    size: Optional[PositiveInt] = None
    """Number of results per page"""
    page: Optional[NonNegativeInt] = None
    """Which page to fetch (starting at 0)"""


# TODO: unclear whether the API accepts the same set of fields
#   for query/return. Defining them separately for now
# NOTE: fields seem to be badly documented. The best canonical source I've
#   been able to find seems to be going directly to the SOLR config for OLS
#   at https://github.com/EBISPOT/OLS/blob/dev/ols-solr/src/main/solr-5-config/ontology/conf/schema.xml
SearchReturnFields = Literal[
    "annotations",  # TODO: not sure if annotations does anything, annotations_trimmed does
    "annotations_trimmed",
    "description",
    "iri",
    "label",
    "obo_id",
    "ontology_name",
    "ontology_prefix",
    "short_form",
    "subset",
    "synonym",
    "type",
]
SearchQueryFields = Literal[
    "annotations",
    "description",
    "iri",
    "label",
    "logical_description",
    "obo_id",
    "short_form",
    "subset",
    "synonym",
]


class SearchParams(TypedDict):
    """
    Optional parameters passed to search() method (not including
    the q/query parameter).

    NOTE: use get_query_dict() to convert this to the format
    needed by the GET request
    """

    q: str
    """Query to search for"""
    ontology: NotRequired[list[str]]
    """Ontologies to search, e.g. `["mondo", "upheno"]`"""
    type: NotRequired[EntityType]
    """Type of term to search for, e.g. "class", "property" """
    slim: NotRequired[list[str]]
    fieldList: NotRequired[list[SearchReturnFields | AnnotationFieldName]]
    """Which fields to return in the results"""
    queryFields: NotRequired[list[SearchQueryFields | AnnotationFieldName]]
    """Which fields to search over"""
    exact: NotRequired[bool]
    """Only return exact matches"""
    groupField: NotRequired[bool]
    """Group results by unique ID"""
    obsoletes: NotRequired[bool]
    """Include obsoleted terms in the results"""
    local: NotRequired[bool]
    """Only return terms in a defining ontology"""
    childrenOf: NotRequired[list[str]]
    """Restrict results to children of these terms"""
    allChildrenOf: NotRequired[list[str]]
    """
    Restrict results to children of these terms, plus other
    child-like relations e.g. "part of", "develops from"
    """
    rows: NotRequired[int]
    """
    Number of results per page
    """
    start: NotRequired[int]
    """
    Index of first result
    """


def get_query_dict(params: SearchParams) -> dict[str, str | bool | int]:
    """
    Convert SearchParams to the format needed in requests, converting any list values to
    comma-separated string, as required by the search endpoint
    """
    query_dict = {}
    for field_name, value in params.items():
        if isinstance(value, list):
            value = ",".join(value)
        query_dict[field_name] = value
    return query_dict


RelativeTypes = Literal[
    "parents",
    "hierarchicalParents",
    "children",
    "hierarchicalChildren",
    "ancestors",
    "descendants",
    "hierarchicalDescendants",
    "hierarchicalAncestors",
]


class TermInDefiningOntologyParams(TypedDict):
    """
    Optional arguments for get_term_in_defining_ontology() method
    """

    iri: NotRequired[str]
    short_form: NotRequired[str]
    obo_id: NotRequired[str]
    id: NotRequired[str]


class GetTermsParams(TypedDict):
    """
    Optional arguments for get_terms() method
    """

    iri: NotRequired[str]
    short_form: NotRequired[str]
    obo_id: NotRequired[str]
    page: NotRequired[int]
    size: NotRequired[int]
