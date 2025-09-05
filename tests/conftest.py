from pathlib import Path

import pytest
import connexion


# API_SPEC_DIR = '../api_spec/'

API_SPEC = "test-api.yml"

# This is a pytest fixture. It's a special function that provides a reusable
# piece of code (like a test client) to your test functions.
@pytest.fixture
def connexion_client():
    """
    A pytest fixture to provide a test client for the Connexion app.
    It sets up the application once per test function and yields the client.
    """
    spec_path = get_api_spec_path(API_SPEC)
    # Create the Connexion app instance for testing.
    # We pass the specification_dir to find the api.yaml file.
    test_app = connexion.FlaskApp(__name__, specification_dir=spec_path)
    test_app.add_api(specification=spec_path)

    # Use the test_client context manager to ensure the client is properly closed.
    with test_app.app.test_client() as client:
        yield client

def get_api_spec_path(filename: str) -> Path:
    """
    Returns a pathlib.Path object for a given API spec filename.

    This function assumes the API specification files are located in the
    './api_spec/' directory relative to the current working directory.

    :param filename: The name of the API specification file (e.g., "test-api.yml").

    :return: Path: A Path object representing the full path to the API spec file.
    """
    # Get the base directory of the project (parent of the current file's directory)
    base_dir = Path(__file__).parent.parent

    # Construct the full path to the API spec file
    api_spec_path = base_dir / "api_spec" / filename

    # Return the Path object
    return api_spec_path

