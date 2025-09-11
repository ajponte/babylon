#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Validate that all required arguments are provided.
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
    echo "Usage: $0 <REPO> <RUN_ID> <ARTIFACT_NAME> <PAT_TOKEN>"
    exit 1
fi

REPO=$1
RUN_ID=$2
ARTIFACT_NAME=$3
PAT_TOKEN=$4

# Define the download directory
DOWNLOAD_DIR="./api-specs"
mkdir -p "$DOWNLOAD_DIR"

echo "Downloading artifact '$ARTIFACT_NAME' from $REPO run $RUN_ID"

# Use the GitHub API to find the artifact ID.
ARTIFACT_ID=$(curl -s -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $PAT_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/runs/$RUN_ID/artifacts" | jq -r '.artifacts[] | select(.name == "'"$ARTIFACT_NAME"'") | .id')

# Check if the artifact ID was found
if [ -z "$ARTIFACT_ID" ]; then
    echo "Error: Artifact with name '$ARTIFACT_NAME' not found for run '$RUN_ID'."
    exit 1
fi

echo "Found artifact with ID: $ARTIFACT_ID"

# Download the artifact as a zip file using its ID.
curl -L -o "$DOWNLOAD_DIR/$ARTIFACT_NAME.zip" \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $PAT_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/artifacts/$ARTIFACT_ID/zip"

echo "Artifact downloaded to $DOWNLOAD_DIR/$ARTIFACT_NAME.zip"

# Unzip the downloaded artifact and junk the paths to place files directly in the download directory.
unzip -oj "$DOWNLOAD_DIR/$ARTIFACT_NAME.zip" -d "$DOWNLOAD_DIR"

echo "Artifact unzipped to $DOWNLOAD_DIR"

# Clean up the downloaded zip file.
rm "$DOWNLOAD_DIR/$ARTIFACT_NAME.zip"

echo "Download and extraction complete."
