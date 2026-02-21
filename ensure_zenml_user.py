import requests
import time
import sys
import os

def wait_for_zenml(url, timeout=60):
    """Wait for the ZenML server to be responsive."""
    start_time = time.time()
    print(f"Waiting for ZenML at {url}...")
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
    return False

def check_or_create_user(url, username, password):
    """
    Attempts to log in with the provided credentials.
    In a local 'pre-load' scenario, the server handles creation via env vars.
    This script verifies that the pre-loading worked.
    """
    login_url = f"{url}/api/v1/login"
    # ZenML OAuth2 login expects form data
    data = {
        "username": username,
        "password": password
    }
    
    try:
        print(f"Attempting to verify user '{username}'...")
        response = requests.post(login_url, data=data)
        
        if response.status_code == 200:
            print(f"✅ Success: User '{username}' is active and authenticated.")
            return True
        elif response.status_code == 401:
            print(f"❌ Error: Authentication failed for '{username}'. The user may not exist or the password is incorrect.")
            return False
        else:
            print(f"❓ Unexpected response: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    # These match the values in your docker-compose.yml
    ZENML_URL = os.getenv("ZENML_SERVER_URL", "http://localhost:8081")
    USERNAME = os.getenv("ZENML_DEFAULT_USER_NAME", "admin")
    PASSWORD = os.getenv("ZENML_DEFAULT_USER_PASSWORD", "Babylon@123")

    if wait_for_zenml(ZENML_URL):
        if check_or_create_user(ZENML_URL, USERNAME, PASSWORD):
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print("Timed out waiting for ZenML server.")
        sys.exit(1)
