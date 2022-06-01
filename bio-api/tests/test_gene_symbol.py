def test_missing_gene_id_param(client):
    """Tests missing mandatory parameter"""
    response = client.get('/gene-symbol')
    assert response.status_code == 400
