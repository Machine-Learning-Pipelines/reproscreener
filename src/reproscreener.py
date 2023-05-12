```
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

if __name__ == "__main__":
    path_corpus = Path("case-studies/arxiv-corpus/mine50-andor")
    manual_path = path_corpus / "manual_eval.csv"

    df, unique_matches_df = main()
    display_dataframe(df, title="Matches")
    display_dataframe(unique_matches_df, title="All unique matches")
```