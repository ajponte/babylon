from http import HTTPStatus

BASE_URI = '/api'

MOCK_ECHO_VAL = 'hello'

def test_echo(app_client):
    uri = f'{BASE_URI}/echo'
    query_params = {"value": MOCK_ECHO_VAL}
    resp = app_client.get(uri, params=query_params)
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data == {"value": MOCK_ECHO_VAL}
