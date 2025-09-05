from http import HTTPStatus

MOCK_ECHO_VAL = 'hello'

def test_echo(connexion_client):
    uri = '/api/echo'
    query_params = {"value": MOCK_ECHO_VAL}
    resp = connexion_client.get(uri, query_string=query_params)
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == {"value": MOCK_ECHO_VAL}
