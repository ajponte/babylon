import subprocess
import os
import argparse
import yaml

def generate_inventory(ip_address, provider, inventory_path="inventory.yml"):
    """Generates an Ansible inventory file."""
    # AWS typically uses 'ubuntu' as the default user for Ubuntu images, 
    # whereas DO and Linode often use 'root'.
    ansible_user = "ubuntu" if provider == "aws" else "root"
    
    inventory = {
        "all": {
            "hosts": {
                f"{provider}_server": {
                    "ansible_host": ip_address,
                    "ansible_user": ansible_user
                }
            },
            "children": {
                "openbao_servers": {
                    "hosts": {
                        f"{provider}_server": None
                    }
                }
            }
        }
    }
    with open(inventory_path, "w") as f:
        yaml.dump(inventory, f)
    return inventory_path

def run_ansible_playbook(inventory_path, playbook_path="ansible/deploy.yml"):
    """Runs the ansible-playbook command."""
    cmd = [
        "ansible-playbook",
        "-i", inventory_path,
        playbook_path
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    parser = argparse.ArgumentParser(description="Deploy OpenBao on a Cloud Provider Droplet/Instance")
    parser.add_argument("--ip", required=True, help="IP address of the instance")
    parser.add_argument("--provider", choices=["digitalocean", "linode", "aws"], default="digitalocean", help="Cloud provider name")
    parser.add_argument("--playbook", default="ansible/deploy.yml", help="Path to the Ansible playbook")
    
    args = parser.parse_args()
    
    inventory_path = generate_inventory(args.ip, args.provider)
    print(f"Generated inventory for {args.provider} at {inventory_path}")
    
    print(f"Starting Ansible deployment for {args.provider} IP: {args.ip}...")
    success, output = run_ansible_playbook(inventory_path, args.playbook)
    
    if success:
        print("Deployment successful!")
        print(output)
    else:
        print("Deployment failed!")
        print(output)

if __name__ == "__main__":
    main()
