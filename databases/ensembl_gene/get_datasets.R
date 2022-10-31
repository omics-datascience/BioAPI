if (!requireNamespace("BiocManager", quietly = TRUE))
  install.packages("BiocManager")

if("biomaRt" %in% rownames(installed.packages()) == FALSE)
  BiocManager::install("biomaRt", force = TRUE)

library(biomaRt)
library(stringr)

# BUSQUEDA PARA GRCh38 ####
ensembl_grch38 = useEnsembl(biomart="genes", dataset = "hsapiens_gene_ensembl") 
# posibles_filtros <- listFilters(ensembl_grch38)
# posibles_atributos <- listAttributes(ensembl_grch38)
atr <- c("ensembl_gene_id", "description", "chromosome_name", "start_position", "end_position", "strand", "band", "percentage_gene_gc_content", "gene_biotype", "hgnc_symbol", "hgnc_id", "entrezgene_id") 
fil <- c("with_hgnc")
res_grch38 <- getBM(
  attributes = atr,
  filters = fil,
  values = TRUE,
  mart = ensembl_grch38 
)
res_grch38$description <- data.frame(do.call('rbind', str_split(res_grch38$description, " \\[Source")))$X1


# BUSQUEDA PARA GRCh37 ####
ensembl_grch37 = useEnsembl(biomart="genes", dataset = "hsapiens_gene_ensembl", GRCh = 37)
# posibles_filtros <- listFilters(ensembl_grch37)
# posibles_atributos <- listAttributes(ensembl_grch37)
atr <- c("ensembl_gene_id", "description", "chromosome_name", "start_position", "end_position", "strand", "band", "percentage_gene_gc_content", "gene_biotype", "hgnc_symbol", "hgnc_id", "entrezgene_id") 
fil <- c("with_hgnc")
res_grch37 <- getBM(
  attributes = atr,
  filters = fil,
  values = TRUE,
  mart = ensembl_grch37
)

res_grch37$description <- data.frame(do.call('rbind', str_split(res_grch37$description, " \\[Source")))$X1

write.csv(res_grch37, "ensembl_gene_grch37.csv", row.names = FALSE, na = "")
write.csv(res_grch38, "ensembl_gene_grch38.csv", row.names = FALSE, na = "")
