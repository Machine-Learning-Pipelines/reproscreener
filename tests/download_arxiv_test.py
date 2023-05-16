import tarfile
from pathlib import Path
from unittest.mock import Mock

import requests

from reproscreener.download_arxiv import download_extract_source


def test_download_extract_source(mocker):
    arxiv_url = "https://arxiv.org/e-print/2106.07704"
    path_download = Path("tests/tmp/")

    # Mock requests.get()
    mock_get_patcher = mocker.patch("requests.get")
    mock_response = Mock()
    mock_response.raw = Mock()
    mock_get_patcher.return_value = mock_response

    # Mock tarfile.open()
    mock_tarfile = mocker.MagicMock()
    mock_opened_tarfile = mocker.MagicMock()
    mock_tarfile.__enter__.return_value = mock_opened_tarfile
    mocker.patch("tarfile.open", return_value=mock_tarfile)

    result = download_extract_source(arxiv_url, path_download)
    mock_get_patcher.assert_called_once_with(arxiv_url, stream=True, timeout=5)
    mock_opened_tarfile.extractall.assert_called_once_with(path_download)
    assert result == path_download
