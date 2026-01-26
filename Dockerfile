# Use a slim version of the official Python 3.13 image as a base.
FROM python:3.13-slim

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

# Copy the rest of your application code into the container.
COPY . .

# Install curl for health checks in the startup script.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the startup script.
COPY start.sh .

# Make the startup script executable.
RUN chmod +x start.sh

# Set the entrypoint for the container to use the startup script.
ENTRYPOINT ["/bin/bash", "start.sh"]

# CMD is empty as the gunicorn command is now inside start.sh.
CMD []
