import json

URL_BASE = '/information-of-genes'

headers = {
    'Content-Type': 'application/json'
}


def test_response_format(client):
    """"Tests a valid response structure"""
    valid_id1 = "MAU2"
    invalid_id2 = "THIS_IS_AN_INVALID_GENE_SYMBOL"
    data = {
        "gene_ids": [valid_id1, invalid_id2]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 200
    assert type(res) == dict
    assert len(res) == 1
    assert type(res[valid_id1]) == dict

def test_oncokb_civic_and_refseq_data(client):
    """"Test a correct data reading from oncokb and refseq"""
    valid_id = "ALK"
    data = {
        "gene_ids": [valid_id]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 200
    assert type(res) == dict
    assert "oncokb_cancer_gene" in res[valid_id]
    assert type(res[valid_id]["oncokb_cancer_gene"]) == str
    assert "refseq_summary" in res[valid_id]
    assert type(res[valid_id]["refseq_summary"]) == str
    assert "civic_description" in res[valid_id]
    assert type(res[valid_id]["civic_description"]) == str    


def test_an_invalid_body_format(client):
    """"Tests a valid body json"""
    valid_id = "MAU2"
    data = {
        "genes": [valid_id]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: gene_ids is mandatory"


def test_empty_gene_id(client):
    """test correct body structure but no gene in the list"""
    data = {
        "gene_ids": []
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 200
    assert len(res) == 0


def test_corrupted_structure(client):
    """test incorrect body structure"""
    data = {
        "this_is_a_key": "this_is_a_value"
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert "error" in res
