from pathlib import Path
from console import console
from markdown_it import MarkdownIt
from bs4 import BeautifulSoup
import numpy as np
import re
import glob


def only_found_dict_vals(d, only_found):
    if only_found:
        out = {k: v for k, v in d.items() if v}
    else:
        out = d
    if out:
        return out
    return dict()


def check_exists_file_names(path_paper, file_names, only_found=False):
    exists = {file_name: False for file_name in file_names}
    for file in path_paper.iterdir():
        if file.is_file():
            try:
                found_index = file_names.index(file.stem)
            except ValueError:
                found_index = -1
                exists[file.stem] = False
            if found_index != -1:
                exists[file.stem] = True

    return only_found_dict_vals(exists, only_found)


def get_downloaded_repos(path_corpus):
    path_repos = path_corpus / "repo"
    downloaded_repos = [p.name for p in path_repos.iterdir() if p.is_dir()]
    return sorted(downloaded_repos)


def check_dependencies(path_corpus, paper, only_found=False):
    path_paper = path_corpus / "repo" / paper
    file_names = [
        "Dockerfile",
        "requirements",
        "setup.py",
        "environment",
        "Pipfile",
        "pyproject.toml",
        "pip_reqs",
        "conda_reqs",
    ]

    return check_exists_file_names(path_paper, file_names, only_found=only_found)


def check_reproducibility_scripts(path_corpus, paper, only_found=False):
    path_paper = path_corpus / "repo" / paper
    file_names = ["plots", "run_experiments"]

    return check_exists_file_names(path_paper, file_names, only_found=only_found)


def parse_readme(path_corpus, paper, only_found=False):
    path_readme = path_corpus / "repo" / paper / "README.md"
    checks = ["requirements", "dependencies", "setup", "install"]
    if Path(path_readme).is_file():
        with open(path_readme, "r") as f:
            readme = f.read()
            md = MarkdownIt("gfm-like")
            html = md.render(readme)
            soup = BeautifulSoup(html, "lxml")
            headings = soup.find_all(re.compile("^h[1-6]$"))
            exists = {
                check: any(check in heading.text.lower() for heading in headings)
                for check in checks
            }
            return only_found_dict_vals(exists, only_found)
    return dict()


def check_wrapper_script(path_corpus, paper, only_found=False):
    path_paper = path_corpus / "repo" / paper
    file_names = [
        "run",
        "main",
        "run_all",
        "run_experiments",
        "MAKEFILE",
        "Makefile",
        "Dockerfile",
    ]

    return check_exists_file_names(path_paper, file_names, only_found=only_found)


def all_checks_by_paper(path_corpus, paper, only_found=False):
    checks = {
        "wrapper_script": check_wrapper_script(
            path_corpus, paper, only_found=only_found
        ),
        "software_dependencies": check_dependencies(
            path_corpus, paper, only_found=only_found
        ),
        "parsed_readme": parse_readme(path_corpus, paper, only_found=only_found),
    }
    return only_found_dict_vals(checks, only_found)


def tally_checks_by_paper(path_corpus, paper, only_found=False, verbose=False):
    checks = all_checks_by_paper(path_corpus, paper, only_found=only_found)
    if verbose:
        console.rule(f"Paper: {paper}", style="bold red")
        console.print(checks)
    if checks:
        return {k: sum(v.values()) for k, v in checks.items()}, checks
    return (None, None)


def dict_files_to_list(cols):
    return cols.apply(lambda d: list(d.keys()) if d is not np.nan else np.nan)


if __name__ == "__main__":
    path_corpus = Path("case-studies/arxiv-corpus/mine50-andor")
    downloaded_repos = get_downloaded_repos(path_corpus)

    for paper in downloaded_repos:
        console.rule(f"Paper: {paper}", style="bold red")
        console.print(tally_checks_by_paper(path_corpus, paper, only_found=False))
        console.print()
