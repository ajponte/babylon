Add a `qduant` service to the `docker-compose.yml`. See https://github.com/qdrant/qdrant.

Allow the dashboard page (http://localhost:{port}/dashboard) to be accessed by a web-browser.

Requests from localhost to persist or retrieve vector embeddings should be accessible.

## Updating this docker-compose
If any additional configuration is needed for docker-compose, or if a reverse-proxy is needed, please address accordingly.

## Verification
For verification, create a `test-qduant.sh` script which will send a cURL request against the service to trigger a health check.
