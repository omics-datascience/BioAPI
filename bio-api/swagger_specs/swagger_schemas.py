from flask_marshmallow import Schema
from marshmallow import fields, validate


class GeneSymbolsRequestSchema(Schema):
    gene_ids = fields.List(fields.String(),
                           description="List of valid genes identifiers",
                           required=True,
                           example=["FANCS", "BRCC1"])     


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


class InformationOfGenesRequestSchema(Schema):
    gene_ids = fields.List(fields.String(),
                           description="List of valid genes identifiers",
                           required=True,
                           example=["TP53", "MC1R"])


class PathwaysInCommonRequestSchema(Schema):
    gene_ids = fields.List(fields.String(),
                           description="List of valid genes identifiers",
                           required=True,
                           example=["HLA-B", "BRAF"])
    

class ExpressionOfGenesRequestSchema(Schema):
    gene_ids = fields.List(fields.String(),
                           description="List of valid genes identifiers",
                           required=True,
                           example=["BRCA1", "BRCA2"])
    tissue = fields.String(description="Healthy tissue from which you want to get the expression values.",
                           required=True, example="Skin",
                           validate=validate.OneOf(["Adipose Tissue", "Adrenal Gland", "Bladder", "Blood", "Blood Vessel", "Brain", "Breast", "Cervix Uteri", "Colon", "Esophagus", "Fallopian Tube", "Heart", "Kidney", "Liver", "Lung", "Muscle", "Nerve", "Ovary", "Pancreas", "Pituitary", "Prostate", "Salivary Gland", "Skin", "Small Intestine", "Spleen", "Stomach", "Testis", "Thyroid", "Uterus", "Vagina"]))
    type = fields.String(description="Type of response format: json or gzip. Default: json",
                         required=False, missing="json", validate=validate.OneOf(["json", "gzip"]))


class GenesToTermsRequestSchema(Schema):
    gene_ids = fields.List(fields.String(),
                           description="List of genes for which you want to get the terms in common",
                           required=True,
                           example=["TMCO4"])
    filter_type = fields.String(description="Type of flter: intersection, union or enrichment",
                                required=False, example="intersection", validate=validate.OneOf(["intersection", "union", "enrichment"]))
    p_value_threshold = fields.Float(description="Just for enrichment filter: It's the p-value threshold. Not recommended to set it higher than 0.05.", dump_only=True, required=False, example=0.05 )
    correction_method = fields.String(description="Just for enrichment filter: The enrichment default correction method is analytical. Alternatively, one may select bonferroni correction or false_discovery_rate (Benjamini-Hochberg FDR).",
                                      required=False, example="analytical", dump_only=True, validate=validate.OneOf(["analytical", "bonferroni", "false_discovery_rate"]))
    relation_type = fields.List(fields.String(),
                                description="Filters the relation between genes and terms. By default it's ['enables','involved_in','part_of','located_in']. It should always be a list containing any permutation of the allowed relations. Only valid on filter_type intersection and union.",
                                required=False,
                                example=['enables', 'involved_in', 'part_of', 'located_in'])
    ontology_type = fields.List(fields.String(),
                                description="Filters the ontology type of the terms in the response. By default it's ['biological_process', 'molecular_function', 'cellular_component']. It should always be a list containing any permutation of the 3 ontologies.",
                                required=False,
                                example=['biological_process', 'molecular_function', 'cellular_component'])


class InformationOfOncokbRequestSchema(Schema):
    gene_ids = fields.List(fields.String(),
                           description="Llist of genes for which you want to get the information from the OncoKB database",
                           required=True,
                           example=["HLA-B", "BRAF"])
    query = fields.String(description="Parameter used to show only the results that match it", required=False, missing="")
