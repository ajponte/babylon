import server.config.hashicorp as MUT
from pytest import fixture
from unittest.mock import MagicMock, patch, ANY

from server.config.hashicorp import BaoSecretsManager, OpenBaoApiClient


@fixture(autouse=True)
def open_bao_api_client():
    """Mock `OpenBaoApiClient`."""
    mock_secrets = {
        'k1': 's1',
        'k2': 's2'
    }

    mock_hvac = MagicMock(spec=MUT.hvac.Client)
    # mock_hvac.is_authenticated.return_value = True
    mock_hvac.secrets.kv.read_secret_version.return_value = {
        'data': {
            'data': mock_secrets,
            'metadata': {'version': 1}
        }
    }
    with patch('server.config.hashicorp.hvac.Client', return_value=mock_hvac):
        mock_hvac.is_authenticated.return_value = True
        api_client = MUT.OpenBaoApiClient()
    return api_client



def test_open_bao_api_client(open_bao_api_client):
    mock_secrets = {
        'k1': 's1',
        'k2': 's2'
    }

    mock_hvac = MagicMock(spec=MUT.hvac.Client)
    mock_hvac.secrets.kv.read_secret_version.return_value = {
        'data': {
            'data': mock_secrets,
            'metadata': {'version': 1}
        }
    }
    secrets = open_bao_api_client.read_secret_values(path=ANY)
    assert secrets == mock_secrets
