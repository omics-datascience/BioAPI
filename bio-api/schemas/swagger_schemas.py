from marshmallow import Schema, fields


class GeneSymbolsRequestSchema(Schema):
    gene_ids = fields.List(fields.String(), required=True, example=["FANCS", "BRCC1"])


class GeneSymbolsFinderRequestSchema(Schema):
    query = fields.String(
        required=True,
        description="gene search string",
        example="TP"
    )
    limit = fields.Integer(
        missing=50,
        description="number of elements returned by the service. Default 50."
    )
