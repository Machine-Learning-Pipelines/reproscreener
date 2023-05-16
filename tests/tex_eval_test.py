from pathlib import Path

import pandas as pd
import pytest
from rich.table import Table

from reproscreener.tex_eval import (
    combine_tex_in_folder,
    extract_tex_urls,
    find_data_repository_links,
    find_tex_variables,
    initialize_repo_evaluation_table,
)

mock_folder_path = Path("./case-studies/arxiv-corpus/mine50-andor/source/1606.04671")
mock_allowed_domains = ["github", "gitlab", "zenodo"]
mock_df = pd.DataFrame([{"id": "1", "title": "title", "found_vars": set(), "found_links": []}])


def test_combine_tex_in_folder():
    combined_path = combine_tex_in_folder(mock_folder_path)
    assert combined_path.exists()  # The file should exist
    assert combined_path.is_file()  # It should be a file


def test_find_tex_variables():
    combined_path = mock_folder_path / "combined.tex"
    found_vars = find_tex_variables(combined_path)
    assert isinstance(found_vars, set)  # The result should be a set


def test_extract_tex_urls():
    combined_path = mock_folder_path / "combined.tex"
    urls = extract_tex_urls(combined_path)
    assert isinstance(urls, set)  # The result should be a set


def test_find_data_repository_links():
    mock_urls = set(["https://github.com/user/repo", "https://notallowed.com"])
    found_links = find_data_repository_links(mock_urls, mock_allowed_domains)
    assert isinstance(found_links, list)  # The result should be a list
    assert len(found_links) == 1  # Only one link is from the allowed domains
    assert "https://github.com/user/repo" in found_links  # The allowed link should be in the result


def test_initialize_repo_evaluation_table():
    table = initialize_repo_evaluation_table(paper_id="1", title="title", found_vars=set(), found_links=[])
    assert isinstance(table, Table)  # The result should be a Table
    assert len(table.rows) == 1  # The table should have one row
