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
    page: Optional[NonNegativeInt]


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
    ontology: Optional[list[str]]
    type: Optional[EntityType]
    slim: Optional[list[str]]
    fieldList: Optional[list[SearchReturnFields]]
    queryFields: Optional[list[SearchQueryFields]]
    exact: Optional[bool]
    groupField: Optional[bool]
    obsoletes: Optional[bool]
    local: Optional[bool]
    childrenOf: Optional[list[str]]
    allChildrenOf: Optional[list[str]]
    rows: Optional[int]
    start: Optional[int]

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
