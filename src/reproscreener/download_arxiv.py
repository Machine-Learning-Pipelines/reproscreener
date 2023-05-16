import tarfile
from pathlib import Path

import requests
from rich import print as rprint

from reproscreener.utils import console


def download_extract_source(arxiv_url: str, path_download: Path) -> Path:
    """
    Downloads and extracts the source code of an ArXiv paper from its URL.
    Returns the download directory path.
    """
    with console.status("[bold green]Downloading and processing paper..."):
        response = requests.get(arxiv_url, stream=True, timeout=5)
        with tarfile.open(fileobj=response.raw, mode="r|gz") as tar:
            tar.extractall(path_download)

    rprint(f"Downloaded source: {arxiv_url} to {path_download}")
    return path_download
