import pytest
from unittest.mock import patch, MagicMock
import github_artifacts
import requests

# Mock constants
MOCK_REPO = "test/repo"
MOCK_PAT_TOKEN = "test_token"
MOCK_RUN_ID = 12345
MOCK_ARTIFACT_NAME = f"api-spec-{MOCK_RUN_ID}"
MOCK_ARTIFACT_ID = 98765

@pytest.fixture
def mock_requests_get():
    """Fixture to mock requests.get."""
    with patch('requests.get') as mock_get:
        yield mock_get

def test_get_latest_successful_run_id_success(mock_requests_get):
    """Test get_latest_successful_run_id successfully finds a run ID."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "workflow_runs": [{"id": MOCK_RUN_ID}]
    }
    mock_requests_get.return_value = mock_response

    run_id = github_artifacts.get_latest_successful_run_id(MOCK_REPO, MOCK_PAT_TOKEN)

    assert run_id == MOCK_RUN_ID
    mock_requests_get.assert_called_once_with(
        f"https://api.github.com/repos/{MOCK_REPO}/actions/runs",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {MOCK_PAT_TOKEN}"
        },
        params={
            "status": "success",
            "branch": "main",
            "per_page": 1
        }
    )

def test_get_latest_successful_run_id_no_runs(mock_requests_get):
    """Test get_latest_successful_run_id when no runs are found."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"workflow_runs": []}
    mock_requests_get.return_value = mock_response

    with pytest.raises(SystemExit):
        github_artifacts.get_latest_successful_run_id(MOCK_REPO, MOCK_PAT_TOKEN)

def test_download_artifact_success(mock_requests_get):
    """Test download_artifact successfully downloads and extracts an artifact."""
    # Mock response for finding the artifact
    mock_find_response = MagicMock()
    mock_find_response.raise_for_status.return_value = None
    mock_find_response.json.return_value = {
        'artifacts': [{'id': MOCK_ARTIFACT_ID, 'name': MOCK_ARTIFACT_NAME}]
    }

    # Mock response for downloading the artifact
    mock_download_response = MagicMock()
    mock_download_response.raise_for_status.return_value = None
    mock_download_response.content = b'zip_content'

    mock_requests_get.side_effect = [mock_find_response, mock_download_response]

    with patch('zipfile.ZipFile') as mock_zipfile, \
         patch('os.makedirs') as mock_makedirs:
        
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance

        github_artifacts.download_artifact(MOCK_REPO, MOCK_RUN_ID, MOCK_ARTIFACT_NAME, MOCK_PAT_TOKEN)

        mock_makedirs.assert_called_with("./api_spec", exist_ok=True)
        mock_zip_instance.extractall.assert_called_with("./api_spec")

def test_download_artifact_not_found(mock_requests_get):
    """Test download_artifact when the artifact is not found."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {'artifacts': []}
    mock_requests_get.return_value = mock_response

    with pytest.raises(SystemExit):
        github_artifacts.download_artifact(MOCK_REPO, MOCK_RUN_ID, MOCK_ARTIFACT_NAME, MOCK_PAT_TOKEN)

def test_download_artifact_api_error(mock_requests_get):
    """Test download_artifact with a requests exception."""
    mock_requests_get.side_effect = requests.exceptions.RequestException

    with pytest.raises(SystemExit):
        github_artifacts.download_artifact(MOCK_REPO, MOCK_RUN_ID, MOCK_ARTIFACT_NAME, MOCK_PAT_TOKEN)

def test_parse_args_with_run_id(monkeypatch):
    """Test parse_args with a specific run ID."""
    monkeypatch.setenv("BABYLON_API_GITHUB_PAT_TOKEN", MOCK_PAT_TOKEN)
    with patch('sys.argv', ['github_artifacts.py', '--repo', MOCK_REPO, '--run-id', str(MOCK_RUN_ID)]):
        args = github_artifacts.parse_args()
        assert args.repo == MOCK_REPO
        assert args.run_id == str(MOCK_RUN_ID)

def test_main_with_run_id(monkeypatch):
    """Test the main execution block with a run ID."""
    monkeypatch.setenv("BABYLON_API_GITHUB_PAT_TOKEN", MOCK_PAT_TOKEN)
    with patch('sys.argv', ['github_artifacts.py', '--repo', MOCK_REPO, '--run-id', str(MOCK_RUN_ID)]):
        mock_download = MagicMock()
        monkeypatch.setattr(github_artifacts, "download_artifact", mock_download)
        
        github_artifacts.main()

        mock_download.assert_called_once_with(
            repo=MOCK_REPO,
            run_id=str(MOCK_RUN_ID),
            artifact_name=f"api-spec-{MOCK_RUN_ID}",
            pat_token=MOCK_PAT_TOKEN
        )

def test_main_with_ci_env(monkeypatch):
    """Test the main execution block in a CI environment."""
    monkeypatch.setenv('CI', 'true')
    monkeypatch.setenv("BABYLON_API_GITHUB_PAT_TOKEN", MOCK_PAT_TOKEN)
    with patch('sys.argv', ['github_artifacts.py', '--repo', MOCK_REPO]):
        mock_download = MagicMock()
        mock_get_latest_run_id = MagicMock(return_value=MOCK_RUN_ID)
        monkeypatch.setattr(github_artifacts, "download_artifact", mock_download)
        monkeypatch.setattr(github_artifacts, "get_latest_successful_run_id", mock_get_latest_run_id)

        github_artifacts.main()

        mock_get_latest_run_id.assert_called_once()
        mock_download.assert_called_once_with(
            repo=MOCK_REPO,
            run_id=MOCK_RUN_ID,
            artifact_name=f"api-spec-{MOCK_RUN_ID}",
            pat_token=MOCK_PAT_TOKEN
        )

def test_main_no_run_id_local(monkeypatch):
    """Test main block exits when no run_id is given locally."""
    monkeypatch.setenv("BABYLON_API_GITHUB_PAT_TOKEN", MOCK_PAT_TOKEN)
    with patch('sys.argv', ['github_artifacts.py', '--repo', MOCK_REPO]):
        with pytest.raises(SystemExit):
            github_artifacts.main()
