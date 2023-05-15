import tarfile
from pathlib import Path

import requests
from rich import print as rprint
from reproscreener.utils import console


def download_extract_source(arxiv_url, path_download) -> Path:
    paper_id = arxiv_url.split("/")[-1]
    path_paper = Path(path_download) / paper_id
    path_paper.mkdir(parents=True, exist_ok=True)

    with console.status("[bold green]Downloading and processing paper..."):
        response = requests.get(arxiv_url, stream=True, timeout=5)
        with tarfile.open(fileobj=response.raw, mode="r|gz") as tar:
            tar.extractall(path_paper)

    rprint("Downloaded source:", arxiv_url, "to", path_paper)
    rprint("Paper ID:", paper_id)
    return path_paper
