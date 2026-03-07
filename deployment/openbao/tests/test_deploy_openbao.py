import unittest
from unittest.mock import patch, mock_open
import os
import sys
import yaml

# Add the scripts directory to the path so we can import the script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from deploy_openbao import generate_inventory, run_ansible_playbook

class TestDeployOpenBao(unittest.TestCase):

    def test_generate_inventory_digitalocean(self):
        """Test that the inventory file is generated correctly for digitalocean."""
        ip_address = "1.2.3.4"
        provider = "digitalocean"
        inventory_path = "test_inventory_do.yml"
        
        with patch("builtins.open", mock_open()) as mocked_file:
            path = generate_inventory(ip_address, provider, inventory_path)
            
            self.assertEqual(path, inventory_path)
            # Verify the content written to the file
            handle = mocked_file()
            written_content = "".join(call.args[0] for call in handle.write.call_args_list)
            data = yaml.safe_load(written_content)
            self.assertEqual(data['all']['hosts']['digitalocean_server']['ansible_host'], ip_address)

    def test_generate_inventory_aws(self):
        """Test that the inventory file is generated correctly for AWS (with 'ubuntu' user)."""
        ip_address = "9.10.11.12"
        provider = "aws"
        inventory_path = "test_inventory_aws.yml"
        
        with patch("builtins.open", mock_open()) as mocked_file:
            path = generate_inventory(ip_address, provider, inventory_path)
            
            self.assertEqual(path, inventory_path)
            handle = mocked_file()
            written_content = "".join(call.args[0] for call in handle.write.call_args_list)
            data = yaml.safe_load(written_content)
            self.assertEqual(data['all']['hosts']['aws_server']['ansible_host'], ip_address)
            self.assertEqual(data['all']['hosts']['aws_server']['ansible_user'], "ubuntu")

    @patch("subprocess.run")
    def test_run_ansible_playbook_success(self, mock_run):
        """Test that the ansible-playbook command is called correctly on success."""
        mock_run.return_value.stdout = "Ansible output"
        mock_run.return_value.returncode = 0
        
        success, output = run_ansible_playbook("inventory.yml", "ansible/deploy.yml")
        
        self.assertTrue(success)
        self.assertEqual(output, "Ansible output")
        mock_run.assert_called_once()
        self.assertIn("ansible-playbook", mock_run.call_args[0][0])
        self.assertIn("inventory.yml", mock_run.call_args[0][0])

    @patch("subprocess.run")
    def test_run_ansible_playbook_failure(self, mock_run):
        """Test that the ansible-playbook command handles failure correctly."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, "ansible-playbook", stderr="Error message")
        
        success, output = run_ansible_playbook("inventory.yml", "ansible/deploy.yml")
        
        self.assertFalse(success)
        self.assertEqual(output, "Error message")

if __name__ == "__main__":
    unittest.main()
