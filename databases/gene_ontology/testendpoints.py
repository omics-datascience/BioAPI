from pymongo import MongoClient

############# MongoDB Conf ############
ip_mongo="localhost"
port_mongo=8888
user="root"
password="root"
db_name="bio_api"
#######################################

mongoClient = MongoClient(ip_mongo + ":" + str(port_mongo),username=user,password=password,authSource='admin',authMechanism='SCRAM-SHA-1')
mydb = mongoClient[db_name]

def terms_related_to_one_gene(gene: str, relation_type: list= ["enables","involved_in","part_of","located_in"]):#-> Dict[str]
    collection_go_anotations = mydb["go_anotations"]
    anotation = dict(collection_go_anotations.find_one({"gene_symbol": gene}))
    # print((anotastion))
    related_genes = set()
    if anotation != None:
        for relation in relation_type:
            if relation in anotation:
                if isinstance(anotation[relation], list):
                    related_genes.update(anotation[relation])
                else:
                    related_genes.add(anotation[relation])
            
        # res = {"gene": gene, "relations" : related_genes}
    
    return related_genes
    
def terms_related_to_many_genes(gene_ids: list, filter_type = "intersection", relation_type: list= ["enables","involved_in","part_of","located_in"]):
    gene = gene_ids.pop()
    term_set= set(terms_related_to_one_gene(gene,relation_type))
    for gene in gene_ids:
        terms = terms_related_to_one_gene(gene,relation_type)
        if filter_type == "intersection":
            term_set= term_set.intersection(terms)
        elif filter_type == "union":
            term_set = term_set.union(terms)

    return term_set

def populate_terms_with_data(term_list, ontology_type: list = ["biological_process", "molecular_function", "cellular_component"]):
    collection_go = mydb["go"]
    terms = list(collection_go.find({"id": { "$in": term_list }, "namespace": { "$in": ontology_type }}))
    return terms
    

# print(terms_related_to_one_gene("RPL41"))
# print(terms_related_to_one_gene("RPS19"))
# print(terms_related_to_one_gene("BRCA1"))
# print(terms_related_to_many_genes(["RPL41","RPS19","BRCA1"],"intersection"))
# print(terms_related_to_many_genes(["RPL41","RPS19"],"intersection"))
# print(terms_related_to_many_genes(["RPL41","RPS19"],"intersection",["enables","involved_in"]))

# aux =list(terms_related_to_many_genes(["RPL41","RPS19"],"intersection"))
# print(len(populate_terms_with_data(aux)))
# print(len(populate_terms_with_data(aux,["cellular_component"])))


def BFS_on_termss(general_depth, hierarchical_depth, ontology_type, relations):
    pass


def strip_term(term,relations):
    new_term = {"id": term["id"], "name": term["name"],"ontology_type": term["namespace"], "relations": {}}
    for r in relations:
        if r in term:
            if not isinstance(term[r], list): term[r] = [term[r]]
            new_term["relations"][r]= term[r]
    return new_term

relations = ["part_of","regulates","has_part"]

def  BFS_on_terms(term_id, relations, general_depth,hierarchical_depth, ontology_type): #function for BFS
    collection_go = mydb["go"]
    graph = {}
    DEPTH_MARK = "*"
    
    visited = [] # List for visited nodes.
    queue = []     #Initialize a queue
    visited.append(term_id)
    queue.append(term_id)
    queue.append(DEPTH_MARK)
    actual_depth = 0

    while queue:          # Creating loop to visit each node
        act = queue.pop(0) 
        if act == DEPTH_MARK:
            if actual_depth == general_depth or not queue:
                break
            queue.append(DEPTH_MARK)
            actual_depth += 1  
        else:
            #could be optimized by pooling all the next level neighbours and doing one db call per level
            #but on the other side you have to control for already visited nodes, so im not sure if its faster
            term = collection_go.find_one({"id": act}) 
            # print(term)
            # print(term["namespace"])
            if not term["namespace"] in ontology_type:
                continue
            term =strip_term(term,relations)
            graph[term["id"]] = term
            for rel in term["relations"].values():
                for neighbour in rel:
                  if neighbour not in visited:
                    visited.append(neighbour)
                    queue.append(neighbour)
    
    terms= [term_id]
    next_level_terms = []
    for i in range(hierarchical_depth):
        terms = collection_go.find({"is_a": { "$in": terms }} )
        for t in terms:
            t_id = t["id"]
            if t_id in visited:
                term =strip_term(t,["is_a"])
                graph[t_id]["relations"]['is_a']= term["relations"]["is_a"]
            else:
                term =strip_term(t,["is_a"])
                graph[term["id"]] = term
            next_level_terms.append(term["id"])
            
        terms = next_level_terms
        next_level_terms = []
    
    #go to the ontology root   
    terms= [term_id]
    while terms: 
        print(terms)
        terms = collection_go.find({"id": { "$in": terms }} )
        for t in terms:
            t_id = t["id"]
            if t_id in visited:
                term =strip_term(t,["is_a"])
                graph[t_id]["relations"]['is_a']= term["relations"]["is_a"]
            else:
                term =strip_term(t,["is_a"])
                graph[term["id"]] = term
            if "is_a" in term["relations"]:
                next_level_terms.extend(term["relations"]["is_a"])
            
        terms = next_level_terms
        next_level_terms = []
    
    
    return list(graph.values())
    
# print(bfs("GO:0000079", relations, 50,["biological_process", "molecular_function"]))
collection_go = mydb["go"]
# term = collection_go.find({"is_a": "GO:0000018"})
# term = collection_go.find({"is_a": { $in: [ "GO:0000018", "X" ] }})
# term = collection_go.find({"is_a": { "$all": ["GO:0000018",'GO:2000779'] }} )
# print(list(term))
# print(".............")
# term2 = collection_go.find({"is_a": { "$in": ["GO:0000018",'GO:2000779'] }} )
# print(list(term2))
# print(list(term) == list(term2))
print(bfs("GO:0000073",relations,0,0,["biological_process", "molecular_function","cellular_component"]))
