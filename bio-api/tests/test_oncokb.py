import json

URL_BASE = '/information-of-oncokb'

headers = {
    'Content-Type': 'application/json'
}


def test_valid_response_format(client):
    """Tests valid response format"""
    gene = "ALK"
    data = {
        "gene_ids": [gene]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 200
    assert type(res) == dict
    assert type(res[gene]) == dict


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