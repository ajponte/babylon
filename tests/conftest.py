import pytest
import connexion
from pathlib import Path


# This is a pytest fixture. It's a special function that provides a reusable
# piece of code (like a test client) to your test functions.
@pytest.fixture
def connexion_client():
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
