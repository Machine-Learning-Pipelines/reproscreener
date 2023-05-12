import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from git import Repo
from matplotlib.colors import ListedColormap
from rich import print
from rich.table import Table

from reproscreener.console import console
from reproscreener.repo_downloader import gdrive_get_manual_eval, get_manual_eval_urls


# List directories
def list_directories(path):
    return [d for d in path.iterdir() if d.is_dir()]


# Check dependencies
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
    return [f.name for f in dir_path.glob("*") if f.name in dependency_files]


# Check parsed readme
def check_parsed_readme(dir_path):
    readme_path = dir_path / "README.md"
    if readme_path.is_file():
        with open(readme_path, "r") as file:
            content = file.read()
            headers = re.findall(
                r"^\s*#{1,6}\s*(requirements|dependencies|setup|install)",
                content,
                re.MULTILINE | re.IGNORECASE,
            )
            return ["readme_" + header.lower() for header in headers]
    return []


# Check wrapper scripts
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
    return [f.name for f in dir_path.glob("*") if f.name in wrapper_files]


def main():
    path_corpus = Path("case-studies/arxiv-corpus/mine50-andor")
    repo_path = path_corpus / "repo"
    directories = list_directories(repo_path)

    data = []
    unique_matches_data = []

    for directory in directories:
        dependencies = check_dependencies(directory)
        parsed_readme = check_parsed_readme(directory)
        wrapper_scripts = check_wrapper_scripts(directory)

        data.append([dependencies, parsed_readme, wrapper_scripts])

        # Combine matches from dependencies, parsed_readme, and wrapper_scripts, removing duplicates
        unique_matches = list(set(dependencies + parsed_readme + wrapper_scripts))

        # If unique_matches is empty, set it to "Code provided but no matches"
        if not unique_matches:
            unique_matches = ["Code provided but no matches"]

        unique_matches_data.append((directory.name, ", ".join(unique_matches)))

    df = pd.DataFrame(
        data,
        columns=["Dependencies", "Parsed Readme", "Wrapper Scripts"],
        index=[d.name for d in directories],
    )

    # Convert unique_matches_data to a dictionary
    unique_matches_dict = {
        directory: matches for directory, matches in unique_matches_data
    }

    # Create a DataFrame from the dictionary
    unique_matches_df = pd.DataFrame.from_dict(
        unique_matches_dict, orient="index", columns=["Matches"]
    )
    unique_matches_df.to_csv(path_corpus / "output/unique_matches.csv")
    return df, unique_matches_df


def display_dataframe(df: pd.DataFrame, title: str):
    table = Table(show_header=True, header_style="bold magenta", title=title)

    # Add index column
    table.add_column("Paper")
    for col_name in df.columns:
        table.add_column(col_name)

    # Add rows with index
    for idx, row in df.iterrows():
        table.add_row(str(idx), *row.map(str).tolist())

    console.print(table)


def download_repo(repo_url: str, path_corpus: Path, paper_id: str, overwrite=False):
    # console = Console()
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


def evaluate_repo(path_corpus):
    path_corpus = Path(path_corpus)
    repo_path = path_corpus / "repo"
    directories = list_directories(repo_path)

    data = []
    unique_matches_data = []

    for directory in directories:
        dependencies = check_dependencies(directory)
        parsed_readme = check_parsed_readme(directory)
        wrapper_scripts = check_wrapper_scripts(directory)

        data.append([dependencies, parsed_readme, wrapper_scripts])

        # Combine matches from dependencies, parsed_readme, and wrapper_scripts, removing duplicates
        unique_matches = list(set(dependencies + parsed_readme + wrapper_scripts))

        # If unique_matches is empty, set it to "Code provided but no matches"
        if not unique_matches:
            unique_matches = ["Code provided but no matches"]

        unique_matches_data.append((directory.name, ", ".join(unique_matches)))

    df = pd.DataFrame(
        data,
        columns=["Dependencies", "Parsed Readme", "Wrapper Scripts"],
        index=[d.name for d in directories],
    )

    # Convert unique_matches_data to a dictionary
    unique_matches_dict = {
        directory: matches for directory, matches in unique_matches_data
    }

    # Create a DataFrame from the dictionary
    unique_matches_df = pd.DataFrame.from_dict(
        unique_matches_dict, orient="index", columns=["Matches"]
    )
    Path(path_corpus / "output").mkdir(parents=True, exist_ok=True)
    unique_matches_df.to_csv(path_corpus / "output/unique_matches.csv")
    return df, unique_matches_df


def create_binary_matrix(unique_matches_df: pd.DataFrame) -> pd.DataFrame:
    unique_matches = []
    for matches in unique_matches_df["Matches"]:
        unique_matches.extend(matches.split(", "))

    unique_matches = list(set(unique_matches))

    binary_data = []
    for _, row in unique_matches_df.iterrows():
        matches = row["Matches"].split(", ")
        binary_row = [1 if match in matches else 0 for match in unique_matches]
        binary_data.append(binary_row)

    binary_df = pd.DataFrame(
        binary_data, columns=unique_matches, index=unique_matches_df.index
    ).T
    return binary_df


def merge_with_manual(binary_df: pd.DataFrame, manual_path: Path) -> pd.DataFrame:
    manual = pd.read_csv(manual_path)
    manual_papers = set(manual["paper"])

    # remove Papers and Totals from the manual_papers set
    manual_papers.remove("Paper")
    manual_papers.remove("Totals")

    # Add empty matches for papers in manual that are not in binary_df
    for paper in manual_papers:
        if paper not in binary_df.columns:
            binary_df[paper] = 0

    # Update the index with the new column order
    binary_df = binary_df.reindex(sorted(binary_df.columns), axis=1)

    return binary_df


def plot_heatmap_test(binary_df: pd.DataFrame, palette):
    custom_cmap = ListedColormap(palette)

    sns.heatmap(binary_df, cmap=custom_cmap, cbar=False)


def plot_heatmap(binary_df: pd.DataFrame):
    #                                   (empty, filled)
    custom_cmap = ListedColormap(["#FFF0F0", "#E74C3C"])

    plt.figure(figsize=(12, 4), tight_layout={"pad": 1.5})
    sns.set_style("whitegrid")
    sns.heatmap(binary_df, cmap=custom_cmap, cbar=False)
    # plt.xlabel("Directories")
    # plt.ylabel("Matches")
    # plt.title("Heatmap of Unique Matches")
    plt.subplots_adjust(top=0.95, left=0.15, right=0.95)
    plt.savefig("heatmap_repo.png", dpi=1500, bbox_inches="tight")
    plt.show()


def test_color_palettes(binary_df: pd.DataFrame):
    color_palettes = [
        ["#5E626E", "#73FBD3"],
        ["#4C4E4F", "#DB2B39"],
        ["#2E86AB", "#EEAA7B"],
        ["#3C3E3F", "#F1C40F"],
        ["#EB984E", "#3498DB"],
        ["#A93226", "#1F618D"],
        ["#566573", "#D4AC0D"],
        ["#7B241C", "#633974"],
        ["#73C6B6", "#5D6D7E"],
        ["#1E8449", "#F39C12"],
    ]
    binary_color_palettes = [
        ["#F0EFEF", "#FF6B6B"],  # light red and red
        ["#EFF7F7", "#4ECDC4"],  # light turquoise and turquoise
        ["#F0FFF0", "#1A535C"],  # light teal and dark teal
        ["#F0F0F0", "#2ECC71"],  # light gray and green
        ["#F0F0FF", "#5E2E88"],  # light purple and purple
        ["#FFFFF0", "#F1C40F"],  # light yellow and yellow
        ["#F0F8FF", "#2980B9"],  # light blue and blue
        ["#FFF0F0", "#E74C3C"],  # light pink and red
        ["#FFF0FF", "#E56B6F"],  # light pink and pink
        ["#F5F0F0", "#6D4C41"],  # light brown and brown
    ]

    plt.figure(figsize=(15, 15))
    for i, palette in enumerate(binary_color_palettes, start=1):
        plt.subplot(4, 3, i)
        plot_heatmap_test(binary_df, palette)

    plt.subplots_adjust(top=0.95, left=0.15, right=0.95)
    plt.savefig("heatmap_repo_palettes.png", dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    path_corpus = Path("case-studies/arxiv-corpus/mine50-andor")
    manual_path = path_corpus / "manual_eval.csv"

    df, unique_matches_df = main()
    display_dataframe(df, title="Matches")
    display_dataframe(unique_matches_df, title="All unique matches")
    binary_df = create_binary_matrix(unique_matches_df)

    # Merge with manual
    binary_df = merge_with_manual(binary_df, manual_path)
    # print(binary_df)

    test_color_palettes(binary_df)

    plot_heatmap(binary_df)
