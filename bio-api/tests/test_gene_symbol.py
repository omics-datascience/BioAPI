import json

URL = '/gene-symbol'


def test_missing_gene_id_param(client):
    """Tests missing mandatory parameter"""
    response = client.get(URL)
    assert response.status_code == 400


def test_gene_id_valid(client):
    """Tests a valid gene_id"""
    response = client.get(f'{URL}?gene_id=A1BG-AS')
    json_data = json.loads(response.data)
    aliases = json_data['gene']
    assert response.status_code == 200
    assert len(aliases) == 1
    assert aliases[0] == 'A1BG-AS1'
