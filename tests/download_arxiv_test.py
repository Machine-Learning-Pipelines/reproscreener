import tarfile
from pathlib import Path
from unittest.mock import Mock, patch

from reproscreener.download_arxiv import download_extract_source


@patch("requests.get")
@patch("tarfile.open")
def test_download_extract_source(mock_tarfile_open, mock_requests_get):
    arxiv_url = "https://arxiv.org/e-print/2106.07704"
    path_download = Path("tests/tmp/")

    # Mock requests.get()
    mock_response = Mock()
    mock_response.raw = Mock()
    mock_requests_get.return_value = mock_response

    # Mock tarfile.open()
    mock_opened_tarfile = Mock()
    mock_tarfile_open.return_value.__enter__.return_value = mock_opened_tarfile

    result = download_extract_source(arxiv_url, path_download)
    mock_requests_get.assert_called_once_with(arxiv_url, stream=True, timeout=5)
    mock_tarfile_open.assert_called_once_with(fileobj=mock_response.raw, mode="r|gz")
    mock_opened_tarfile.extractall.assert_called_once_with(path_download)
    assert result[1] == path_download
