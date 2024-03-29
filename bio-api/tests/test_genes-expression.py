import json

URL_BASE = '/expression-of-genes'

headers = {
    'Content-Type': 'application/json'
}


def test_valid_response_format(client):
    """Tests valid response format"""
    gene = "FAM87B"
    tissue = "Breast"
    data = {
        "tissue": tissue,
        "gene_ids": [gene]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 200
    assert type(res) == list
    assert type(res[0]) == dict


def test_invalid_body_format(client):
    """Tests invalid body format"""
    # 'tejido' instead of 'tissue'
    data = {
        "tejido": "Blood",
        "gene_ids": ["BRCA1", "BRCA2"]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: tissue is mandatory"
    # 'gene' instead of 'gene_ids'
    data = {
        "tissue": "Blood",
        "gene": ["BRCA1"]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: gene_ids is mandatory"
    # Str instead of list type in gene_ids
    data = {
        "tissue": "Blood",
        "gene_ids": "BRCA1"
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: gene_ids must be a list"


def test_invalid_tissues(client):
    """Tests invalid tissues"""
    gene = "BRCA1"
    tissue = "invalid_tissue"
    data = {
        "tissue": tissue,
        "gene_ids": [gene]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 200
    assert res == []
