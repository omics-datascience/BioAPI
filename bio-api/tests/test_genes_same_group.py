import json

URL_BASE = '/genes-same-group'

def test_gene_in_group(client):
    """test gene that belongs to a group"""
    valid_id="1956" #Entrez ID
    response = client.get(f'{URL_BASE}/{valid_id}')
    res = json.loads(response.data)
    assert response.status_code == 200
    assert "gene_id" in list(res.keys())
    assert "groups" in list(res.keys())
    assert "locus_group" in list(res.keys())
    assert "locus_type" in list(res.keys())
    assert type(res["gene_id"]) == str
    assert type(res["groups"]) == list
    assert type(res["locus_group"]) == str
    assert type(res["locus_type"]) == str
    assert res["gene_id"] == "EGFR"
    assert res["locus_group"] == "protein-coding gene"
    assert res["locus_type"] == "gene with protein product"
    assert len(res["groups"]) == 1
    assert res["groups"][0]["gene_group"] == "Erb-b2 receptor tyrosine kinases"
    assert res["groups"][0]["gene_group_id"] == "1096"
    assert sorted(res["groups"][0]["genes"]) == sorted(["ERBB3","EGFR","ERBB2","ERBB4"])


def test_gene_not_in_group(client):
    """test gene that dont belongs to a group"""
    valid_id="TP53" #HGNC approved symbol
    response = client.get(f'{URL_BASE}/{valid_id}')
    res = json.loads(response.data)
    assert response.status_code == 200
    assert "gene_id" in list(res.keys())
    assert "groups" in list(res.keys())
    assert "locus_group" in list(res.keys())
    assert "locus_type" in list(res.keys())
    assert type(res["gene_id"]) == str
    assert type(res["groups"]) == list
    assert type(res["locus_group"]) == str
    assert type(res["locus_type"]) == str
    assert res["gene_id"] == "TP53"
    assert res["locus_group"] == "protein-coding gene"
    assert res["locus_type"] == "gene with protein product"
    assert len(res["groups"]) == 0


def test_gene_alias(client):
    """test with gene symbol that is alias of two valid symbols"""
    alias_id="BRCC1" #Alias
    response = client.get(f'{URL_BASE}/{alias_id}')
    res = json.loads(response.data)
    assert response.status_code == 400
    assert "error" in list(res.keys())
    assert type(res["error"]) == str
    assert res["error"] == "400 Bad Request: ambiguous gene identifier. The identifier may refer to more than one HGNC-approved gene (BRCA1,ICE2)"


def test_invalid_gene_symbol(client):
    """test with invalid gene symbol"""
    invalid_id="bolainas" #invalid id
    response = client.get(f'{URL_BASE}/{invalid_id}')
    res = json.loads(response.data)
    assert response.status_code == 400
    assert "error" in list(res.keys())
    assert type(res["error"]) == str
    assert res["error"] =="400 Bad Request: invalid gene identifier"


def test_invalid_gene_symbol(client):
    """Tests missing mandatory parameter"""
    response = client.get(f'{URL_BASE}')
    res = json.loads(response.data)
    assert response.status_code == 404
    assert "error" in list(res.keys())
    assert type(res["error"]) == str
    assert res["error"] == "404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."