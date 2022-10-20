from __future__ import annotations

from typing import Any, Optional

import pydantic
from pydantic import BaseModel, Extra, Field, HttpUrl

from ols_py.schemas.common import EntityType


class PageInfo(BaseModel):
    """
    Page information returned in paginated responses
    """

    size: int
    totalElements: int
    totalPages: int
    number: int


class Link(BaseModel):
    """
    Link item returned in responses
    """

    href: HttpUrl


class Term(BaseModel):
    """
    Response returned by term endpoints
    """

    iri: pydantic.AnyUrl
    label: str
    description: list[str]
    # Not specifying annotations for now, not sure if these
    #   are fixed
    annotation: dict[str, list[str]]
    synonyms: Optional[list[str]]
    ontology_name: str
    ontology_prefix: str
    ontology_iri: pydantic.AnyUrl
    is_obsolete: bool
    term_replaced_by: Optional[Any]
    has_children: bool
    is_root: bool
    short_form: str
    # Higher level terms may not have an obo ID, e.g.
    # terms will be descendants of http://www.w3.org/2002/07/owl#Thing
    obo_id: Optional[str]
    in_subset: Optional[Any]
    links: dict[str, Link] = Field(..., alias="_links")

    class Config:
        extra = "allow"


class ApiInfoLinks(BaseModel):
    """
    Set of links returned in the root endpoint/
    API ifno
    """

    ontologies: Link
    individuals: Link
    terms: Link
    properties: Link
    profile: Link


class ApiInfo(BaseModel):
    """
    Response returned by the root API endpoint,
    links to other endpoints/resources
    """

    links: ApiInfoLinks = Field(..., alias="_links")


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


class EmbeddedTerms(BaseModel):
    """
    "_embedded" field used in responses returning terms
    """

    terms: list[Term]


class TermRelativesLinks(BaseModel):
    self: Link


class TermRelatives(BaseModel):
    """
    Response returned for term parents, ancestors, descendants etc.
    The actual terms are at ``response.embedded.terms``
    """

    embedded: EmbeddedTerms = Field(None, alias="_embedded")
    links: TermRelativesLinks = Field(None, alias="_links")
    page: PageInfo


class TermInDefiningOntologyLinks(BaseModel):
    self: Link


class TermInDefiningOntology(BaseModel):
    """
    Response returned for /terms/findByIdAndIsDefiningOntology/
    endpoint
    """

    embedded: EmbeddedTerms = Field(..., alias="_embedded")
    links: TermInDefiningOntologyLinks = Field(..., alias="_links")
    page: PageInfo


class SearchResultItem(BaseModel, extra=Extra.allow):
    id: Optional[str]
    annotations: Optional[list[str]]
    annotations_trimmed: Optional[list[str]]
    description: Optional[list[str]]
    iri: Optional[str]
    label: Optional[str]
    obo_id: Optional[str]
    ontology_name: Optional[str]
    ontology_prefix: Optional[str]
    subset: Optional[list[str]]
    short_form: Optional[str]
    synonym: Optional[list[str]]
    type: Optional[EntityType]


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
