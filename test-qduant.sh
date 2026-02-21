#!/bin/bash
# Script to verify the Qdrant service health.

echo "Checking Qdrant health..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:6333/healthz)

if [ "$RESPONSE" -eq 200 ]; then
    echo "Qdrant is healthy (HTTP $RESPONSE)."
    exit 0
else
    echo "Qdrant health check failed (HTTP $RESPONSE)."
    exit 1
fi
