from pymongo import MongoClient


def related_terms_to_gene(str: gene)-> Dict[str]
    collection_go_anotations = mydb["go_anotations"]
    anotation = collection_go_anotations.find("gene_symbol": gene)
    if anotation != None:
        res = {"gene": gene, "relations" : set(anotation["involved_in"]+anotation["located_in"]+anotation["enables"]+anotation["part_of"])}
    res = {}
    return {}