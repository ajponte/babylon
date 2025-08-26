from server.config import hashicorp as MUT
from unittest.mock import MagicMock, patch, ANY


def test_open_bao_api_client():
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
    with patch('server.config.hashicorp.hvac.Client', return_value=mock_hvac):
        api_client = MUT.OpenBaoApiClient()
        secrets = api_client.read_secret_values(path=ANY)

    assert secrets == mock_secrets