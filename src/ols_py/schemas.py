from __future__ import annotations

from typing import Literal, Optional

import pydantic
from pydantic import BaseModel, Field, HttpUrl, validator


class Link(BaseModel):
    href: HttpUrl


class RootLinks(BaseModel):
    ontologies: Link
    individuals: Link
    terms: Link
    properties: Link
    profile: Link


class ApiRoot(BaseModel):
    links: RootLinks = Field(None, alias="_links")


class OntologyItem(BaseModel):
    ontologyId: str
    status: str
    numberOfProperties: int
    numberOfTerms: int

    class Config:
        extra = "allow"


class OntologyListEmbedded(BaseModel):
    ontologies: list[OntologyItem]


class OntologyList(BaseModel):
    page: PageInfo
    embedded: OntologyListEmbedded = Field(None, alias="_embedded")


class Term(BaseModel):
    iri: pydantic.AnyUrl
    label: str
    description: list[str]
    synonyms: Optional[list[str]]
    ontology_name: str
    ontology_iri: pydantic.AnyUrl
    obo_id: str

    class Config:
        extra = "allow"


class PageInfo(BaseModel):
    size: int
    totalElements: int
    totalPages: int
    number: int


# TODO: what other fields are allowed here? it's not
#   obvious from the docs
SearchReturnFields = Literal[
    "iri",
    "label",
    "short_form",
    "obo_id",
    "ontology_name",
    "ontology_prefix",
    "description",
    "type",
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
    type: Optional[Literal["class", "property", "individual", "ontology"]]
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
        query_dict = {}
        for field_name, value in self:
            if isinstance(value, list):
                value = ",".join(value)
            query_dict[field_name] = value
        return query_dict


# TODO: more fields to include here
class SearchResultItem(BaseModel):
    id: str
    iri: Optional[str]
    short_form: Optional[str]
    description: Optional[list[str]]
    label: Optional[str]


class SearchResponseResponse(BaseModel):
    numFound: int
    start: int
    docs: list[SearchResultItem]


class SearchResponse(BaseModel):
    responseHeader: dict
    response: SearchResponseResponse


class OlsErrorSchema(BaseModel):
    """
    Error data returned the OLS API for a bad request/error
    """

    error: str
    message: str
    path: str
    status: int
    timestamp: int | float


# Update forward refs for any types that were annotated as string
OntologyList.update_forward_refs()
