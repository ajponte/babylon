import argparse
import os
import subprocess
import sys
import requests

def run_tox_build():
    """
    Executes tox to build the artifact.
    """
    print("Building artifact with tox...")
    try:
        subprocess.run(["tox", "-e", "build-artifact"], check=True)
        print("Tox build successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Tox build failed with exit code {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'tox' command not found. Ensure tox is installed.")
        sys.exit(1)

def get_release_by_tag(repo: str, tag: str, pat_token: str):
    """
    Fetches a release by its tag.
    """
    api_url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {pat_token}"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def create_release(repo: str, tag: str, pat_token: str):
    """
    Creates a new release on GitHub.
    """
    print(f"Creating new release for tag: {tag}")
    api_url = f"https://api.github.com/repos/{repo}/releases"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {pat_token}"
    }
    data = {
        "tag_name": tag,
        "name": f"Babylon Artifact {tag}",
        "body": "Automatically generated Babylon artifact.",
        "draft": False,
        "prerelease": False
    }
    response = requests.post(api_url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def upload_artifact_to_release(repo: str, release_id: int, artifact_path: str, pat_token: str):
    """
    Uploads a file as a release asset.
    """
    artifact_name = os.path.basename(artifact_path)
    print(f"Uploading {artifact_name} to release {release_id}...")
    
    # First, check if asset already exists and delete it if so (to allow overwrite)
    api_url = f"https://api.github.com/repos/{repo}/releases/{release_id}/assets"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {pat_token}"
    }
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    assets = response.json()
    for asset in assets:
        if asset['name'] == artifact_name:
            print(f"Deleting existing asset: {artifact_name}")
            delete_url = asset['url']
            requests.delete(delete_url, headers=headers).raise_for_status()

    # Upload the new asset
    upload_url = f"https://uploads.github.com/repos/{repo}/releases/{release_id}/assets?name={artifact_name}"
    headers["Content-Type"] = "application/zip"
    
    with open(artifact_path, "rb") as f:
        response = requests.post(upload_url, headers=headers, data=f)
        response.raise_for_status()
    
    print(f"Successfully uploaded {artifact_name} to GitHub Releases.")

def main():
    parser = argparse.ArgumentParser(description="Build and upload Babylon artifact to GitHub.")
    parser.add_argument("--repo", required=True, help="GitHub repository (e.g., owner/repo)")
    parser.add_argument("--tag", default="latest", help="Release tag to upload to (defaults to 'latest')")
    parser.add_argument("--pat-token", default=os.environ.get("BABYLON_API_GITHUB_PAT_TOKEN"), help="GitHub PAT token")
    parser.add_argument("--skip-build", action="store_true", help="Skip the tox build step")

    args = parser.parse_args()
    
    if not args.pat_token:
        print("Error: GitHub PAT token not provided. Set BABYLON_API_GITHUB_PAT_TOKEN or use --pat-token.")
        sys.exit(1)

    artifact_path = "babylon.zip"

    if not args.skip_build:
        run_tox_build()

    if not os.path.exists(artifact_path):
        print(f"Error: Artifact not found at {artifact_path}")
        sys.exit(1)

    try:
        release = get_release_by_tag(args.repo, args.tag, args.pat_token)
        if not release:
            release = create_release(args.repo, args.tag, args.pat_token)
        
        upload_artifact_to_release(args.repo, release['id'], artifact_path, args.pat_token)
    except requests.exceptions.RequestException as e:
        print(f"GitHub API Error: {e}")
        if e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)

if __name__ == "__main__":
    main()
