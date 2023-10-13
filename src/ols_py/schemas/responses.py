from __future__ import annotations

from typing import Any, Optional

import pydantic
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, HttpUrl

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


# TODO: not sure which of these are optional
class OboXref(BaseModel):
    database: Optional[str] = None
    id: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None


class OboSynonym(BaseModel):
    name: str
    # TODO: can this be a fixed set, e.g. hasExactSynonym, hasRelatedSynonym?
    scope: str
    type: Optional[str] = None
    xrefs: list[OboXref] = Field(default_factory=list)


class Term(BaseModel):
    """
    Response returned by term endpoints
    """

    # Haven't typed all attributes yet, so allow additional fields
    #   for now
    model_config = ConfigDict(extra="allow")
    iri: pydantic.AnyUrl
    label: str
    description: list[str]
    # Not specifying annotations for now, not sure if these
    #   are fixed
    annotation: dict[str, list[str]]
    synonyms: Optional[list[str]] = None
    obo_xref: Optional[list[OboXref]] = None
    obo_synonym: Optional[list[OboSynonym]] = None
    ontology_name: str
    ontology_prefix: str
    ontology_iri: pydantic.AnyUrl
    is_obsolete: bool
    term_replaced_by: Optional[Any] = None
    has_children: bool
    is_root: bool
    short_form: str
    # Higher level terms may not have an obo ID, e.g.
    # terms will be descendants of http://www.w3.org/2002/07/owl#Thing
    obo_id: Optional[str] = None
    in_subset: Optional[Any] = None
    links: dict[str, Link] = Field(..., alias="_links")


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


class OntologyItemLinks(BaseModel):
    self: Link
    terms: Link
    properties: Link
    individuals: Link


class OntologyItem(BaseModel):
    ontologyId: str
    status: str
    numberOfProperties: int
    numberOfTerms: int
    languages: Optional[list[str]] = None
    links: OntologyItemLinks = Field(..., alias="_links")

    # TODO: not all fields have been documented so far, allow
    #   them through with extra="allow" for now
    model_config = ConfigDict(extra="allow")


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


class MultipleTerms(BaseModel):
    """
    Response returned for endpoints which return multiple term results,
    e.g. parents, ancestors, descendants etc.
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

    embedded: EmbeddedTerms | None = Field(None, alias="_embedded")
    links: TermInDefiningOntologyLinks = Field(..., alias="_links")
    page: PageInfo


class SearchResultItem(BaseModel, extra="allow"):
    id: Optional[str] = None
    annotations: Optional[list[str]] = None
    annotations_trimmed: Optional[list[str]] = None
    description: Optional[list[str]] = None
    iri: Optional[str] = None
    label: Optional[str] = None
    obo_id: Optional[str] = None
    ontology_name: Optional[str] = None
    ontology_prefix: Optional[str] = None
    subset: Optional[list[str]] = None
    short_form: Optional[str] = None
    # This field is actually named 'synonym' in OLS search
    #   responses, but we remap it to synonyms
    synonyms: Optional[list[str]] = Field(
        default=None, validation_alias=AliasChoices("synonyms", "synonym")
    )
    type: Optional[EntityType] = None


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
