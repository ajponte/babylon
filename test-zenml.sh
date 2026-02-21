#!/bin/bash

# A simple shell script to test the ZenML container.
# This script assumes the ZenML server is running via docker-compose.

ZENML_ADDR="http://localhost:8081"

echo "Waiting for ZenML to be ready (at $ZENML_ADDR)..."

# Use a loop to wait for the ZenML server to respond.
# We check both /health and /api/v1/info as different versions might expose different endpoints.
MAX_RETRIES=12
COUNT=0

while [ $COUNT -lt $MAX_RETRIES ]; do
    HEALTH_CHECK=$(curl -s "$ZENML_ADDR/health")
    INFO_CHECK=$(curl -s "$ZENML_ADDR/api/v1/info")
    
    if echo "$HEALTH_CHECK" | grep -q '"status":"ok"'; then
        echo "ZenML Health: OK"
        break
    elif echo "$INFO_CHECK" | grep -q '"version":'; then
        echo "ZenML Info: Available"
        break
    fi
    
    echo "ZenML not yet ready, waiting... ($((COUNT+1))/$MAX_RETRIES)"
    sleep 10
    COUNT=$((COUNT+1))
done

if [ $COUNT -eq $MAX_RETRIES ]; then
    echo "ZenML failed to start within the expected time."
    exit 1
fi

echo "ZenML is ready!"
echo "---"
echo "Server Info:"
curl -s "$ZENML_ADDR/api/v1/info"
echo -e "
---"
echo "ZenML test complete."
