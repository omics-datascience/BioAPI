import json

URL_BASE = '/genes-pathways'


def test_valid_source_and_externalid(client):
    """Tests valid source an external_id"""
    source = "humancyc"
    external_id = "BETA-ALA-DEGRADATION-I-PWY"
    response = client.get(f'{URL_BASE}/{source}/{external_id}')
    res = json.loads(response.data)
    assert response.status_code == 200
    assert type(res["genes"]) == list
    assert len(res["genes"]) == 2
    assert "ALDH6A1" in res["genes"]
    assert "ABAT" in res["genes"]


def test_invalid_source(client):
    """Tests invalid source"""
    source = "ciscate"
    external_id = "path:hsa05206"
    response = client.get(f'{URL_BASE}/{source}/{external_id}')
    res = json.loads(response.data)
    assert response.status_code == 404
    assert res["error"] == '404 Not Found: '+source+' is an invalid pathway source'


def test_invalid_external_id(client):
    """Tests invalid external_id"""
    source = "kegg"
    external_id = "SrThompson"
    response = client.get(f'{URL_BASE}/{source}/{external_id}')
    res = json.loads(response.data)
    assert response.status_code == 200
    assert type(res["genes"]) == list
    assert len(res["genes"]) == 0
