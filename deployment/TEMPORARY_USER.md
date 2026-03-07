# Temporary User Credentials (A/B Test)

## Digital Ocean (Droplet)
- **Username:** `babylon-admin`
- **Password:** `BabylonTemporary2026!`
- **Role:** Administrator
- **SSH Key:** `~/.ssh/id_rsa_babylon` (ensure this is added to the Digital Ocean droplet)

## Linode (Instance)
- **Username:** `babylon-admin`
- **Password:** `BabylonLinode2026!`
- **Role:** Administrator
- **SSH Key:** `~/.ssh/id_rsa_babylon` (ensure this is added to the Linode instance)

## AWS (EC2 Instance)
- **Username:** `ubuntu` (Default for Ubuntu AMIs)
- **Role:** Administrator
- **SSH Key:** `~/.ssh/babylon-aws.pem`

## AWS Secrets Manager (Managed Service)
- **IAM User:** `babylon-secrets-manager` (Access via AWS CLI/SDK)
- **Region:** `us-east-1`

## OpenBao Initial Root Token
- **Token:** `dev-root-token` (Placeholder: Replace after initialization)

## Access
- **URL:** `https://<DROPLET_IP>/ui`
- **SSH:** `ssh root@<DROPLET_IP>`
