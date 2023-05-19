import tarfile
from pathlib import Path
from typing import Tuple

import feedparser
import requests
from rich.style import Style
from rich.text import Text

path_style = Style(underline=True)

from reproscreener.utils import console


def download_extract_source(arxiv_url: str, path_download: Path) -> Tuple[str, Path]:
    """
    Downloads and extracts the source code of an ArXiv paper from its URL.
    Also retrieves the paper title from the arXiv API.
    Returns the paper title and the download directory path.
    """
    arxiv_id = arxiv_url.split("/")[-1]
    if "v" in arxiv_id:
        arxiv_id = arxiv_id.split("v")[0]

    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    feed = feedparser.parse(api_url)
    title = feed.entries[0].title

    with console.status("[bold green]Downloading and processing paper..."):
        source_url = f"https://arxiv.org/e-print/{arxiv_id}"
        response = requests.get(source_url, stream=True, timeout=5)
        with tarfile.open(fileobj=response.raw, mode="r|gz") as tar:
            tar.extractall(path_download)

    source_text = Text.assemble(
        "Downloaded source: ",
        Text(source_url, style=Style(underline=True, color="cyan", link=True)),
        " to ",
        Text(str(path_download), Style(underline=True, color="blue")),
    )
    console.print(source_text)
    return title, path_download
