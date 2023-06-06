import json

URL_BASE = '/genes-to-terms'

headers = {
    'Content-Type': 'application/json'
}


def test_valid_response_format(client):
    """Tests valid response format"""
    data ={    "gene_ids" : ["TMCO4"],
				"relation_type": ["enables"],   
				"ontology_type" : ["molecular_function"],
                "filter_type" : "union"}
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    assert response.status_code == 200
    res = json.loads(response.data)
    assert type(res) == list
    assert type(res[0]) == dict
    assert type(res[0]["relations_to_genes"]) == list
    assert type(res[0]["relations_to_genes"][0]) == dict
    assert "go_id" in res[0]
    assert "name" in res[0]
    assert "ontology_type" in res[0]
    assert "definition" in res[0]
    # 'gene_ids' that is not on DB
    data = {
        "gene_ids": ["BROCO1i"]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 200
    res = json.loads(response.data)
    assert res == []

    #test gene enrichment
    data ={    "gene_ids" : ["RPL41","RPS19","BRCA1"],  
				"ontology_type" : ["molecular_function"],
                "filter_type" : "enrichment",
                "correction_method": "bonferroni",
                "p_value_threshold" : 0.5}
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    assert response.status_code == 200
    res = json.loads(response.data)
    assert type(res) == list
    assert type(res[0]) == dict
    assert type(res[0]["relations_to_genes"]) == list
    assert type(res[0]["relations_to_genes"][0]) == dict
    assert "go_id" in res[0]
    assert "name" in res[0]
    assert "ontology_type" in res[0]
    assert "definition" in res[0]
    assert "enrichment_metrics" in res[0]
    assert "effective_domain_size" in res[0]["enrichment_metrics"]
    assert "intersection_size" in res[0]["enrichment_metrics"]
    assert "p_value" in res[0]["enrichment_metrics"]
    assert "precision" in res[0]["enrichment_metrics"]
    assert "query_size" in res[0]["enrichment_metrics"]
    assert "recall" in res[0]["enrichment_metrics"]
    assert "term_size" in res[0]["enrichment_metrics"]

def test_invalid_body_format(client):
    """Tests invalid body format"""
    # 'ids' instead of 'gene_ids'
    data = {
        "ids": ["BRCA1", "BRCA2"]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: gene_ids is mandatory"
    
    
    # Str instead of list type in gene_ids
    data = {
        "gene_ids": "BRCA1"
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: gene_ids must be a list"
    
    # Str instead of list type in relation_type
    data = {
        "gene_ids": ["BRCA1", "BRCA2"],
        "relation_type": "enables"
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: relation_type must be a list"
    
    # Str instead of list type in ontology_type
    data = {
        "gene_ids": ["BRCA1", "BRCA2"],
        "ontology_type" : "molecular_function"
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: ontology_type must be a list"
    
    #Invalid filter_type
    data = {
        "gene_ids": ["BRCA1"],
        "filter_type" : "interunion"
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert "filter_type is invalid" in res["error"]
    
    #invalid ontology_type
    data = {
        "gene_ids": ["BRCA1"],
        "ontology_type" : ["molecular_function","not_an_ontology_type"]
        
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: not_an_ontology_type is not a valid ontology_type"
    #relation type when not aplicable
    data = {
        "gene_ids": ["MLH1","PMS2","MSH2","MSH6","BRAC1", "GSTM2"],
        "filter_type" : "enrichment",
        "relation_type": ["enables"],
        "correction_method": "bonferroni",
        "p_value_threshold" : "1e-11"
        
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: relation_type filter is not valid on gene enrichment analysis, all the available relation types will be used."
        #p_value_threshold when not aplicable
    data = {
        "gene_ids": ["MLH1","PMS2","MSH2","MSH6","BRAC1", "GSTM2"],
        "filter_type" : "union",
        "p_value_threshold" : "1e-11"
        
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: p_value_threshold is only valid on gene enrichment analysis"
        #correction_method when not aplicable
    data = {
        "gene_ids": ["MLH1","PMS2","MSH2","MSH6","BRAC1", "GSTM2"],
        "filter_type" : "union",
        "correction_method": "bonferroni"
        
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: correction_method is only valid on gene enrichment analysis"
        #invalid p_value_threshold 
    data = {
        "gene_ids": ["MLH1","PMS2","MSH2","MSH6","BRAC1", "GSTM2"],
        "filter_type" : "enrichment",
        "p_value_threshold" : "not a number"

        
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: p_value_threshold should be an float"
        #invalid correction_method
    data = {
        "gene_ids": ["MLH1","PMS2","MSH2","MSH6","BRAC1", "GSTM2"],
        "filter_type" : "enrichment",
        "correction_method": "true_discovery_rate"
        
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert "correction_method is invalid" in res["error"]
    
    