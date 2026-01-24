from http import HTTPStatus

BASE_URI = '/api/v1'

# It's common to need a bearer token for protected endpoints.
# This token is likely a mock value used across the test suite.
MOCK_BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
HTTP_HEADER_CONTENT_TYPE = 'application/json'


def test_datalake_sync_status_get(app_client):
    """Test the datalake sync status endpoint."""
    uri = f'{BASE_URI}/datalake/sync/status'
    headers = {"Authorization": f"Bearer {MOCK_BEARER_TOKEN}", 'content-type': HTTP_HEADER_CONTENT_TYPE}
    resp = app_client.get(uri, headers=headers)
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert "status" in data
    assert "last_successful_sync" in data
    assert "records_processed" in data
    assert isinstance(data["records_processed"], int)
