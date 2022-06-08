import json

URL_BASE = '/genes-symbols'
headers = {
    'Content-Type': 'application/json'
}

def test_gene_id_valid(client):
    """"Tests a valid gene_id"""
    valid_id="ENSG00000157764" #ensembl_gene_id
    data = {    
        "genes_ids" : [ valid_id ]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.content_type == 'application/json'
    assert response.status_code == 200
    assert valid_id in list(res.keys())
    assert type(res[valid_id]) == list
    assert "BRAF" in res[valid_id]

def test_valid_and_invalid_genes(client):
    """"test for one valid and one invalid gene"""
    valid_id="HGNC:3236"    #hgnc_id
    invalid_id="blcdtm"     #invalid id
    data = {    
        "genes_ids" : [ valid_id, invalid_id ]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.content_type == 'application/json'
    assert response.status_code == 200
    assert valid_id in list(res.keys())
    assert invalid_id in list(res.keys())
    assert type(res[valid_id]) == list
    assert type(res[invalid_id]) == list
    assert res[valid_id][0] == "EGFR"
    assert res[invalid_id] == []


def test_gene_alias_two_genes_and_invalid_id(client):
    """tests a symbol that is aliases of two genes and an invalid symbol"""
    alias_id="NAP1"    #alias
    invalid_id="estoesungeninvalido"     #invalid id
    data = {    
        "genes_ids" : [ alias_id, invalid_id ]
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.content_type == 'application/json'
    assert response.status_code == 200
    assert alias_id in list(res.keys())
    assert invalid_id in list(res.keys())
    assert type(res[alias_id]) == list
    assert type(res[invalid_id]) == list
    assert res[invalid_id] == []
    assert "ACOT8" in res[alias_id]
    assert "AZI2" in res[alias_id]
    assert "CXCL8" in res[alias_id]
    assert "NAP1L1" in res[alias_id]
    assert "NAPSA" in res[alias_id]


def test_empty_gene_id(client):
    """test correct body structure but no gene in the list"""
    data = {    
        "genes_ids" : []
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.content_type == 'application/json'
    assert response.status_code == 200
    assert len(list(res.keys())) == 0
    assert res == {}
    

def test_corrupted_structure(client):
    """test incorrect body structure"""
    data = {    
        "thisisakey" : "hi"
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.content_type == 'application/json'
    assert response.status_code == 400
    assert "error" in list(res.keys())
    assert res["error"] == "400 Bad Request: genes_ids is mandatory"