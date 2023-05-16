from pathlib import Path
import logging

import typer
from rich import print as rprint

from reproscreener import tex_eval, repo_eval
from reproscreener.utils import log, console
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
        console.rule(f"\nPaper evaluation: {paper_id}")
        path_base = path_download / paper_id
        path_paper = download_extract_source(arxiv, path_base / "paper")
    elif local_arxiv:
        path_paper = Path(local_arxiv)
        paper_id = path_paper.name
        console.rule(f"Paper evaluation: {paper_id}")
    else:
        path_paper = None

    if path_paper is not None:
        combined_tex = tex_eval.combine_tex_in_folder(path_paper)
        found_vars = tex_eval.find_tex_variables(combined_tex)
        urls = tex_eval.extract_tex_urls(combined_tex)
        found_links = tex_eval.find_data_repository_links(urls)
        paper_table = tex_eval.initialize_repo_evaluation_table(paper_id, "title", found_vars, found_links)
        console.print(paper_table, overflow="fold")
        console.print("\n")

    if repo:
        console.rule("Repository evaluation")
        repo_name = repo.split("/")[-1].split(".git")[0]
        cloned_path = repo_eval.clone_repo(
            repo, (path_base / "repo" / repo_name) if path_base else (path_download / "repos")
        )

    elif local_repo:
        cloned_path = Path(local_repo)
    else:
        cloned_path = None

    if cloned_path is not None:
        repo_df = repo_eval.evaluate_repo(cloned_path)
        repo_eval.display_dataframe(repo_df)

    if not (arxiv or local_arxiv or repo or local_repo):
        raise ValueError("Must specify either an arXiv paper, a local paper, a repo, or a local repo.")


if __name__ == "__main__":
    app()
