import logging

from rich.console import Console
from rich.logging import RichHandler
import tarfile
from pathlib import Path
from typing import Tuple

import feedparser
import requests
from rich.style import Style
from rich.text import Text

console = Console(
    quiet=False,
)


FORMAT = "%(message)s"
logging.basicConfig(
    level="WARNING",  # "NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)

log = logging.getLogger("rich")

ext_mapping = {
    "Dependencies": {
        "Dockerfile": [],
        "requirements": [".txt"],
        "setup": [".py"],
        "environment": [".yml"],
        "Pipfile": [],
        "pyproject": [".toml"],
        "pip_reqs": [".txt"],
        "conda_reqs": [".txt"],
    },
    "Wrapper Scripts": {
        "run": [".py", ".sh"],
        "main": [".py", ".sh"],
        "run_all": [".py", ".sh"],
        "run_experiments": [".py", ".sh"],
        "MAKEFILE": [],
        "Makefile": [],
        "Dockerfile": [],
    },
    "Parsed Readme": {
        "readme_requirements": [""],
        "readme_dependencies": [""],
        "readme_setup": [""],
        "readme_install": [""],
    },
    "Others": {
        "No code provided": [""],
        "Code provided but no matches": [""],
    },
}

# Create the reverse mapping
reverse_mapping = {
    file + ext: category
    for category, files in ext_mapping.items()
    for file, extensions in files.items()
    for ext in extensions
}

labels_mapping = {
    "experiment_setup": "Experimental setup",
    "hypothesis": "Hypothesis",
    "method_source_code": "Method source code",
    "objective": "Objective/Goal",
    "prediction": "Prediction",
    "problem": "Research problem",
    "pseudocode": "Pseudocode",
    "research_method": "Research method",
    "research_questions": "Research questions",
    "test_data": "Test data",
    "training_data": "Training data",
    "validation_data": "Validation data",
}


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
