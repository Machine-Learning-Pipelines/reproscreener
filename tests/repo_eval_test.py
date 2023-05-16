from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

from reproscreener.repo_eval import (
    check_dependencies,
    check_files,
    check_parsed_readme,
    check_wrapper_scripts,
    clone_repo,
    display_dataframe,
    evaluate_repo,
)

mock_folder_path = Path("tests/2106.07704")
mock_repo_url = "https://github.com/HanGuo97/soft-Q-learning-for-text-generation"


def test_check_files():
    mock_files = ["file1", "file2"]
    found_files, not_found_files = check_files(mock_folder_path, mock_files)
    assert isinstance(found_files, list)  # The result should be a list
    assert isinstance(not_found_files, list)  # The result should be a list


def test_check_dependencies():
    found_files, not_found_files = check_dependencies(mock_folder_path)
    assert isinstance(found_files, list)  # The result should be a list
    assert isinstance(not_found_files, list)  # The result should be a list


def test_check_wrapper_scripts():
    found_files, not_found_files = check_wrapper_scripts(mock_folder_path)
    assert isinstance(found_files, list)  # The result should be a list
    assert isinstance(not_found_files, list)  # The result should be a list


def test_check_parsed_readme():
    found_headers, not_found_headers = check_parsed_readme(mock_folder_path)
    assert isinstance(found_headers, list)  # The result should be a list
    assert isinstance(not_found_headers, list)  # The result should be a list


def test_evaluate_repo():
    df = evaluate_repo(mock_folder_path)
    assert isinstance(df, pd.DataFrame)  # The result should be a DataFrame


def test_display_dataframe():
    mock_df = pd.DataFrame(
        [["Category", "Item", True, [".txt"], ".txt"]],
        columns=["Category", "Item", "Found", "Extensions", "Found_Extension"],
    )
    display_dataframe(mock_df, "Test Title")


def test_clone_repo(mocker):
    # Mocking the git.Repo.clone_from method to simulate successful cloning
    mocker.patch("git.Repo.clone_from", return_value=True)
    cloned_path = clone_repo(mock_repo_url, mock_folder_path, overwrite=True)
    assert cloned_path  # The returned path should be truthy
