from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from rich.table import Table

from reproscreener.repo_eval import (
    check_dependencies,
    check_files,
    check_parsed_readme,
    check_wrapper_scripts,
    clone_repo,
    evaluate_repo,
    repo_eval_table,
)

mock_folder_path = Path("tests/2106.07704")
mock_repo_url = "https://github.com/HanGuo97/soft-Q-learning-for-text-generation"
mock_data = pd.DataFrame(
    {
        "Category": ["Dependencies", "Parsed Readme", "Wrapper Scripts"],
        "Variable": ["pandas", "README.md", "app.py"],
        "Found?": [True, False, True],
        "Extensions": [[".py"], [], [".yaml", ".yml"]],
    }
)


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
    with patch("builtins.input", side_effect=[".txt"]):
        df = evaluate_repo(mock_folder_path)
    assert isinstance(df, pd.DataFrame)


def test_repo_eval_table_input_type():
    with pytest.raises(TypeError):
        repo_eval_table("not a dataframe")


def test_repo_eval_table_correct_input():
    df = pd.DataFrame(
        {
            "Category": ["Dependencies", "Dependencies", "Parsed Readme", "Wrapper Scripts", "Wrapper Scripts"],
            "Variable": ["var1", "var2", "var3", "var4", "var5"],
            "Found?": [True, False, True, False, True],
            "Extensions": [[".txt", ".sh"], [".py"], [".toml", ".csv"], [".xls"], [".txt", ".md"]],
            "Found_Extension": [".txt", "", ".py", "", ".md"],
        }
    )

    table = repo_eval_table(df)

    assert isinstance(table, Table), "The function should return a Table object"
    assert len(table.columns) == 4, "The table should have 4 columns"

    num_category_changes = df["Category"].ne(df["Category"].shift()).sum() - 1
    expected_num_rows = len(df) + num_category_changes

    assert (
        len(table.rows) == expected_num_rows
    ), "The table should have a row for each data frame entry plus additional rows for category changes"


def test_clone_repo(mocker):
    # Mocking the git.Repo.clone_from method to simulate successful cloning
    mocker.patch("git.Repo.clone_from", return_value=True)
    cloned_path = clone_repo(mock_repo_url, mock_folder_path, overwrite=True)
    assert cloned_path  # The returned path should be truthy
