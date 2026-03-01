# Runbook: OpenBao Deployment on Digital Ocean

This runbook describes how to deploy OpenBao on a Digital Ocean droplet using Ansible and Python.

## Prerequisites
1.  **Digital Ocean Droplet:** A fresh droplet with Ubuntu (preferably 22.04 LTS).
2.  **SSH Access:** Ensure your SSH key is added to the droplet for the `root` user.
3.  **Local Environment:**
    *   Python 3.x
    *   Ansible (`pip install ansible`)
    *   PyYAML (`pip install pyyaml`)

## Deployment Steps

### 1. Configure the Droplet IP
Set the IP address of your Digital Ocean droplet.

### 2. Run the Deployment Script
Navigate to the `deployment/openbao` directory and run the deployment script:

```bash
cd deployment/openbao
python scripts/deploy_openbao.py --ip <DROPLET_IP>
```

### 3. Verification
Once the deployment is complete, access the OpenBao UI via HTTPS:

`https://<DROPLET_IP>/ui`

**Note:** You will see a certificate warning because we are using a self-signed certificate. You can replace this later with a Let's Encrypt certificate.

### 4. OpenBao Initialization
If this is the first time you are deploying OpenBao, you will need to initialize it:

1.  Access the droplet via SSH: `ssh root@<DROPLET_IP>`
2.  Run the initialization command inside the container:
    ```bash
    docker exec -it openbao bao operator init
    ```
3.  Save the **Unseal Keys** and the **Initial Root Token** in a secure location.
4.  Unseal OpenBao using 3 of the keys:
    ```bash
    docker exec -it openbao bao operator unseal <KEY1>
    docker exec -it openbao bao operator unseal <KEY2>
    docker exec -it openbao bao operator unseal <KEY3>
    ```

## Post-Deployment
- Configure policies and authentication methods in OpenBao.
- Update `TEMPORARY_USER.md` with the new root token if necessary for testing.

