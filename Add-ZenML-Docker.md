Add a `zenml` service to the `docker-compose.yml`.
See
- https://hub.docker.com/r/zenmldocker/zenml
- https://github.com/zenml-io/zenml
- https://docs.zenml.io/api-reference/pro-api/pro-api/health
- https://docs.zenml.io/deploying-zenml/deploying-zenml/deploy-with-docker

## Dockerfile
Ensure that zenml has its own dockerfile named `zenml.Dockerfile` to better organize and manage the image settings.

## Purpose
This docker service will orchestrate steps in a RAG pipeline.

## Dashboard
Enable the zenml dashboard. This is fine to be ran as a separate container.

## Verification
To verify, create a `test-zenml` script which will execute a cURL request against a health endpoint.
