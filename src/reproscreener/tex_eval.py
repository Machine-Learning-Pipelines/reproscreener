import glob
import urllib.parse
from pathlib import Path
from typing import List, Set

from flashtext import KeywordProcessor
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text
from urlextract import URLExtract
import pandas as pd

from reproscreener import keywords
from reproscreener.utils import console, log


def combine_tex_in_folder(folder_path: Path) -> Path:
    """
    Combine all .tex files in a given directory into a single file.

    Args:
        folder_path (Path): Path to the directory containing .tex files.

    Returns:
        Path: Path to the combined .tex file.
    """
    # Create a combined file of all .tex files in folder_path directory
    combined_path = folder_path / "combined.tex"
    with open(combined_path, "w", encoding="utf-8") as outfile:
        for name in glob.glob(f"{folder_path}/*.tex"):
            with open(name, encoding="utf-8") as infile:
                outfile.write(infile.read())
    return combined_path


def find_tex_variables(combined_path: Path) -> Set[str]:
    """
    Find variables in the combined tex file.
    Uses the `KeywordProcessor` from `flashtext` package to extract variables.

    Args:
        combined_path (Path): Path to the combined .tex file.

    Returns:
        Set[str]: Set of found variables.
    """
    keyword_dict = keywords.generate_gunderson_dict()
    keyword_processor = KeywordProcessor(case_sensitive=True)
    keyword_processor.add_keywords_from_dict(keyword_dict)
    with open(combined_path, "r", errors="replace", encoding="utf-8") as f:
        data = f.readlines()
        all_found = [keyword_processor.extract_keywords(line, span_info=True) for line in data]
        non_empty_found = [x for x in all_found if x != []]
        # Using set comprehension to avoid duplicates
        found_vars = {j[0] for i in non_empty_found for j in i}
    return found_vars


def extract_tex_urls(combined_path: Path) -> Set[str]:
    """
    Extract URLs from the combined tex file.

    Args:
        combined_path (Path): Path to the combined .tex file.

    Returns:
        Set[str]: Set of found URLs.
    """
    with open(combined_path, "r", errors="replace", encoding="utf-8") as f:
        data = f.read()
    extractor = URLExtract()
    urls = extractor.find_urls(data)
    log.debug("All urls:\n %s \n", urls)
    return set(urls)


def find_data_repository_links(
    url_list: Set[str], allowed_domains: List[str] = ["github", "gitlab", "zenodo"]
) -> List[str]:
    """
    Find URLs belonging to allowed domains (default - github, gitlab, zenodo).

    Args:
        url_list (Set[str]): Set of URLs to process.
        allowed_domains (List[str], optional): List of allowed domain names. Defaults to ["github", "gitlab", "zenodo"].

    Returns:
        List[str]: List of found URLs belonging to allowed domains.
    """
    found_list = [
        url for url in url_list if any(domain in urllib.parse.urlparse(url).netloc for domain in allowed_domains)
    ]
    for url in found_list:
        log.debug(f"Found {urllib.parse.urlparse(url).netloc} link: {url}")
    return found_list


def paper_evaluation_results(
    paper_id: str, title: str, found_vars: Set[str], found_links: List[str]
) -> (pd.DataFrame, Panel):
    """
    Create a rich Panel with the results of the paper evaluation.

    Args
        paper_id (str): ID of the paper.
        title (str): Title of the paper.
        found_vars (Set[str]): Set of found variables.
        found_links (List[str]): List of found URLs.
    """
    if not isinstance(paper_id, str):
        raise TypeError(f"Expected paper_id to be str, got {type(paper_id).__name__}.")
    if not isinstance(title, str):
        raise TypeError(f"Expected title to be str, got {type(title).__name__}.")
    if not isinstance(found_vars, set):
        raise TypeError(f"Expected found_vars to be set, got {type(found_vars).__name__}.")
    if not isinstance(found_links, list):
        raise TypeError(f"Expected found_links to be list, got {type(found_links).__name__}.")

    result_text = Text.assemble(
        ("\nPaper ID: ", "bold cyan"),
        (paper_id, "bold yellow"),
        ("\n\nTitle: ", "bold cyan"),
        (title, "bold yellow"),
        ("\n\nFound Variables:\n", "bold cyan"),
        *[(f"- {var}\n", "green") for var in found_vars],
        ("\nFound Links:\n", "bold cyan"),
    )
    for link in found_links:
        result_text.append(f"- ", style="bold cyan")
        result_text.append(link, style=Style(link=True, underline=True, color="blue"))
        result_text.append("\n")  # Add newline after each link

    result_panel = Panel(
        result_text,
        title=Text.assemble((f"Paper Evaluation: {paper_id}", "bold magenta")),
        box=box.ROUNDED,
        expand=False,
    )

    result_dataframe = pd.DataFrame(
        {
            "Paper ID": [paper_id],
            "Found Variables": [", ".join(found_vars)],
            "Found Links": [", ".join(found_links)],
        }
    )

    return result_panel, result_dataframe
