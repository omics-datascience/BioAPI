from __future__ import annotations

from typing import Literal, NotRequired, Sequence, TypeAlias, TypedDict, cast
from urllib.parse import quote

import requests

from .utils import DEFAULT_BASE_URL, get_api_response, post_api_response


PathwaySource: TypeAlias = Literal[
    "kegg",
    "biocarta",
    "ehmn",
    "humancyc",
    "inoh",
    "netpath",
    "pid",
    "reactome",
    "smpdb",
    "signalink",
    "wikipathways",
]
ExpressionResponseFormat: TypeAlias = Literal["json", "gzip"]
GeneTermsFilterType: TypeAlias = Literal["intersection", "union", "enrichment"]
GeneTermRelationType: TypeAlias = Literal[
    "enables",
    "involved_in",
    "part_of",
    "located_in",
]
OntologyType: TypeAlias = Literal[
    "biological_process",
    "molecular_function",
    "cellular_component",
]
TermRelationType: TypeAlias = Literal["part_of", "regulates", "has_part"]
CorrectionMethod: TypeAlias = Literal[
    "analytical",
    "bonferroni",
    "false_discovery_rate",
]
GeneSymbolsResponse: TypeAlias = dict[str, list[str]]


class GeneInformation(TypedDict, total=False):
    alias_symbol: str | list[str]
    percentage_gene_gc_content: float
    oncokb_cancer_gene: str
    name: str
    band: str
    chromosome: str
    start_position: int
    end_position: int
    start_GRCh37: int
    end_GRCh37: int
    strand: int
    gene_biotype: str
    refseq_summary: str
    civic_description: str
    hgnc_id: str
    uniprot_ids: str | list[str]
    omim_id: str | list[str]
    ensembl_gene_id: str
    entrez_id: str


GeneInformationResponse: TypeAlias = dict[str, GeneInformation]


class GeneGroup(TypedDict, total=False):
    gene_group: str
    gene_group_id: str | int
    genes: list[str]


class GeneGroupResponse(TypedDict):
    gene_id: str | None
    groups: list[GeneGroup]
    locus_group: str | None
    locus_type: str | None


class PathwayGenesResponse(TypedDict):
    genes: list[str]


class Pathway(TypedDict):
    source: str
    external_id: str
    pathway: str


class PathwaysInCommonResponse(TypedDict):
    pathways: list[Pathway]


ExpressionValue: TypeAlias = int | float
GeneExpressionResponse: TypeAlias = dict[str, list[ExpressionValue] | list[str]]


class OncoKBEvidence(TypedDict, total=False):
    drugs: str
    level_of_evidence: str
    alterations: str
    cancer_types: str


class OncoKBPrecisionTherapy(TypedDict, total=False):
    precision_oncology_therapy: str
    fda_first_approval: str
    drug_classification: str
    fda_recognized_biomarkers: str
    method_of_biomarker_detection: str


class OncoKBGeneInformation(TypedDict, total=False):
    therapeutic: list[OncoKBEvidence]
    diagnostic: list[OncoKBEvidence]
    prognostic: list[OncoKBEvidence]
    oncokb_cancer_gene: list[str]
    refseq_transcript: str
    sources: list[str]
    precision_therapies: list[OncoKBPrecisionTherapy]


OncoKBInformationResponse: TypeAlias = dict[str, OncoKBGeneInformation]


class GeneTermRelation(TypedDict, total=False):
    gene: str
    relation_type: str
    evidence: str


class EnrichmentMetrics(TypedDict, total=False):
    p_value: float
    intersection_size: int
    effective_domain_size: int
    query_size: int
    term_size: int
    precision: float
    recall: float


class GeneOntologyTerm(TypedDict, total=False):
    go_id: str
    name: str
    ontology_type: str
    definition: str
    synonyms: list[str]
    subset: list[str]
    is_a: str | list[str]
    alt_id: str | list[str]
    synonym: list[str]
    definition_reference: str | list[str]
    relations_to_genes: list[GeneTermRelation]
    enrichment_metrics: EnrichmentMetrics


class RelatedTerm(TypedDict):
    go_id: str
    name: str
    ontology_type: str
    relations: dict[str, list[str]]


class PharmGKBDrugLabel(TypedDict, total=False):
    pharmgkb_id: str
    name: str
    source: str
    biomarker_flag: str
    testing_level: str
    chemicals: str
    genes: list[str]
    variants_haplotypes: str


PharmGKBDrugsResponse: TypeAlias = dict[str, list[PharmGKBDrugLabel]]


class StringRelation(TypedDict):
    gene_1: str
    gene_2: str
    neighborhood_transferred: NotRequired[int | None]
    fusion: NotRequired[int | None]
    cooccurence: NotRequired[int | None]
    homology: NotRequired[int | None]
    coexpression: NotRequired[int | None]
    coexpression_transferred: NotRequired[int | None]
    experiments: NotRequired[int | None]
    experiments_transferred: NotRequired[int | None]
    database: NotRequired[int | None]
    database_transferred: NotRequired[int | None]
    textmining: NotRequired[int | None]
    textmining_transferred: NotRequired[int | None]
    combined_score: int


class DrugBankGeneRegulationResponse(TypedDict):
    link: str


def _quote_path_segment(value: str) -> str:
    """Return a URL-safe BioAPI path segment.

    :param value: Raw path segment value.
    :returns: Percent-encoded path segment.
    """
    return quote(value, safe="")


def gene_symbols(
    gene_ids: Sequence[str],
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> GeneSymbolsResponse:
    """Validate gene identifiers and return HGNC-approved symbols.

    :param gene_ids: Gene identifiers to validate against HGNC nomenclature.
    :param base_url: Base BioAPI URL.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` used to send the request.
    :returns: Mapping from each submitted identifier to matching symbols.
    """
    return cast(
        GeneSymbolsResponse,
        post_api_response(
            "/gene-symbols",
            body={"gene_ids": list(gene_ids)},
            base_url=base_url,
            timeout=timeout,
            session=session,
        ),
    )


def gene_symbols_finder(
    query: str,
    *,
    limit: int = 50,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> list[str]:
    """Find gene symbols that contain the given search text.

    :param query: Gene search string.
    :param limit: Maximum number of results to return.
    :param base_url: Base BioAPI URL.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` used to send the request.
    :returns: Gene symbols matching the search criteria.
    """
    return cast(
        list[str],
        get_api_response(
            "/gene-symbols-finder/",
            params={"query": query, "limit": limit},
            base_url=base_url,
            timeout=timeout,
            session=session,
        ),
    )


def information_of_genes(
    gene_ids: Sequence[str],
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> GeneInformationResponse:
    """Return genomic and database information for valid genes.

    :param gene_ids: Valid gene identifiers to query.
    :param base_url: Base BioAPI URL.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` used to send the request.
    :returns: Mapping from gene symbol to available gene information.
    """
    return cast(
        GeneInformationResponse,
        post_api_response(
            "/information-of-genes",
            body={"gene_ids": list(gene_ids)},
            base_url=base_url,
            timeout=timeout,
            session=session,
        ),
    )


def genes_of_its_group(
    gene_id: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> GeneGroupResponse:
    """Return HGNC group information for a gene identifier.

    :param gene_id: Gene identifier from any supported database.
    :param base_url: Base BioAPI URL.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` used to send the request.
    :returns: Approved symbol, locus metadata, and matching HGNC groups.
    """
    endpoint = f"/genes-of-its-group/{_quote_path_segment(gene_id)}"
    return cast(
        GeneGroupResponse,
        get_api_response(
            endpoint,
            base_url=base_url,
            timeout=timeout,
            session=session,
        ),
    )


def pathway_genes(
    source: PathwaySource,
    external_id: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> PathwayGenesResponse:
    """Return genes involved in a metabolic pathway.

    :param source: Lowercase pathway database source.
    :param external_id: Pathway identifier in the source database.
    :param base_url: Base BioAPI URL.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` used to send the request.
    :returns: Genes involved in the requested pathway.
    """
    endpoint = (
        f"/pathway-genes/{_quote_path_segment(source)}/"
        f"{_quote_path_segment(external_id)}"
    )
    return cast(
        PathwayGenesResponse,
        get_api_response(
            endpoint,
            base_url=base_url,
            timeout=timeout,
            session=session,
        ),
    )


def pathways_in_common(
    gene_ids: Sequence[str],
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> PathwaysInCommonResponse:
    """Return pathways common to all submitted genes.

    :param gene_ids: Genes used to compute the pathway intersection.
    :param base_url: Base BioAPI URL.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` used to send the request.
    :returns: Common pathway records.
    """
    return cast(
        PathwaysInCommonResponse,
        post_api_response(
            "/pathways-in-common",
            body={"gene_ids": list(gene_ids)},
            base_url=base_url,
            timeout=timeout,
            session=session,
        ),
    )


def expression_of_genes(
    gene_ids: Sequence[str],
    tissue: str,
    *,
    response_format: ExpressionResponseFormat = "json",
    samples: bool = False,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> GeneExpressionResponse:
    """Return GTEx expression values for genes in a healthy tissue.

    :param gene_ids: Genes for which expression values are requested.
    :param tissue: Healthy tissue name accepted by BioAPI.
    :param response_format: BioAPI response type, mapped to the ``type`` body key.
    :param samples: Include GTEx sample identifiers when true.
    :param base_url: Base BioAPI URL.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` used to send the request.
    :returns: Mapping from genes to expression values, with optional samples.
    """
    return cast(
        GeneExpressionResponse,
        post_api_response(
            "/expression-of-genes",
            body={
                "gene_ids": list(gene_ids),
                "tissue": tissue,
                "type": response_format,
                "samples": samples,
            },
            base_url=base_url,
            timeout=timeout,
            session=session,
        ),
    )


def information_of_oncokb(
    gene_ids: Sequence[str],
    *,
    query: str | None = None,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> OncoKBInformationResponse:
    """Return OncoKB cancer evidence and precision therapy data.

    :param gene_ids: Genes for which OncoKB information is requested.
    :param query: Optional filter applied to OncoKB text fields.
    :param base_url: Base BioAPI URL.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` used to send the request.
    :returns: Mapping from gene symbol to available OncoKB information.
    """
    body: dict[str, object] = {"gene_ids": list(gene_ids)}
    if query is not None:
        body["query"] = query

    return cast(
        OncoKBInformationResponse,
        post_api_response(
            "/information-of-oncokb",
            body=body,
            base_url=base_url,
            timeout=timeout,
            session=session,
        ),
    )


def genes_to_terms(
    gene_ids: Sequence[str],
    *,
    filter_type: GeneTermsFilterType = "intersection",
    relation_type: Sequence[GeneTermRelationType] | None = None,
    ontology_type: Sequence[OntologyType] | None = None,
    p_value_threshold: float | None = None,
    correction_method: CorrectionMethod | None = None,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> list[GeneOntologyTerm]:
    """Return Gene Ontology terms related to submitted genes.

    :param gene_ids: HGNC gene symbols to query.
    :param filter_type: Term filter mode: intersection, union, or enrichment.
    :param relation_type: Optional gene-to-term relation filters.
    :param ontology_type: Optional ontology filters.
    :param p_value_threshold: Enrichment p-value threshold.
    :param correction_method: Enrichment correction method.
    :param base_url: Base BioAPI URL.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` used to send the request.
    :returns: Gene Ontology term records matching the filters.
    """
    body: dict[str, object] = {
        "gene_ids": list(gene_ids),
        "filter_type": filter_type,
    }
    if relation_type is not None:
        body["relation_type"] = list(relation_type)
    if ontology_type is not None:
        body["ontology_type"] = list(ontology_type)
    if p_value_threshold is not None:
        body["p_value_threshold"] = p_value_threshold
    if correction_method is not None:
        body["correction_method"] = correction_method

    return cast(
        list[GeneOntologyTerm],
        post_api_response(
            "/genes-to-terms",
            body=body,
            base_url=base_url,
            timeout=timeout,
            session=session,
        ),
    )


def related_terms(
    term_id: str,
    *,
    relations: Sequence[TermRelationType] | None = None,
    ontology_type: Sequence[OntologyType] | None = None,
    general_depth: int | None = None,
    hierarchical_depth_to_children: int | None = None,
    to_root: bool | None = None,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> list[RelatedTerm]:
    """Return Gene Ontology terms related to a specific term.

    :param term_id: GO term identifier without the ``GO:`` prefix.
    :param relations: Optional non-hierarchical relation filters.
    :param ontology_type: Optional ontology filters.
    :param general_depth: Search depth for non-hierarchical relations.
    :param hierarchical_depth_to_children: Search depth toward child terms.
    :param to_root: Include hierarchical terms toward the root when true.
    :param base_url: Base BioAPI URL.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` used to send the request.
    :returns: Related GO term records.
    """
    body: dict[str, object] = {"term_id": term_id}
    if relations is not None:
        body["relations"] = list(relations)
    if ontology_type is not None:
        body["ontology_type"] = list(ontology_type)
    if general_depth is not None:
        body["general_depth"] = general_depth
    if hierarchical_depth_to_children is not None:
        body["hierarchical_depth_to_children"] = hierarchical_depth_to_children
    if to_root is not None:
        body["to_root"] = to_root

    return cast(
        list[RelatedTerm],
        post_api_response(
            "/related-terms",
            body=body,
            base_url=base_url,
            timeout=timeout,
            session=session,
        ),
    )


def drugs_pharm_gkb(
    gene_ids: Sequence[str],
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> PharmGKBDrugsResponse:
    """Return PharmGKB cancer-related drug labels for genes.

    :param gene_ids: Genes for which related drug labels are requested.
    :param base_url: Base BioAPI URL.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` used to send the request.
    :returns: Mapping from gene symbol to PharmGKB drug label records.
    """
    return cast(
        PharmGKBDrugsResponse,
        post_api_response(
            "/drugs-pharm-gkb",
            body={"gene_ids": list(gene_ids)},
            base_url=base_url,
            timeout=timeout,
            session=session,
        ),
    )


def string_relations(
    gene_id: str,
    *,
    min_combined_score: int | None = None,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> list[StringRelation]:
    """Return STRING functional association relations for a gene.

    :param gene_id: Target gene symbol.
    :param min_combined_score: Optional minimum combined score from 1 to 1000.
    :param base_url: Base BioAPI URL.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` used to send the request.
    :returns: STRING relations containing the target gene.
    """
    body: dict[str, object] = {"gene_id": gene_id}
    if min_combined_score is not None:
        body["min_combined_score"] = min_combined_score

    return cast(
        list[StringRelation],
        post_api_response(
            "/string-relations",
            body=body,
            base_url=base_url,
            timeout=timeout,
            session=session,
        ),
    )


def drugs_regulating_gene(
    gene_id: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> DrugBankGeneRegulationResponse:
    """Return a DrugBank link for drugs that regulate a gene.

    :param gene_id: Gene symbol to search on DrugBank.
    :param base_url: Base BioAPI URL.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` used to send the request.
    :returns: Dictionary containing the DrugBank transcriptomics link.
    """
    endpoint = f"/drugs-regulating-gene/{_quote_path_segment(gene_id)}"
    return cast(
        DrugBankGeneRegulationResponse,
        get_api_response(
            endpoint,
            base_url=base_url,
            timeout=timeout,
            session=session,
        ),
    )


__all__: list[str] = [
    "CorrectionMethod",
    "DrugBankGeneRegulationResponse",
    "EnrichmentMetrics",
    "ExpressionResponseFormat",
    "ExpressionValue",
    "GeneExpressionResponse",
    "GeneGroup",
    "GeneGroupResponse",
    "GeneInformation",
    "GeneInformationResponse",
    "GeneOntologyTerm",
    "GeneSymbolsResponse",
    "GeneTermRelation",
    "GeneTermRelationType",
    "GeneTermsFilterType",
    "OncoKBEvidence",
    "OncoKBGeneInformation",
    "OncoKBInformationResponse",
    "OncoKBPrecisionTherapy",
    "OntologyType",
    "Pathway",
    "PathwayGenesResponse",
    "PathwaySource",
    "PathwaysInCommonResponse",
    "PharmGKBDrugLabel",
    "PharmGKBDrugsResponse",
    "RelatedTerm",
    "StringRelation",
    "TermRelationType",
    "drugs_pharm_gkb",
    "drugs_regulating_gene",
    "expression_of_genes",
    "gene_symbols",
    "gene_symbols_finder",
    "genes_of_its_group",
    "genes_to_terms",
    "information_of_genes",
    "information_of_oncokb",
    "pathway_genes",
    "pathways_in_common",
    "related_terms",
    "string_relations",
]
