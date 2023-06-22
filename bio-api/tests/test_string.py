import json

URL_BASE = '/string-relations'

headers = {
    'Content-Type': 'application/json'
}


def test_valid_response_format(client):
    """Tests valid response format"""
    min_combined_score = 998
    data = {
    "gene_id" : "JAK2",
    "min_combined_score": min_combined_score
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    assert response.status_code == 200
    res = json.loads(response.data)
    assert type(res) == list
    assert "gene_1" in res[1]
    assert "gene_2" in res[1]
    assert "combined_score" in res[1]
    assert min_combined_score < res[1]["combined_score"]

    data["min_combined_score"] = 1000
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    assert response.status_code == 200
    res = json.loads(response.data)
    assert res == []


def test_invalid_body_format(client):
    """Tests invalid body format"""
    # no 'gene_id'
    
    data ={   
    "min_combined_score": 900
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: gene_id is mandatory"
    #min_combined_score not a number
    data = {
        "gene_id" : "JAK2",
        "min_combined_score": "ten"
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: min_combined_score must be number"