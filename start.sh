#!/bin/bash

# A startup script for the babylon-app to wait for OpenBao before starting Gunicorn.

BAO_ADDR="${BAO_ADDR:-http://openbao:8200}" # Use environment variable if set, otherwise default
BAO_TOKEN="${BAO_TOKEN:-dev-token}" # Use environment variable if set, otherwise default

echo "Waiting for OpenBao to be ready at $BAO_ADDR..."
until curl -s "$BAO_ADDR/v1/sys/health" | grep '"initialized":true' > /dev/null; do
    echo "OpenBao not yet ready, waiting..."
    sleep 2
done

echo "OpenBao is initialized and ready!"
echo "Starting Gunicorn..."

# Execute the original Gunicorn command
poetry run gunicorn --bind 0.0.0.0:8000 --workers 4 production:application