from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

import requests
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from . import services
from .services import (
    CorrectionMethod,
    ExpressionResponseFormat,
    GeneTermRelationType,
    GeneTermsFilterType,
    OntologyType,
    PathwaySource,
    TermRelationType,
)
from .utils import BioAPIRequestError, DEFAULT_BASE_URL


DEFAULT_TIMEOUT = 30.0

mcp = FastMCP(
    "BioAPI",
    instructions=(
        "Use BioAPI to query human gene nomenclature, gene information, "
        "metabolic pathways, GTEx expression, OncoKB, Gene Ontology, "
        "PharmGKB, STRING, and DrugBank links. Tools call the bioapi-sdk "
        "package and return BioAPI JSON responses."
    ),
)


def _resolve_base_url(base_url: str | None) -> str:
    if base_url is None or base_url.strip() == "":
        return DEFAULT_BASE_URL
    return base_url.strip()


def _resolve_timeout(timeout: float | None) -> float:
    if timeout is None:
        timeout_from_env = os.getenv("BIOAPI_TIMEOUT")
        if timeout_from_env is None or timeout_from_env.strip() == "":
            resolved_timeout = DEFAULT_TIMEOUT
        else:
            try:
                resolved_timeout = float(timeout_from_env)
            except ValueError as exc:
                raise ToolError("BIOAPI_TIMEOUT must be a number of seconds.") from exc
    else:
        resolved_timeout = timeout

    if resolved_timeout <= 0:
        raise ToolError("timeout must be greater than 0 seconds.")
    return resolved_timeout


def _format_api_error(exc: BioAPIRequestError) -> str:
    details: list[str] = [str(exc)]
    if exc.status_code is not None:
        details.append(f"status={exc.status_code}")
    if exc.url is not None:
        details.append(f"url={exc.url}")
    return "BioAPI request failed: " + " | ".join(details)


def _call_bioapi(
    operation: Callable[..., Any],
    /,
    *args: Any,
    base_url: str | None = None,
    timeout: float | None = None,
    **kwargs: Any,
) -> Any:
    try:
        return operation(
            *args,
            base_url=_resolve_base_url(base_url),
            timeout=_resolve_timeout(timeout),
            **kwargs,
        )
    except BioAPIRequestError as exc:
        raise ToolError(_format_api_error(exc)) from exc
    except requests.RequestException as exc:
        raise ToolError(f"BioAPI request failed: {exc}") from exc


@mcp.tool()
def validate_gene_symbols(
    gene_ids: list[str],
    base_url: str | None = None,
    timeout: float | None = None,
) -> dict[str, list[str]]:
    """Validate gene identifiers and return HGNC-approved symbols.

    Use this before downstream tools when identifiers may be aliases, Ensembl
    IDs, Entrez IDs, or other supported nomenclature.
    """
    return _call_bioapi(
        services.gene_symbols,
        gene_ids,
        base_url=base_url,
        timeout=timeout,
    )


@mcp.tool()
def find_gene_symbols(
    query: str,
    limit: int = 50,
    base_url: str | None = None,
    timeout: float | None = None,
) -> list[str]:
    """Find HGNC gene symbols that contain a search string."""
    return _call_bioapi(
        services.gene_symbols_finder,
        query,
        limit=limit,
        base_url=base_url,
        timeout=timeout,
    )


@mcp.tool()
def get_gene_information(
    gene_ids: list[str],
    base_url: str | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    """Return genomic and database annotations for valid genes."""
    return _call_bioapi(
        services.information_of_genes,
        gene_ids,
        base_url=base_url,
        timeout=timeout,
    )


@mcp.tool()
def get_gene_group(
    gene_id: str,
    base_url: str | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    """Return HGNC group, locus group, and locus type for one gene."""
    return _call_bioapi(
        services.genes_of_its_group,
        gene_id,
        base_url=base_url,
        timeout=timeout,
    )


@mcp.tool()
def get_pathway_genes(
    source: PathwaySource,
    external_id: str,
    base_url: str | None = None,
    timeout: float | None = None,
) -> dict[str, list[str]]:
    """Return genes involved in a metabolic pathway from a supported source."""
    return _call_bioapi(
        services.pathway_genes,
        source,
        external_id,
        base_url=base_url,
        timeout=timeout,
    )


@mcp.tool()
def find_common_pathways(
    gene_ids: list[str],
    base_url: str | None = None,
    timeout: float | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Return metabolic pathways common to all submitted genes."""
    return _call_bioapi(
        services.pathways_in_common,
        gene_ids,
        base_url=base_url,
        timeout=timeout,
    )


@mcp.tool()
def get_gene_expression(
    gene_ids: list[str],
    tissue: str,
    response_format: ExpressionResponseFormat = "json",
    samples: bool = False,
    base_url: str | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    """Return GTEx expression values for genes in a healthy tissue.

    Keep response_format as "json" for LLM-readable responses. Set samples to
    true to include GTEx sample identifiers when BioAPI supports them.
    """
    return _call_bioapi(
        services.expression_of_genes,
        gene_ids,
        tissue,
        response_format=response_format,
        samples=samples,
        base_url=base_url,
        timeout=timeout,
    )


@mcp.tool()
def get_oncokb_information(
    gene_ids: list[str],
    query: str | None = None,
    base_url: str | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    """Return OncoKB cancer evidence and precision therapy data for genes."""
    return _call_bioapi(
        services.information_of_oncokb,
        gene_ids,
        query=query,
        base_url=base_url,
        timeout=timeout,
    )


@mcp.tool()
def get_gene_ontology_terms(
    gene_ids: list[str],
    filter_type: GeneTermsFilterType = "intersection",
    relation_type: list[GeneTermRelationType] | None = None,
    ontology_type: list[OntologyType] | None = None,
    p_value_threshold: float | None = None,
    correction_method: CorrectionMethod | None = None,
    base_url: str | None = None,
    timeout: float | None = None,
) -> list[dict[str, Any]]:
    """Return Gene Ontology terms related to submitted genes.

    Use filter_type="enrichment" for enrichment analysis. For enrichment,
    relation_type is ignored by BioAPI and all available relations are used.
    """
    return _call_bioapi(
        services.genes_to_terms,
        gene_ids,
        filter_type=filter_type,
        relation_type=relation_type,
        ontology_type=ontology_type,
        p_value_threshold=p_value_threshold,
        correction_method=correction_method,
        base_url=base_url,
        timeout=timeout,
    )


@mcp.tool()
def get_related_gene_ontology_terms(
    term_id: str,
    relations: list[TermRelationType] | None = None,
    ontology_type: list[OntologyType] | None = None,
    general_depth: int | None = None,
    hierarchical_depth_to_children: int | None = None,
    to_root: bool | None = None,
    base_url: str | None = None,
    timeout: float | None = None,
) -> list[dict[str, Any]]:
    """Return Gene Ontology terms related to a specific GO term.

    term_id should be the numeric GO identifier without the "GO:" prefix.
    """
    return _call_bioapi(
        services.related_terms,
        term_id,
        relations=relations,
        ontology_type=ontology_type,
        general_depth=general_depth,
        hierarchical_depth_to_children=hierarchical_depth_to_children,
        to_root=to_root,
        base_url=base_url,
        timeout=timeout,
    )


@mcp.tool()
def get_pharmgkb_cancer_drugs(
    gene_ids: list[str],
    base_url: str | None = None,
    timeout: float | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Return PharmGKB cancer-related drug labels for genes."""
    return _call_bioapi(
        services.drugs_pharm_gkb,
        gene_ids,
        base_url=base_url,
        timeout=timeout,
    )


@mcp.tool()
def get_string_relations(
    gene_id: str,
    min_combined_score: int | None = None,
    base_url: str | None = None,
    timeout: float | None = None,
) -> list[dict[str, Any]]:
    """Return STRING functional association relations for a gene."""
    return _call_bioapi(
        services.string_relations,
        gene_id,
        min_combined_score=min_combined_score,
        base_url=base_url,
        timeout=timeout,
    )


@mcp.tool()
def get_drugs_regulating_gene(
    gene_id: str,
    base_url: str | None = None,
    timeout: float | None = None,
) -> dict[str, str]:
    """Return a DrugBank link for drugs that regulate a gene."""
    return _call_bioapi(
        services.drugs_regulating_gene,
        gene_id,
        base_url=base_url,
        timeout=timeout,
    )


@mcp.tool()
def get_bioapi_mcp_server_info() -> dict[str, Any]:
    """Return BioAPI MCP server defaults and available tool categories."""
    return {
        "base_url": DEFAULT_BASE_URL,
        "timeout": _resolve_timeout(None),
        "tools": [
            "gene nomenclature",
            "gene information",
            "HGNC groups",
            "metabolic pathways",
            "GTEx expression",
            "OncoKB cancer evidence",
            "Gene Ontology",
            "PharmGKB cancer drugs",
            "STRING associations",
            "DrugBank regulation links",
        ],
    }


def main() -> None:
    """Run the BioAPI MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
