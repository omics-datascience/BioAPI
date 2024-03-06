if (!require("BiocManager", quietly = TRUE))
  install.packages("BiocManager")
BiocManager::install(version = "3.18", ask = FALSE)

if("biomaRt" %in% rownames(installed.packages()) == FALSE)
  BiocManager::install("biomaRt", force = TRUE)

if("devtools" %in% rownames(installed.packages()) == FALSE)
  install.packages("devtools", repos = "http://cran.us.r-project.org")

if("dbplyr" %in% rownames(installed.packages()) == FALSE)
  devtools::install_version("dbplyr", version = "2.3.4", force = TRUE)

if("GeneSummary" %in% rownames(installed.packages()) == FALSE)
  BiocManager::install("GeneSummary", update = FALSE, ask = FALSE, force = FALSE)

library(GeneSummary)
library(dplyr)
library(biomaRt)
library(stringr)
library(BiocManager)

civicUrl="https://civicdb.org/downloads/nightly/nightly-GeneSummaries.tsv"
try(civicUrl <- Sys.getenv(CIVIC_URL), silent = TRUE)

# GRCh38 ####
ensembl_grch38 = useEnsembl(biomart = "genes", dataset = "hsapiens_gene_ensembl") 
atr <- c("ensembl_gene_id", "description", "chromosome_name", "start_position", "end_position", "strand", "band", "percentage_gene_gc_content", "gene_biotype", "hgnc_symbol", "hgnc_id", "entrezgene_id") 
fil_chrom <- c("MT", "X", "Y", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22")

res_grch38 <- getBM(
  attributes = atr,
  filters = c("chromosome_name", "with_hgnc"),
  values = list(fil_chrom, TRUE),
  mart = ensembl_grch38 
)
res_grch38$description <- data.frame(do.call('rbind', str_split(res_grch38$description, " \\[Source")))$X1


# GRCh37 ####
ensembl_grch37 = useEnsembl(biomart="genes", dataset = "hsapiens_gene_ensembl", GRCh = 37)
# listFilters(ensembl_grch37)
# listAttributes(ensembl_grch37)
atr <- c("ensembl_gene_id", "description", "chromosome_name", "start_position", "end_position", "strand", "band", "percentage_gene_gc_content", "gene_biotype", "hgnc_symbol", "hgnc_id", "entrezgene_id") 
res_grch37 <- getBM(
  attributes = atr,
  filters = c("chromosome_name", "with_hgnc"),
  values = list(fil_chrom, TRUE),
  mart = ensembl_grch37
)

res_grch37$description <- data.frame(do.call('rbind', str_split(res_grch37$description, " \\[Source")))$X1


# Summary of genes for Humans from RefSeq
RefSeqSummaryGenes = loadGeneSummary(organism = 9606)[, c(4,6)] # col 4: EntrezID. col 6: Summary of RefSeq gene
RefSeqSummaryGenesFiltered <- distinct(RefSeqSummaryGenes, Gene_ID, .keep_all = TRUE) # remove duplpicates ids 
names(RefSeqSummaryGenesFiltered)[names(RefSeqSummaryGenesFiltered) == "Gene_ID"] <- "entrezgene_id"
names(RefSeqSummaryGenesFiltered)[names(RefSeqSummaryGenesFiltered) == "Gene_summary"] <- "refseq_summary"

# dataset of genes from CiVIC 
civicGenes = read.csv(civicUrl, sep = "\t")[, c(4,5)]
civicGenes <- subset(civicGenes, !(description == "")) # remove empty descriptions
civicGenesFiltered <- distinct(civicGenes, entrez_id, .keep_all = TRUE) # remove duplpicates  
names(civicGenesFiltered)[names(civicGenesFiltered) == "description"] <- "civic_description"
names(civicGenesFiltered)[names(civicGenesFiltered) == "entrez_id"] <- "entrezgene_id"



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
