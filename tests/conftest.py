import pytest
from pytest import fixture
import connexion
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


# The original hvac_client and open_bao_api_client fixtures are replaced
# with a single, more explicit test function using a patch context manager.


@fixture(autouse=True)
def mock_hvac_client():
    """
    This fixture patches the hvac.Client and yields a mock instance of it.
    The patch is automatically started and stopped by pytest.
    """
    with patch('server.config.hashicorp.hvac.Client') as mock_client:
        yield mock_client

# This is a pytest fixture. It's a special function that provides a reusable
# piece of code (like a test client) to your test functions.
@fixture
def connexion_client(mock_bao_client):
    """
    A pytest fixture to provide a test client for the Connexion app.
    It sets up the application once per test function and yields the client.
    """
    # Assuming your application has a create_app function that returns a Connexion app instance.
    # We will import that function and use it to set up the test client.
    from server.app import create_app

    # Create the Connexion app instance for testing.
    test_app = create_app()

    # Use the test_client context manager to ensure the client is properly closed.
    with test_app.app.test_client() as client:
        # A helpful debugging step to see what URLs are actually available
        print("\nAvailable Routes:")
        for rule in test_app.app.url_map.iter_rules():
            print(f"- {rule.endpoint}: {rule.rule}")

        yield client


@fixture(scope="function", autouse=True)
def mock_env():
    """
    A pytest fixture to set and unset environment variables for testing.
    This ensures a clean environment for each test function.
    """
    # Store the original environment variables
    original_env = os.environ.copy()

    # Set the required environment variables for the tests
    os.environ['BAO_ADDR'] = 'http://localhost:8200'
    os.environ['BAO_TOKEN'] = 'dev-token'

    os.environ['OPENBAO_SECRETS_PATH'] = 'test'
    os.environ['SQLALCHEMY_POOL_RECYCLE'] = '3600'
    os.environ['SQLALCHEMY_DB_ENGINE'] = 'sqlite'
    os.environ['SQLALCHEMY_DATABASE_NAME'] = 'babylon'

    # The `yield` statement makes this a generator fixture.
    # The code before yield runs during setup, and the code after runs during teardown.
    yield

    # Restore the original environment variables after the test is done
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_bao_client():
    """
    A fixture to mock the OpenBao client for tests that require a secrets manager.
    """
    with patch('server.config.hashicorp.BaoSecretsManager') as MockBaoSecretsManager:
        # We need to create a mock of the instance that will be returned
        mock_instance = MagicMock()

        # We need to mock the client attribute of the instance
        mock_instance.client = MagicMock()
        mock_instance.client.is_authenticated.return_value = True

        # And set up the mock return values for the methods called
        mock_instance.client.secrets.kv.read_secret_version.return_value = {
            'data': {
                'data': {
                    'BAO_ADDR': 'http://localhost:8200',
                    'BAO_TOKEN': 'dev-token',
                    'DB_HOST': 'https://mock-host.com',
                    'DB_PORT': '5432',
                    'DB_USERNAME': 'dummy',
                    'DB_PASSWORD': 'dummy'
                },
                'metadata': {
                    'version': 1
                }
            }
        }

        # Set the return value of the patched class to our mock instance
        MockBaoSecretsManager.return_value = mock_instance

        yield mock_instance
