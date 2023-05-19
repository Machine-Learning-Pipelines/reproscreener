from pathlib import Path
from typing import List, Set

import pandas as pd
import pytest
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from reproscreener.tex_eval import (
    combine_tex_in_folder,
    extract_tex_urls,
    find_data_repository_links,
    find_tex_variables,
    paper_evaluation_results,
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


def test_paper_evaluation_results_input_type():
    # Test that a TypeError is raised when input types are not as expected
    with pytest.raises(TypeError):
        paper_evaluation_results(123, "title", set(), list())  # paper_id is not str
    with pytest.raises(TypeError):
        paper_evaluation_results("paper_id", 123, set(), list())  # title is not str
    with pytest.raises(TypeError):
        paper_evaluation_results("paper_id", "title", list(), list())  # found_vars is not set
    with pytest.raises(TypeError):
        paper_evaluation_results("paper_id", "title", set(), set())  # found_links is not list


def test_paper_evaluation_results_correct_input():
    # Test that the function completes successfully with correct input
    paper_id = "123"
    title = "Title"
    found_vars = {"var1", "var2", "var3"}
    found_links = ["http://example.com", "http://example.org"]

    # Now we can check the structure of the output
    panel = paper_evaluation_results(paper_id, title, found_vars, found_links)

    assert isinstance(panel, Panel), "The function should return a Panel object"

    # Check that the Panel contains the correct text
    expected_text = Text.assemble(
        ("\nPaper ID: ", "bold cyan"),
        (paper_id, "bold yellow"),
        ("\n\nTitle: ", "bold cyan"),
        (title, "bold yellow"),
        ("\n\nFound Variables:\n", "bold cyan"),
        *[(f"- {var}\n", "green") for var in found_vars],
        ("\nFound Links:\n", "bold cyan"),
    )
    for link in found_links:
        expected_text.append(f"- ", style="bold cyan")
        expected_text.append(link, style=Style(link=True, underline=True, color="blue"))
        expected_text.append("\n")  # Add newline after each link

    assert panel.renderable == expected_text, "The Panel should contain the expected text"
