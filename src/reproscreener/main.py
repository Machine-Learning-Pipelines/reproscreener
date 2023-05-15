from pathlib import Path
import logging

import typer
from rich import print as rprint

from reproscreener import read_tex, repo_eval
from reproscreener.utils import log
from reproscreener.download_arxiv import download_extract_source

app = typer.Typer()


# Mapping from command-line strings to logging levels
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


@app.command()
def main(
    arxiv: str = typer.Option(None, help="arXiv paper URL to download and evaluate"),
    repo: str = typer.Option(None, help="Git repo to evaluate"),
    local_arxiv: str = typer.Option(
        None,
        help="Local directory containing the arXiv source (.tex files to the paper)",
    ),
    local_repo: str = typer.Option(None, help="Local directory containing the repo"),
    log_level: str = typer.Option("info", help="Logging level"),
):
    # Set the logging level based on the command-line option
    log.setLevel(LOG_LEVELS[log_level])
    path_download = Path("case-studies/individual")
    path_download.mkdir(parents=True, exist_ok=True)

    if arxiv:
        paper_id = arxiv.split("/")[-1]
        path_base = path_download / paper_id
        path_paper = download_extract_source(arxiv, path_base / "paper")
    elif local_arxiv:
        path_paper = Path(local_arxiv)
        paper_id = path_paper.name
    else:
        path_paper = None

    if path_paper is not None:
        df_vars = read_tex.get_found_vars_tex(path_paper)
        paper_table = read_tex.init_repro_eval(df_vars)
        rprint(paper_table)

    if repo:
        repo_name = repo.split("/")[-1].split(".git")[0]
        cloned_path = repo_eval.clone_repo(
            repo, (path_base / "repo") if path_base else (path_download / "repos")
        )

    elif local_repo:
        cloned_path = Path(local_repo)
    else:
        cloned_path = None

    if cloned_path is not None:
        repo_df = repo_eval.evaluate_repo(cloned_path)
        repo_eval.display_dataframe(repo_df, title="Repository evaluation")

    if not (arxiv or local_arxiv or repo or local_repo):
        raise ValueError(
            "Must specify either an arXiv paper, a local paper, a repo, or a local repo."
        )


if __name__ == "__main__":
    app()
