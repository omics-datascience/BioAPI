import json

URL_BASE = '/gene-symbols-finder/'

header = {'Content-Type': 'application/json'}


def test_response_format(client):
    """"Tests a valid response structure"""
    data = {"limit": 100000, "query": "a"}
    response = client.get(path=URL_BASE, query_string=data, headers=header)
    res = json.loads(response.data)
    assert response.status_code == 200
    assert type(res) == list
    for element in res:
        assert type(element) == str
    data = {"limit": 2, "query": "brc"}
    response = client.get(path=URL_BASE, query_string=data, headers=header)
    res = json.loads(response.data)
    assert len(res) == 2


def test_missing_query_parameter(client):
    """Tests missing query mandatory parameter"""
    data = {"limit": 50}
    response = client.get(path=URL_BASE, query_string=data, headers=header)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: 'query' parameter is mandatory"


def test_limit_parameter_as_string(client):
    """Tests an non numeric value for limit parameter"""
    data = {"query": "tp", "limit": "two"}
    response = client.get(path=URL_BASE, query_string=data, headers=header)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert res["error"] == "400 Bad Request: 'limit' parameter must be a numeric value"
