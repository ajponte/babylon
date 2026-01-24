import argparse
import os
import sys
import requests
import zipfile
import io


def get_latest_successful_run_id(repo: str, pat_token: str) -> int:
    """
    Finds the ID of the most recent successful workflow run on the main branch.
    """
    print(f"Finding latest successful run for repo: {repo}")
    api_url = f"https://api.github.com/repos/{repo}/actions/runs"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {pat_token}"
    }
    params = {
        "status": "success",
        "branch": "main",
        "per_page": 1
    }

    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        runs = response.json().get('workflow_runs', [])

        if not runs:
            print("Error: No successful workflow runs found on the main branch.")
            sys.exit(1)

        latest_run_id = runs[0]['id']
        print(f"Found latest successful run with ID: {latest_run_id}")
        return latest_run_id

    except requests.exceptions.RequestException as e:
        print(f"API request to find latest run failed: {e}")
        sys.exit(1)
    except (KeyError, IndexError) as e:
        print(f"Failed to parse API response for latest run: {e}")
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pat-token",
        default=os.environ.get("BABYLON_API_GITHUB_PAT_TOKEN"),
        help="GitHub PAT token (or set BABYLON_API_GITHUB_PAT_TOKEN env var)",
    )
    parser.add_argument('--repo', required=True)
    parser.add_argument('--latest-successful-run', action='store_true', help='Download artifact from the latest successful run on the main branch.')
    parser.add_argument('--run-id')
    parser.add_argument('--artifact-name')

    args = parser.parse_args()

    if not args.pat_token:
        sys.stderr.write(
            "ERROR: GitHub PAT token not provided.\n"
            "  Either pass --pat-token <token> or set the "
            "BABYLON_API_GITHUB_PAT_TOKEN environment variable.\n"
        )
        sys.exit(1)

    if not args.latest_successful_run and not (args.run_id and args.artifact_name):
        parser.error("Either --latest-successful-run or both --run-id and --artifact-name are required.")

    return args


def download_artifact(repo: str, run_id: int, artifact_name: str, pat_token: str):
    """
    Downloads an artifact from a GitHub Actions workflow run using the GitHub REST API.
    """
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
        # Add more context to the 410 Gone error
        if e.response is not None and e.response.status_code == 410:
            print("  This '410 Gone' error typically means the artifact has expired and been deleted by GitHub's retention policy.")
        sys.exit(1)
    except (KeyError, IndexError) as e:
        print(f"Failed to parse API response: {e}")
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    token = args.pat_token
    repo = args.repo

    if args.latest_successful_run:
        run_id = get_latest_successful_run_id(repo, token)
        # Assuming the artifact name follows this pattern
        artifact_name = f"api-spec-{run_id}"
    else:
        run_id = args.run_id
        artifact_name = args.artifact_name

    download_artifact(
        repo=repo,
        run_id=run_id,
        artifact_name=artifact_name,
        pat_token=token
    )