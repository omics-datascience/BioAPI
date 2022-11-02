import json

URL_BASE = '/genes-information'

headers = {
    'Content-Type': 'application/json'
}

def test_response_format(client):
    """"Tests a valid response strucure"""
    valid_id1 = "MAU2"
    invalid_id2 = "THIS_IS_AN_INVALID_GENE_SYMBOL" 
    data = {    
        "genes_ids" : [ valid_id1, invalid_id2 ]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 200
    assert type(res) == dict
    assert len(res) == 1
    assert type(res[valid_id1]) == dict
    assert len(res[valid_id1]) == 7

def test_an_invalid_body_format(client):
    """"Tests a valid body json"""
    valid_id = "MAU2"
    data = {    
        "genes" : [ valid_id ]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: genes_ids is mandatory"

def test_empty_gene_id(client):
    """test correct body structure but no gene in the list"""
    data = {    
        "genes_ids" : []
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 200
    assert len(res) == 0
    assert res == {}
    

def test_corrupted_structure(client):
    """test incorrect body structure"""
    data = {    
        "thisisakey" : "thisisavalue"
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert "error" in list(res.keys())