import subprocess
import os
import argparse
import yaml

def generate_inventory(ip_address, inventory_path="inventory.yml"):
    """Generates an Ansible inventory file."""
    inventory = {
        "all": {
            "hosts": {
                "openbao_server": {
                    "ansible_host": ip_address,
                    "ansible_user": "root"
                }
            },
            "children": {
                "openbao_servers": {
                    "hosts": {
                        "openbao_server": None
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
    parser = argparse.ArgumentParser(description="Deploy OpenBao on a Digital Ocean Droplet")
    parser.add_argument("--ip", required=True, help="IP address of the droplet")
    parser.add_argument("--playbook", default="ansible/deploy.yml", help="Path to the Ansible playbook")
    
    args = parser.parse_args()
    
    inventory_path = generate_inventory(args.ip)
    print(f"Generated inventory at {inventory_path}")
    
    print(f"Starting Ansible deployment for IP: {args.ip}...")
    success, output = run_ansible_playbook(inventory_path, args.playbook)
    
    if success:
        print("Deployment successful!")
        print(output)
    else:
        print("Deployment failed!")
        print(output)

if __name__ == "__main__":
    main()
