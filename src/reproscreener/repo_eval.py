import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from git import Repo
from matplotlib.colors import ListedColormap
from rich import box, print
from rich.console import Console
from rich.style import Style
from rich.table import Table

from reproscreener.utils import console
from reproscreener.repo_downloader import gdrive_get_manual_eval, get_manual_eval_urls


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


def list_directories(path):
    return [d for d in path.iterdir() if d.is_dir()]


def check_files(dir_path, files):
    found_files = []
    not_found_files = list(files)

    for f in dir_path.glob("*"):
        if f.stem in files:
            if f.suffix in ext_mapping.get(f.stem, [""]):
                found_files.append(f.name)
                not_found_files.remove(f.stem)

    return found_files, not_found_files


def check_dependencies(dir_path):
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


def check_wrapper_scripts(dir_path):
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


def check_parsed_readme(dir_path):
    readme_path = dir_path / "README.md"
    possible_headers = ["requirements", "dependencies", "setup", "install"]
    if readme_path.is_file():
        with open(readme_path, "r") as file:
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


def evaluate_repo(path_corpus):
    path_corpus = Path(path_corpus)
    repo_path = path_corpus / "repo"
    directories = list_directories(repo_path)

    data = []

    for directory in directories:
        dependencies_found, dependencies_not_found = check_dependencies(directory)
        parsed_readme_found, parsed_readme_not_found = check_parsed_readme(directory)
        wrapper_scripts_found, wrapper_scripts_not_found = check_wrapper_scripts(
            directory
        )

        categories = ["Dependencies", "Parsed Readme", "Wrapper Scripts"]
        found_lists = [dependencies_found, parsed_readme_found, wrapper_scripts_found]
        not_found_lists = [
            dependencies_not_found,
            parsed_readme_not_found,
            wrapper_scripts_not_found,
        ]

        for category, found_items, not_found_items in zip(
            categories, found_lists, not_found_lists
        ):
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

    df = pd.DataFrame(
        data,
        columns=["Category", "Item", "Found", "Extensions", "Found_Extension"],
    )

    return df


def display_dataframe(df, title=""):
    for category, group in df.groupby("Category"):
        table = Table(title=f"{title} - {category}")
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
                    f"[green]{ext}[/green]"
                    if ext == found_extension
                    else f"[red]{ext}[/red]"
                    for ext in extensions
                )

            found_str = "[green]Found[/green]" if found else "[red]Not Found[/red]"
            table.add_row(item, found_str, ext_color_str)

        console.print(table)
        console.print("\n")


def download_repo(repo_url: str, path_corpus: Path, paper_id: str, overwrite=False):
    path_paper = path_corpus / "repo" / paper_id
    path_exists = path_paper.is_dir()

    if path_exists and not overwrite:
        console.print(
            f"Repo directory already exists: {path_paper}, use the overwrite flag to download"
        )
        return

    Path(path_paper).mkdir(parents=True, exist_ok=True)

    try:
        with console.status("Cloning repo...", spinner="dots"):
            Repo.clone_from(repo_url, path_paper)
        console.print(f"Successfully cloned repo: {repo_url}")
    except Exception as e:
        console.print(f"Failed to clone repo: {repo_url}. Error: {e}")
