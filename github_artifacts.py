import argparse
import os
import sys
import requests
import zipfile
import io


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pat-token",
        default=os.environ.get("BABYLON_API_GITHUB_PAT_TOKEN"),
        help="GitHub PAT token (or set BABYLON_API_GITHUB_PAT_TOKEN env var)",
    )
    parser.add_argument('--run-id')
    parser.add_argument('--artifact-name')
    parser.add_argument('--repo')

    args = parser.parse_args()

    if not args.pat_token:
        sys.stderr.write(
            "ERROR: GitHub PAT token not provided.\n"
            "  Either pass --pat-token <token> or set the "
            "BABYLON_API_GITHUB_PAT_TOKEN environment variable.\n"
        )
        sys.exit(1)

    return args

def download_artifact(repo: str, run_id: str, artifact_name: str, pat_token: str | None=None):
    """
    Downloads an artifact from a GitHub Actions workflow run using the GitHub REST API.
    """
    if not all([repo, run_id, artifact_name, pat_token]):
        print("Error: Missing input.")
        print("Please set REPO, RUN_ID, ARTIFACT_NAME, and PAT_TOKEN.")
        sys.exit(1)

    print(f"Downloading artifact '{artifact_name}' from {repo} run {run_id}")

    # Step 1: Find the artifact ID
    api_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {pat_token}"
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        artifacts = response.json().get('artifacts', [])

        artifact = next((a for a in artifacts if a['name'] == artifact_name), None)

        if not artifact:
            print(f"Error: Artifact with name '{artifact_name}' not found for run '{run_id}'.")
            sys.exit(1)

        artifact_id = artifact['id']
        print(f"Found artifact with ID: {artifact_id}")

        # Step 2: Download the artifact
        download_url = f"https://api.github.com/repos/{repo}/actions/artifacts/{artifact_id}/zip"
        download_response = requests.get(download_url, headers=headers, stream=True)
        download_response.raise_for_status()

        # Step 3: Unzip the downloaded artifact
        download_dir = "./api_spec"
        os.makedirs(download_dir, exist_ok=True)

        with zipfile.ZipFile(io.BytesIO(download_response.content)) as zip_ref:
            zip_ref.extractall(download_dir)

        print(f"Artifact unzipped to {download_dir}")
        print("Download and extraction complete.")

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        sys.exit(1)
    except (KeyError, IndexError) as e:
        print(f"Failed to parse API response: {e}")
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    run_id = args.run_id
    artifact_name = args.artifact_name
    repo = args.repo
    token = args.pat_token

    download_artifact(
        repo=repo,
        run_id=run_id,
        artifact_name=artifact_name,
        pat_token=token
    )
