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
    
    