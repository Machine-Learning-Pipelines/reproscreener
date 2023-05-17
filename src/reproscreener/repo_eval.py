import re
from pathlib import Path
from typing import List, Tuple

import git
import pandas as pd
from rich.table import Table

from reproscreener.utils import console

ext_mapping = {
    "run": [".py", ".sh"],
    "main": [".py", ".sh"],
    "run_all": [".py", ".sh"],
    "run_experiments": [".py", ".sh"],
    "Dockerfile": [],
    "requirements": [".txt"],
    "setup": [".py"],
    "environment": [".yml"],
    "Pipfile": [],
    "pyproject": [".toml"],
    "pip_reqs": [".txt"],
    "conda_reqs": [".txt"],
    "MAKEFILE": [],
    "Makefile": [],
    "readme_requirements": [],
    "readme_dependencies": [],
    "readme_setup": [],
    "readme_install": [],
}


def check_files(dir_path: Path, files: List[str]) -> Tuple[List[str], List[str]]:
    """
    Check if the given files exist in the directory.

    Args:
        dir_path (Path): Path to the directory to check.
        files (List[str]): List of filenames to look for.

    Returns:
        Tuple[List[str], List[str]]: Two lists containing the found files and not found files.
    """
    found_files = []
    not_found_files = list(files)

    for f in dir_path.glob("*"):
        if f.stem in files:
            if f.suffix in ext_mapping.get(f.stem, [""]):
                found_files.append(f.name)
                not_found_files.remove(f.stem)

    return found_files, not_found_files


def check_dependencies(dir_path: Path) -> Tuple[List[str], List[str]]:
    """
    Check if the necessary dependency files exist in the directory.

    Args:
        dir_path (Path): Path to the directory to check.

    Returns:
        Tuple[List[str], List[str]]: Two lists containing the found dependency files and not found dependency files.
    """
    dependency_files = [
        "Dockerfile",
        "requirements",
        "setup.py",
        "environment",
        "Pipfile",
        "pyproject.toml",
        "pip_reqs",
        "conda_reqs",
    ]
    return check_files(dir_path, dependency_files)


def check_wrapper_scripts(dir_path: Path) -> Tuple[List[str], List[str]]:
    """
    Check if the necessary wrapper script files exist in the directory.

    Args:
        dir_path (Path): Path to the directory to check.

    Returns:
        Tuple[List[str], List[str]]: Two lists containing the found wrapper script files and not found wrapper script files.
    """
    wrapper_files = [
        "run",
        "main",
        "run_all",
        "run_experiments",
        "MAKEFILE",
        "Makefile",
        "Dockerfile",
    ]
    return check_files(dir_path, wrapper_files)


def check_parsed_readme(dir_path: Path) -> Tuple[List[str], List[str]]:
    """
    Check if the necessary sections exist in the README file.

    Args:
        dir_path (Path): Path to the directory to check.

    Returns:
        Tuple[List[str], List[str]]: Two lists containing the found sections and not found sections.
    """
    readme_path = dir_path / "README.md"
    possible_headers = ["requirements", "dependencies", "setup", "install"]
    if readme_path.is_file():
        with open(readme_path, "r", encoding="utf-8") as file:
            content = file.read()
            found_headers = re.findall(
                r"^\s*#{1,6}\s*(" + "|".join(possible_headers) + ")",
                content,
                re.MULTILINE | re.IGNORECASE,
            )
            found_headers = [header.lower() for header in found_headers]
            not_found_headers = list(set(possible_headers) - set(found_headers))
            return ["readme_" + header for header in found_headers], [
                "readme_" + header for header in not_found_headers
            ]
    return [], possible_headers


def evaluate_repo(path_corpus: Path) -> pd.DataFrame:
    """
    Evaluate a repository by checking the existence of certain files and sections in README.

    Args:
        path_corpus (Path): Path to the repository.

    Returns:
        pd.DataFrame: A DataFrame with the evaluation results.
    """
    if (path_corpus / "repo").is_dir():
        repo_path = path_corpus / "repo"
    else:
        repo_path = path_corpus

    dependencies_found, dependencies_not_found = check_dependencies(repo_path)
    parsed_readme_found, parsed_readme_not_found = check_parsed_readme(repo_path)
    wrapper_scripts_found, wrapper_scripts_not_found = check_wrapper_scripts(repo_path)

    categories = ["Dependencies", "Parsed Readme", "Wrapper Scripts"]
    found_lists = [dependencies_found, parsed_readme_found, wrapper_scripts_found]
    not_found_lists = [
        dependencies_not_found,
        parsed_readme_not_found,
        wrapper_scripts_not_found,
    ]

    data = []

    for category, found_items, not_found_items in zip(categories, found_lists, not_found_lists):
        for item in found_items:
            item_path = Path(item)
            item_base_name = item_path.stem
            found_extension = item_path.suffix
            data.append(
                [
                    category,
                    item_base_name,
                    True,
                    ext_mapping.get(item_base_name, []),
                    found_extension,
                ]
            )
        for item in not_found_items:
            data.append([category, item, False, ext_mapping.get(item, []), ""])

    return pd.DataFrame(
        data,
        columns=["Category", "Item", "Found", "Extensions", "Found_Extension"],
    )


def display_dataframe(df_table: pd.DataFrame, title: str = ""):
    """
    Display a DataFrame as a rich table in console.

    Args:
        df_table (pd.DataFrame): DataFrame to display.
        title (str, optional): Title of the table. Defaults to "".
    """
    for category, group in df_table.groupby("Category"):
        table = Table(title=f"{category}")
        table.add_column("Item")
        table.add_column("Found")
        table.add_column("Extensions")

        for _, row in group.iterrows():
            item = row["Item"]
            found = row["Found"]
            extensions = row["Extensions"]
            found_extension = row["Found_Extension"]

            if not extensions:
                ext_color_str = ""
            else:
                ext_color_str = ", ".join(
                    f"[green]{ext}[/green]" if ext == found_extension else f"[red]{ext}[/red]" for ext in extensions
                )

            found_str = "[green]Found[/green]" if found else "[red]Not Found[/red]"
            table.add_row(item, found_str, ext_color_str)

        console.print(table)
        console.print("\n")


def clone_repo(repo_url: str, path_corpus: Path, overwrite: bool = False) -> Path:
    """
    Clone a repository from the given URL to the given path. If the repository already exists, it won't be overwritten unless specified.

    Args:
        repo_url (str): URL of the repository to clone.
        path_corpus (Path): Path to clone the repository to.
        overwrite (bool, optional): Whether to overwrite the existing repository. Defaults to False.

    Returns:
        Path: Path to the cloned repository. Returns False if cloning fails.
    """
    path_exists = path_corpus.is_dir()

    if path_exists and not overwrite:
        console.print(f"Repo directory already exists: {path_corpus}, use the overwrite flag to download\n")
        return path_corpus

    path_corpus.mkdir(parents=True, exist_ok=True)
    repo_name = repo_url.split("/")[-1].split(".git")[0]
    cloned_path = path_corpus / repo_name

    try:
        with console.status("Cloning repo...", spinner="dots"):
            git.Repo.clone_from(repo_url, cloned_path)
            console.print(f"Successfully cloned repo: {repo_url}\n")
            return cloned_path
    except git.exc.CommandError as error:
        console.print(f"Failed to clone repo: {repo_url}. Error: {error}\n")
        return False
