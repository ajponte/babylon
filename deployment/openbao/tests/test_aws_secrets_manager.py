import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the scripts directory to the path so we can import the script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from aws_secrets_manager_util import AWSSecretsManager

class TestAWSSecretsManager(unittest.TestCase):

    @patch("boto3.client")
    def test_create_secret_new(self, mock_boto):
        """Test creating a new secret."""
        mock_client = MagicMock()
        mock_boto.return_value = mock_client
        mock_client.create_secret.return_value = {"Name": "test_secret"}
        
        sm = AWSSecretsManager()
        success, response = sm.create_secret("test_secret", "test_value")
        
        self.assertTrue(success)
        mock_client.create_secret.assert_called_once()

    @patch("boto3.client")
    def test_get_secret(self, mock_boto):
        """Test retrieving a secret."""
        mock_client = MagicMock()
        mock_boto.return_value = mock_client
        mock_client.get_secret_value.return_value = {"SecretString": "secret_data"}
        
        sm = AWSSecretsManager()
        success, value = sm.get_secret("test_secret")
        
        self.assertTrue(success)
        self.assertEqual(value, "secret_data")

if __name__ == "__main__":
    unittest.main()
