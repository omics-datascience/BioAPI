import json

URL_BASE = '/genes-pathways-intersection'
headers = {
    'Content-Type': 'application/json'
}


def test_valid_genes_ids(client):
    """"Tests valid genes ids"""
    valid_ids = ["HLA-B", "BRAF"]
    data = {
        "genes_ids": valid_ids
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 200
    assert type(res["pathways"]) == list
    assert len(res["pathways"]) == 1
    assert res["pathways"][0]["external_id"] == "hsa04650"
    assert res["pathways"][0]["pathway"] == "Natural killer cell mediated cytotoxicity"
    assert res["pathways"][0]["source"] == "KEGG"


def test_invalid_genes_ids(client):
    """ Tests invalid genes ids """
    invalids_ids = ["HLA-B", "INVALID"]
    data = {
        "genes_ids": invalids_ids
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 200
    assert type(res["pathways"]) == list
    assert len(res["pathways"]) == 0


def test_empty_gene_id(client):
    """test correct body structure but no gene in the list"""
    data = {
        "genes_ids": []
    }
    response = client.post(f'{URL_BASE}', data=json.dumps(data), headers=headers)
    res = json.loads(response.data)
    assert response.status_code == 400
    assert "error" in res
