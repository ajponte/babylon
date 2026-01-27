import os
import pytest
import hvac
from server.config.hashicorp import OpenBaoApiClient, SecretsManagerException

def test_read_secret_from_openbao_integration():
    """
    Test that the Flask app can read a secret from OpenBao.
    """
    client = OpenBaoApiClient()
    path = "secret/database"
    key = "url"
    expected_value = "postgresql://user:password@postgres:5432/babylon"

    try:
        secret_data = client.read_secret_values(path=path)
        assert key in secret_data
        assert secret_data[key] == expected_value
    except SecretsManagerException as e:
        pytest.fail(f"Failed to read secret from OpenBao: {e}")
