from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


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


class PageInfo(BaseModel):
    size: int
    totalElements: int
    totalPages: int
    number: int


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
