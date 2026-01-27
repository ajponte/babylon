#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for OpenBao to become available
# This is a simple loop that waits for the OpenBao health endpoint to return a 200 status code.
echo "Waiting for OpenBao to start..."
while ! wget --no-verbose --tries=1 --spider http://127.0.0.1:8200/v1/sys/health; do
    sleep 1
done
echo "OpenBao is up and running!"

# Authenticate with OpenBao
# The BAO_TOKEN environment variable is set in the docker-compose.yml file.
export BAO_ADDR='http://127.0.0.1:8200'
export BAO_TOKEN='dev-token'

# Enable the KV secrets engine
# The kv-v2 secrets engine is a key-value store that can be used to store arbitrary secrets.
echo "Enabling KV secrets engine..."
bao secrets enable -path=secret kv-v2

# Write a secret
# This command writes a secret to the KV secrets engine.
# The secret is a database connection string.
echo "Writing secret..."
bao kv put secret/database url="postgresql://user:password@postgres:5432/babylon"

echo "OpenBao setup complete."
