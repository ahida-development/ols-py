import typing

from pydantic import BaseModel, Field, HttpUrl


class Link(BaseModel):
    href: HttpUrl


class RootLinks(BaseModel):
    ontologies: list[Link]
    individuals: list[Link]
    terms: list[Link]
    properties: list[Link]
    profile = list[Link]


class ApiRoot(BaseModel):
    links: RootLinks = Field(None, alias="_links")


class OlsErrorSchema(BaseModel):
    """
    Error data returned the OLS API for a bad request/error
    """

    error: str
    message: str
    path: str
    status: int
    timestamp: typing.Union[int, float]
