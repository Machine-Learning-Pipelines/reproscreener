from pathlib import Path
import logging

import typer
from rich import print as rprint
from rich.progress import Progress

from reproscreener import read_tex, repo_eval
from reproscreener.utils import console, log
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
    arxiv: str = typer.Option(..., help="Arxiv URL to download and evaluate"),
    repo: str = typer.Option(..., help="Git repo to evaluate"),
    log_level: str = typer.Option("info", help="Logging level"),
):
    # Set the logging level based on the command-line option
    log.setLevel(LOG_LEVELS[log_level])
    path_download = Path("case-studies/individual")
    path_download.mkdir(parents=True, exist_ok=True)

    progress = Progress()
    progress.start()

    path_paper = download_extract_source(arxiv, path_download)
    progress.stop()

    paper_id = arxiv.split("/")[-1]
    repo_eval.download_repo(repo, path_paper, paper_id)

    df = read_tex.get_found_vars_tex(path_paper)
    paper_table = read_tex.init_repro_eval(path_paper, df)
    rprint(paper_table)

    repo_df = repo_eval.evaluate_repo(path_paper)
    repo_eval.display_dataframe(repo_df, title="Repository evaluation")


if __name__ == "__main__":
    app()
