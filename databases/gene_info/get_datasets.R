# Install BiocManager if it doesn't exist
if (!requireNamespace("BiocManager", quietly = TRUE)) {
  install.packages("BiocManager")
}

# Auxiliary function to install from CRAN
install_if_missing <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "http://cran.us.r-project.org")
  }
}

# Install CRAN packages
cran_packages <- c("devtools", "dplyr", "stringr")
invisible(lapply(cran_packages, install_if_missing))

# Install specific version of dbplyr
if (!requireNamespace("dbplyr", quietly = TRUE) || packageVersion("dbplyr") != "2.3.4") {
  devtools::install_version("dbplyr", version = "2.3.4", repos = "http://cran.us.r-project.org")
}

# Install Bioconductor packages
bioc_packages <- c("biomaRt", "GeneSummary")
for (pkg in bioc_packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    BiocManager::install(pkg, update = FALSE, ask = FALSE)
  }
}

# Load libraries
library(GeneSummary)
library(dplyr)
library(biomaRt)
library(stringr)



civicUrl <- "https://civicdb.org/downloads/nightly/nightly-FeatureSummaries.tsv" # URL to download the latest version of CiVIC Gene Summaries


atr <- c("ensembl_gene_id", "description", "chromosome_name", "start_position", "end_position", "strand", "band", "percentage_gene_gc_content", "gene_biotype", "hgnc_symbol", "hgnc_id", "entrezgene_id") 
fil_chrom <- c("MT", "X", "Y", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22")

# GRCh37 ####
ensembl_grch37 = useEnsembl(biomart="ensembl", dataset = "hsapiens_gene_ensembl", GRCh = 37)
res_grch37 <- getBM(
  attributes = atr,
  filters = c("chromosome_name", "with_hgnc"),
  values = list(fil_chrom, TRUE),
  mart = ensembl_grch37
)
res_grch37$description <- data.frame(do.call('rbind', str_split(res_grch37$description, " \\[Source")))$X1


# GRCh38 ####
ensembl_grch38 = useMart(biomart = "ensembl", dataset = "hsapiens_gene_ensembl") 
res_grch38 <- getBM(
  attributes = atr,
  filters = c("chromosome_name", "with_hgnc"),
  values = list(fil_chrom, TRUE),
  mart = ensembl_grch38 
)
res_grch38$description <- data.frame(do.call('rbind', str_split(res_grch38$description, " \\[Source")))$X1

# Summary of genes for Humans from RefSeq
RefSeqSummaryGenes = loadGeneSummary(organism = 9606)[, c(4,6)] # col 4: EntrezID. col 6: Summary of RefSeq gene
RefSeqSummaryGenesFiltered <- distinct(RefSeqSummaryGenes, Gene_ID, .keep_all = TRUE) # remove duplpicates ids 
names(RefSeqSummaryGenesFiltered)[names(RefSeqSummaryGenesFiltered) == "Gene_ID"] <- "entrezgene_id"
names(RefSeqSummaryGenesFiltered)[names(RefSeqSummaryGenesFiltered) == "Gene_summary"] <- "refseq_summary"

# dataset of genes from CiVIC 
civicGenes_raw <- read.csv(civicUrl, sep = "\t")
civicGenesFiltered <- civicGenes_raw %>%
  dplyr::select(entrez_id, description) %>%
    filter(!is.na(description) & description != "") %>%
      distinct(entrez_id, .keep_all = TRUE) %>%
      rename(
        civic_description = description,
        entrezgene_id = entrez_id
      )

res_grch37 = merge(res_grch37, civicGenesFiltered, 
                             by = "entrezgene_id", all.x = TRUE)
all_grch37_gene_data = merge(res_grch37, RefSeqSummaryGenesFiltered, 
                             by = "entrezgene_id", all.x = TRUE)
res_grch38 = merge(res_grch38, civicGenesFiltered, 
                   by = "entrezgene_id", all.x = TRUE)
all_grch38_gene_data = merge(res_grch38, RefSeqSummaryGenesFiltered, 
                             by = "entrezgene_id", all.x = TRUE)

write.csv(all_grch37_gene_data, "gene_info_grch37.csv", row.names = FALSE, na = "")
write.csv(all_grch38_gene_data, "gene_info_grch38.csv", row.names = FALSE, na = "")
