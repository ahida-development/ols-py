from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from ..schemas import responses
from ..schemas.common import EntityType


# Structure of search results has changed from OLS v3,
#   some fields are now list[str] instead of str
class SearchResultItem(BaseModel, extra="allow"):
    id: Optional[str] = None
    annotations: Optional[list[str]] = None
    annotations_trimmed: Optional[list[str]] = None
    description: Optional[list[str]] = None
    iri: Optional[str] = None
    label: Optional[list[str]] = None
    obo_id: Optional[list[str]] = None
    ontology_name: Optional[str] = None
    ontology_prefix: Optional[str] = None
    subset: Optional[list[str]] = None
    short_form: Optional[list[str]] = None
    synonym: Optional[list[str]] = None
    type: Optional[EntityType] = None


class SearchResponseResponse(BaseModel):
    docs: list[SearchResultItem]


class SearchResponse(BaseModel):
    responseHeader: dict
    response: SearchResponseResponse


class TermInDefiningOntology(responses.TermInDefiningOntology):
    """
    Not all responses in Ols4 seem to have the _embedded property so make it optional
    """

    embedded: responses.EmbeddedTerms | None = Field(default=None, alias="_embedded")
