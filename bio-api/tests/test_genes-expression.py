import json

URL_BASE = '/genes-expression'

headers = {
    'Content-Type': 'application/json'
}

def test_valid_response_format(client):
    """Tests valid response_format"""
    gene="FAM87B"
    tissue="Breast"
    data = {    
        "tissue": tissue,
        "genes_ids": [gene]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 200
    assert type(res) == list
    assert type(res[0]) == list
    assert type(res[0][0]) == dict
    claves = list(res[0][0])
    assert "expression" in claves and "gene" in claves
