import json

URL_BASE = '/gene-symbol'


def test_gene_id_valid(client):
    """"Tests a valid gene_id"""
    valid_id = "191170"  # OMIM ID
    response = client.get(f'{URL_BASE}/{valid_id}')
    res = json.loads(response.data)
    assert response.status_code == 200
    assert type(res[valid_id]) == list
    assert "TP53" in res[valid_id]


def test_gene_alias_two_genes(client):
    """"test with gene symbol that is alias of two valid symbols"""
    alias_id = "BRCC1"  # Alias
    response = client.get(f'{URL_BASE}/{alias_id}')
    res = json.loads(response.data)
    assert response.status_code == 200
    assert type(res[alias_id]) == list
    assert "BRCA1" in res[alias_id]
    assert "ICE2" in res[alias_id]
    assert len(res[alias_id]) == 2


def test_gene_id_invalid(client):
    """"Tests a invalid gene_id"""
    invalid_id = "XXX"  # Invalid id
    response = client.get(f'{URL_BASE}/{invalid_id}')
    res = json.loads(response.data)
    assert response.status_code == 404
    assert "error" in res


def test_missing_gene_id_param(client):
    """Tests missing mandatory parameter"""
    response = client.get(f'{URL_BASE}/')
    res = json.loads(response.data)
    assert response.status_code == 404
    assert "error" in res
