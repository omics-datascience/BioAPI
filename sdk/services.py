from typing import Literal, NotRequired, Sequence, TypeAlias, TypedDict, cast
from urllib.parse import quote

import requests

from .utils import get_api_response, post_api_response, DEFAULT_BASE_URL



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
    """Alternative symbols for a known gene."""
    percentage_gene_gc_content: float
    """Ratio of guanine and cytosine nucleotides in the gene DNA sequence."""
    oncokb_cancer_gene: str
    """Oncogene or Tumor Suppressor Gene when present in the OncoKB database."""
    name: str
    """Gene name according to the HGNC database."""
    band: str
    """Cytoband or specific location in the genome."""
    chromosome: str
    """Chromosome where the gene is located, without the chr prefix."""
    start_position: int
    """Chromosomal position where the gene starts in reference genome GRCh38."""
    end_position: int
    """Chromosomal position where the gene ends in reference genome GRCh38."""
    start_GRCh37: int
    """Chromosomal position where the gene starts in reference genome GRCh37."""
    end_GRCh37: int
    """Chromosomal position where the gene ends in reference genome GRCh37."""
    strand: int
    """DNA strand containing the coding sequence: 1 positive or -1 negative."""
    gene_biotype: str
    """Gene or transcript classification, such as protein_coding or miRNA."""
    refseq_summary: str
    """Complete gene description according to the RefSeq database."""
    civic_description: str
    """Description of clinical relevance according to the CIViC database."""
    hgnc_id: str
    """Gene identifier in the HGNC database."""
    uniprot_ids: str | list[str]
    """Gene identifier or identifiers in the Uniprot database."""
    omim_id: str | list[str]
    """Gene identifier or identifiers in the OMIM database."""
    ensembl_gene_id: str
    """Gene identifier in the Ensembl database."""
    entrez_id: str
    """Gene identifier in the NCBI Entrez database."""


GeneInformationResponse: TypeAlias = dict[str, GeneInformation]


class GeneGroup(TypedDict, total=False):
    gene_group: str
    """Gene group name."""
    gene_group_id: str | int
    """Gene group identifier."""
    genes: list[str]
    """All other genes for this group."""


class GeneGroupResponse(TypedDict):
    gene_id: str | None
    """HGNC approved gene symbol."""
    groups: list[GeneGroup]
    """HGNC gene groups to which the approved gene belongs."""
    locus_group: str | None
    """
    Related locus type set, such as protein-coding gene, pseudogene,
    phenotype, or other.
    """
    locus_type: str | None
    """Genetic class of the gene entry according to HGNC."""


class PathwayGenesResponse(TypedDict):
    genes: list[str]
    """Genes involved in the metabolic pathway."""


class Pathway(TypedDict):
    source: str
    """Database of the metabolic pathway found."""
    external_id: str
    """Pathway identifier in the source database."""
    pathway: str
    """Name of the pathway."""


class PathwaysInCommonResponse(TypedDict):
    pathways: list[Pathway]
    """Metabolic pathways common to the submitted genes."""


ExpressionValue: TypeAlias = int | float
GeneExpressionResponse: TypeAlias = dict[str, list[ExpressionValue] | list[str]]


class OncoKBEvidence(TypedDict, total=False):
    drugs: str
    """Therapeutic drug or drugs associated with the evidence."""
    level_of_evidence: str
    """OncoKB evidence level for a therapeutic, diagnostic, or prognostic assertion."""
    alterations: str
    """Specific cancer gene alterations."""
    cancer_types: str
    """Cancer types using the OncoTree nomenclature."""


class OncoKBPrecisionTherapy(TypedDict, total=False):
    precision_oncology_therapy: str
    """
    Drug most effective in a molecularly defined subset of patients where
    pre-treatment molecular profiling is required for selection.
    """
    fda_first_approval: str
    """Year of the drug's first FDA approval in any indication."""
    drug_classification: str
    """
    Drug class based on OncoKB precision oncology therapy categories, such as
    first-in-class, mechanistically-distinct, follow-on, or resistance.
    """
    fda_recognized_biomarkers: str
    """
    Biomarkers related to the therapy according to the FDA, including
    pathognomonic and indication-specific biomarkers.
    """
    method_of_biomarker_detection: str
    """Biomarker detection method, including companion diagnostic details."""


class OncoKBGeneInformation(TypedDict, total=False):
    therapeutic: list[OncoKBEvidence]
    """Therapeutic evidence records for the gene."""
    diagnostic: list[OncoKBEvidence]
    """Diagnostic evidence records for the gene in hematologic malignancies."""
    prognostic: list[OncoKBEvidence]
    """Prognostic evidence records for the gene in hematologic malignancies."""
    oncokb_cancer_gene: list[str]
    """Cancer gene classification: Oncogene and/or Tumor Suppressor Gene."""
    refseq_transcript: str
    """Gene transcript according to the RefSeq database."""
    sources: list[str]
    """Sources with evidence of the gene's relationship with cancer."""
    precision_therapies: list[OncoKBPrecisionTherapy]
    """FDA-approved therapies considered precision oncology therapies by OncoKB."""


OncoKBInformationResponse: TypeAlias = dict[str, OncoKBGeneInformation]


class GeneTermRelation(TypedDict, total=False):
    gene: str
    """Name of the gene."""
    relation_type: str
    """Type of relation between the gene and the Gene Ontology term."""
    evidence: str
    """Evidence code indicating how the annotation to the term is supported."""


class EnrichmentMetrics(TypedDict, total=False):
    p_value: float
    """Hypergeometric p-value after correction for multiple testing."""
    intersection_size: int
    """Number of genes in the query annotated to the corresponding term."""
    effective_domain_size: int
    """
    Total number of genes in the universe used for the hypergeometric
    probability function of statistical significance.
    """
    query_size: int
    """Number of genes included in the query."""
    term_size: int
    """Number of genes annotated to the term."""
    precision: float
    """Proportion of input genes annotated to the function."""
    recall: float
    """Proportion of functionally annotated genes recovered by the query."""


class GeneOntologyTerm(TypedDict, total=False):
    go_id: str
    """Unique Gene Ontology identifier."""
    name: str
    """Human-readable term name."""
    ontology_type: str
    """
    Sub-ontology to which the term belongs: biological_process,
    molecular_function, or cellular_component.
    """
    definition: str
    """Textual description of what the term represents, plus source references."""
    synonyms: list[str]
    """
    Alternative words or phrases closely related to the term name, with
    synonym scope.
    """
    subset: list[str]
    """Additional ontology categorization for grouping related terms."""
    is_a: str | list[str]
    """Semantic relationship indicating a subtype of a more general term."""
    alt_id: str | list[str]
    """Alternative or secondary identifiers for the ontology term."""
    synonym: list[str]
    """Alternative words or phrases closely related in meaning to the term name."""
    definition_reference: str | list[str]
    """Bibliographic references or sources for the term definition."""
    relations_to_genes: list[GeneTermRelation]
    """Gene-to-term relation records for this Gene Ontology term."""
    enrichment_metrics: EnrichmentMetrics
    """Enrichment metrics returned for gene enrichment analysis."""


class RelatedTerm(TypedDict):
    go_id: str
    """ID of the Gene Ontology term."""
    name: str
    """Name of the Gene Ontology term."""
    ontology_type: str
    """
    Sub-ontology to which the term belongs: cellular_component,
    biological_process, or molecular_function.
    """
    relations: dict[str, list[str]]
    """Relation names mapped to lists of related Gene Ontology identifiers."""


class PharmGKBDrugLabel(TypedDict, total=False):
    pharmgkb_id: str
    """Identifier assigned to this drug label by PharmGKB."""
    name: str
    """Name assigned to the label by PharmGKB."""
    source: str
    """Source that originally authored the label, such as EMA, FDA, HCSC, or PMDA."""
    biomarker_flag: str
    """Whether the drug label appears on the FDA Biomarker list."""
    testing_level: str
    """PGx testing level as annotated by PharmGKB."""
    chemicals: str
    """Related chemicals."""
    genes: list[str]
    """Related genes."""
    variants_haplotypes: str
    """Related variants and/or haplotypes."""


PharmGKBDrugsResponse: TypeAlias = dict[str, list[PharmGKBDrugLabel]]


class StringRelation(TypedDict):
    gene_1: str
    """First gene in the bidirectional relationship."""
    gene_2: str
    """Second gene in the bidirectional relationship."""
    neighborhood_transferred: NotRequired[int | None]
    """Score for neighborhood evidence transferred from other organisms."""
    fusion: NotRequired[int | None]
    """Score derived from fused proteins in other species."""
    cooccurence: NotRequired[int | None]
    """Score derived from similar absence or presence patterns across species."""
    homology: NotRequired[int | None]
    """Score measuring homology between the protein interaction partners."""
    coexpression: NotRequired[int | None]
    """Score measuring coexpression of two genes."""
    coexpression_transferred: NotRequired[int | None]
    """Coexpression score transferred from other species based on homology."""
    experiments: NotRequired[int | None]
    """Score representing protein interaction confidence from experimental evidence."""
    experiments_transferred: NotRequired[int | None]
    """Experimental evidence score transferred from other species based on homology."""
    database: NotRequired[int | None]
    """Score derived from curated database evidence."""
    database_transferred: NotRequired[int | None]
    """Curated database evidence score transferred from other species based on homology."""
    textmining: NotRequired[int | None]
    """Score derived from co-occurrence of gene or protein names in publications."""
    textmining_transferred: NotRequired[int | None]
    """Text-mining score transferred from other species based on homology."""
    combined_score: int
    """Confidence score combining all evidence channels."""


class DrugBankGeneRegulationResponse(TypedDict):
    link: str
    """URL pointing to gene regulation information on the DrugBank website."""


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
