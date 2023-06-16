from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Extra, Field

from ..schemas import responses
from ..schemas.common import EntityType


# Structure of search results has changed from OLS v3,
#   some fields are now list[str] instead of str
class SearchResultItem(BaseModel, extra=Extra.allow):
    id: Optional[str]
    annotations: Optional[list[str]]
    annotations_trimmed: Optional[list[str]]
    description: Optional[list[str]]
    iri: Optional[str]
    label: Optional[list[str]]
    obo_id: Optional[list[str]]
    ontology_name: Optional[str]
    ontology_prefix: Optional[str]
    subset: Optional[list[str]]
    short_form: Optional[list[str]]
    synonym: Optional[list[str]]
    type: Optional[EntityType]


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
