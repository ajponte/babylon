from http import HTTPStatus

BASE_URI = '/api'

HTTP_HEADER_CONTENT_TYPE = 'application/json'

MOCK_BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

MOCK_ECHO_VAL = 'hello'

def test_echo(app_client):
    uri = f'{BASE_URI}/echo'
    query_params = {"inputVal": MOCK_ECHO_VAL}
    headers = {"Authorization": f"Bearer {MOCK_BEARER_TOKEN}", 'content-type': HTTP_HEADER_CONTENT_TYPE}
    resp = app_client.get(uri, params=query_params, headers=headers)
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data == {"value": MOCK_ECHO_VAL}
