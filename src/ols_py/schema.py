import marshmallow
from marshmallow import fields


class LinkSchema(marshmallow.Schema):
    href = fields.Url()


class BaseLinksSchema(marshmallow.Schema):
    ontologies = fields.Nested(LinkSchema)
    individuals = fields.Nested(LinkSchema)
    terms = fields.Nested(LinkSchema)
    properties = fields.Nested(LinkSchema)
    profile = fields.Nested(LinkSchema)


class ApiBaseSchema(marshmallow.Schema):
    links = fields.Nested(BaseLinksSchema, data_key="_links")


class OlsErrorSchema(marshmallow.Schema):
    """
    Error data returned the OLS API for a bad request/error
    """

    error = fields.String()
    message = fields.String()
    path = fields.String()
    status = fields.Integer()
    timestamp = fields.Number()
