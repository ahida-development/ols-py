from __future__ import annotations

from typing import Optional

from pydantic import AliasChoices, BaseModel, Field

from ..schemas.common import EntityType


# Structure of search results has changed from OLS v3,
#   some fields are now list[str] instead of str
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
    # OLS4 has recently switched to "synonyms" for this field,
    #   where OLS3 has "synonym"
    synonyms: Optional[list[str]] = Field(
        default=None, validation_alias=AliasChoices("synonyms", "synonym")
    )
    type: Optional[EntityType] = None


class SearchResponseResponse(BaseModel):
    docs: list[SearchResultItem]


class SearchResponse(BaseModel):
    responseHeader: dict
    response: SearchResponseResponse
