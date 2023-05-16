import glob
import urllib.parse
from pathlib import Path
from typing import Set

import pandas as pd
from flashtext import KeywordProcessor
from rich import print as rprint
from rich.table import Table
from urlextract import URLExtract

from reproscreener import keywords
from reproscreener.utils import log


def combine_tex_in_folder(folder_path: Path) -> Path:
    # Create a combined file of all .tex files in folder_path directory
    combined_path = folder_path / "combined.tex"
    with open(combined_path, "w", encoding="utf-8") as outfile:
        for name in glob.glob(f"{folder_path}/*.tex"):
            with open(name, encoding="utf-8") as infile:
                outfile.write(infile.read())
    return combined_path


def find_tex_variables(combined_path: Path) -> Set:
    """
    Find variables in the combined tex file.
    Uses the `KeywordProcessor` from `flashtext` package to extract variables.
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


def extract_tex_urls(combined_path: Path) -> Set:
    """
    Extract URLs from the combined tex file.
    """
    with open(combined_path, "r", errors="replace", encoding="utf-8") as f:
        data = f.read()
    extractor = URLExtract()
    urls = extractor.find_urls(data)
    log.debug("All urls:\n %s \n", urls)
    return set(urls)


def find_data_repository_links(url_list: Set[str], allowed_domains: list = ["github", "gitlab", "zenodo"]) -> list:
    """
    Find URLs belonging to allowed domains (default - github, gitlab, zenodo).
    """
    found_list = [
        url for url in url_list if any(domain in urllib.parse.urlparse(url).netloc for domain in allowed_domains)
    ]
    for url in found_list:
        log.debug(f"Found {urllib.parse.urlparse(url).netloc} link: {url}")
    return found_list


def initialize_repo_evaluation_table(paper_id: str, title: str, found_vars: Set, found_links: list) -> Table:
    # Create a rich Table object with specified columns and add a row
    table = Table()
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Found Variables", justify="right", style="green")
    table.add_column("Found Links", style="yellow")

    table.add_row(paper_id, title, ", ".join(found_vars), ", ".join(found_links))

    return table
