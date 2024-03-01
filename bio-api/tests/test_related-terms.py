import json

URL_BASE = '/related-terms'

headers = {
    'Content-Type': 'application/json'
}


def test_valid_response_format(client):
    """Tests valid response format"""
    data = {"term_id": "0000079",
            "general_depth": 5}
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    assert response.status_code == 200
    res = json.loads(response.data)
    assert type(res) == list
    assert type(res[0]) == dict
    assert type(res[0]["relations"]) == dict
    assert "go_id" in res[0]
    assert "name" in res[0]
    assert "ontology_type" in res[0]


def test_invalid_body_format(client):
    """Tests invalid body format"""
    # 'id' instead of term_id'
    data = {
        "id": "0000079"
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: term_id is mandatory"

    # term_id not in DB
    data = {
        "term_id": "GO: 0000079"
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: term_id is not on database"

    # Str instead of list type in relations
    data = {
        "term_id": "0000079",
        "relations": "regulates"

    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: relations must be a list"

    # Str instead of list type in  ontology_type
    data = {
        "term_id": "0000079",
        "ontology_type": "molecular_function"

    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: ontology_type must be a list"

    # invalid ontology_type
    data = {
        "term_id": "0000079",
        "ontology_type": ["molecular_function", "not_an_ontology_type"]

    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: not_an_ontology_type is not a valid ontology_type"

    # general_depth is negative'
    data = {
        "term_id": "0000079",
        "general_depth": -100
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: depth should be a positive integer"
    # hierarchical_depth_to_children is negative'
    data = {
        "term_id": "0000079",
        "hierarchical_depth_to_children": -100
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: hierarchical depth should be a positive integer"

    # general_depth is not an integer'
    data = {
        "term_id": "0000079",
        "general_depth": "a"
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: depth should be an integer"
    # hierarchical_depth_to_children is not an integer
    data = {
        "term_id": "0000079",
        "hierarchical_depth_to_children": "a"
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: depth should be an integer"
