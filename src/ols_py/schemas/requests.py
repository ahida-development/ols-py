from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, NonNegativeInt, PositiveInt, validator

from .common import EntityType


class PageParams(BaseModel):
    """
    Pagination params accepted by endpoints that return multiple
    resources
    """

    size: Optional[PositiveInt]
    """Number of results per page"""
    page: Optional[NonNegativeInt]
    """Which page to fetch (starting at 0)"""


SearchReturnFields = Literal[
    "iri",
    "label",
    "short_form",
    "obo_id",
    "ontology_name",
    "ontology_prefix",
    "description",
    "type",
    "synonym",
]
SearchQueryFields = Literal[
    "label",
    "synonym",
    "description",
    "short_form",
    "obo_id",
    "annotations",
    "logical_description",
    "iri",
]


class SearchParams(BaseModel):
    """
    Schema for parameters accepted by the search endpoint.
    Note you should use get_query_dict() to get a dictionary
    you can use in the request - we want to convert any
    lists of options to comma-separated strings, which
    we can't do with the default dict() method
    """

    q: str
    """Query to search for"""
    ontology: Optional[list[str]]
    """Ontologies to search, e.g. `["mondo", "upheno"]`"""
    type: Optional[EntityType]
    """Type of term to search for, e.g. "class", "property" """
    slim: Optional[list[str]]
    fieldList: Optional[list[SearchReturnFields]]
    """Which fields to return in the results"""
    queryFields: Optional[list[SearchQueryFields]]
    """Which fields to search over"""
    exact: Optional[bool]
    groupField: Optional[bool]
    """Group results by unique ID"""
    obsoletes: Optional[bool]
    """Include obsoleted terms in the results"""
    local: Optional[bool]
    """Only return terms in a defining ontology"""
    childrenOf: Optional[list[str]]
    """Restrict results to children of these terms"""
    allChildrenOf: Optional[list[str]]
    """
    Restrict results to children of these terms, plus other
    child-like relations e.g. "part of", "develops from"
    """
    rows: Optional[int]
    """
    Number of results per page
    """
    start: Optional[int]
    """
    Index of first result
    """

    @validator(
        "ontology",
        "slim",
        "childrenOf",
        "allChildrenOf",
        "fieldList",
        "queryFields",
        pre=True,
    )
    def _single_to_list(cls, v):
        """
        If a single string is passed but we expect
        list[str], convert to a 1-item list automatically.
        Called at the pre-validation step.
        """
        if isinstance(v, str):
            return [v]
        return v

    def get_query_dict(self) -> dict[str, str | bool | int]:
        """
        Convert to dictionary, converting any list values to
        comma-separated string, as required by the search endpoint
        """
        query_dict = {}
        for field_name, value in self:
            if isinstance(value, list):
                value = ",".join(value)
            query_dict[field_name] = value
        return query_dict


RelativeTypes = Literal[
    "parents",
    "children",
    "ancestors",
    "descendants",
    "hierarchicalDescendants",
    "hierarchicalAncestors",
]

TermInDefiningOntologyParams = dict[Literal["iri", "short_form", "obo_id", "id"], str]
