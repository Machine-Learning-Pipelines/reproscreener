import glob
import urllib.parse
from pathlib import Path
from typing import List, Set

from flashtext import KeywordProcessor
from rich.table import Table
from urlextract import URLExtract

from reproscreener import keywords
from reproscreener.utils import log


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


def initialize_repo_evaluation_table(paper_id: str, title: str, found_vars: Set[str], found_links: List[str]) -> Table:
    """
    Initialize a rich Table object with specified columns and add a row.

    Args:
        paper_id (str): ID of the paper.
        title (str): Title of the paper.
        found_vars (Set[str]): Set of found variables.
        found_links (List[str]): List of found URLs.

    Returns:
        Table: Initialized Table object.
    """
    table = Table()
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Found Variables", justify="right", style="green")
    table.add_column("Found Links", style="yellow")

    table.add_row(paper_id, title, ", ".join(found_vars), ", ".join(found_links))

    return table
