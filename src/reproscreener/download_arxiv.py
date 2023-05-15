import tarfile
from pathlib import Path

import requests
from rich import print as rprint
from reproscreener.utils import console


def download_extract_source(arxiv_url, path_download) -> Path:
    paper_id = arxiv_url.split("/")[-1]

    with console.status("[bold green]Downloading and processing paper..."):
        response = requests.get(arxiv_url, stream=True, timeout=5)
        with tarfile.open(fileobj=response.raw, mode="r|gz") as tar:
            tar.extractall(path_download)

    rprint("Downloaded source:", arxiv_url, "to", path_download)
    rprint("Paper ID:", paper_id)
    return path_download
