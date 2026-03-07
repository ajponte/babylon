# Use a slim version of the official Python 3.13 image as a base.
FROM python:3.13-slim

# Build arguments for GitHub release download
ARG BABYLON_API_GITHUB_PAT_TOKEN
ARG BABYLON_API_REPO=ajponte/babylon_api_spec
ARG BABYLON_API_RELEASE_TAG=latest

# Install curl and unzip for health checking and artifact extraction.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container.
WORKDIR /usr/src/app

# Copy the dependency management files first.
COPY pyproject.toml poetry.lock ./

# Copy the .env file so it can be used by the application at runtime.
COPY .env .

# Install poetry.
RUN pip install poetry

# Install the dependencies and create a virtual environment within the container.
RUN poetry install --without test --no-root --sync --no-ansi

# Download babylon.zip from GitHub releases.
RUN if [ -n "$BABYLON_API_GITHUB_PAT_TOKEN" ]; then \
    curl -fSL "https://github.com/${BABYLON_API_REPO}/releases/download/${BABYLON_API_RELEASE_TAG}/babylon.zip" \
        -H "Authorization: Bearer ${BABYLON_API_GITHUB_PAT_TOKEN}" \
        -o babylon.zip && \
    unzip -o babylon.zip && \
    pip install server-*.whl --force-reinstall --no-deps && \
    rm -f babylon.zip server-*.whl server-*.tar.gz server-*.tar; \
    fi

# Copy the rest of your application code into the container.
COPY . .

# Expose port 8000.
EXPOSE 8000

# Set the entrypoint for the container to use poetry's executable.
ENTRYPOINT ["poetry", "run"]

# The command to run your application using gunicorn.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "production:application"]
