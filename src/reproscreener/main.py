from pathlib import Path
import logging
import pandas as pd
from rich.text import Text
from rich.progress import Progress
import typer

import tex_eval, repo_eval
from utils import log, console, download_extract_source
from plots import tex_eval_heatmaps, repo_eval_heatmaps
from scrape_arxiv import scrape_arxiv, get_paper_ids, init_paths, extract_tar_files

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
        paper_title, path_paper = download_extract_source(arxiv, path_base / "paper")
    elif local_arxiv:
        path_paper = Path(local_arxiv)
        paper_id = path_paper.name
        console.rule("")
    else:
        path_paper = None

    if path_paper is not None:
        combined_tex = tex_eval.combine_tex_in_folder(path_paper)
        found_vars = tex_eval.find_tex_variables(combined_tex)
        urls = tex_eval.extract_tex_urls(combined_tex)
        found_links = tex_eval.find_data_repository_links(urls)
        _, df_paper_results = tex_eval.paper_evaluation_results(paper_id, found_vars, found_links, paper_title)
        console.print(df_paper_results)
        console.print("\n")

    if repo:
        if path_paper is None:
            path_base = path_download
        console.rule(
            Text.assemble(("Repository evaluation", "bold magenta")),
        )
        repo_name = repo.split("/")[-1].split(".git")[0]
        cloned_path = repo_eval.clone_repo(
            repo, (path_base / "repo" / repo_name) if path_base else (path_download / "repos")
        )

    elif local_repo:
        cloned_path = Path(local_repo)
    else:
        cloned_path = None

    if cloned_path is not None:
        df_repo_results = repo_eval.evaluate_repo(cloned_path)
        repo_results = repo_eval.repo_eval_table(df_repo_results)
        console.print(repo_results)

    if not (arxiv or local_arxiv or repo or local_repo):
        raise ValueError("Must specify either an arXiv paper, a local paper, a repo, or a local repo.")
    if not (arxiv or local_arxiv or repo or local_repo):
        raise ValueError("Must specify either an arXiv paper, a local paper, a repo, or a local repo.")


@app.command()
def download_gold_standard(
    base_dir: str = "./case-studies/arxiv-corpus/",
    folder_name: str = "gold_standard/",
    path_manual_eval: str = "case-studies/arxiv-corpus/manual_eval.csv",
):
    progress = Progress()
    path_corpus = init_paths(base_dir, folder_name)
    paper_ids = get_paper_ids(path_manual_eval)

    with progress:
        task_id = progress.add_task("[cyan]Downloading...", total=len(paper_ids))
        scrape_arxiv(paper_ids, path_corpus, progress, task_id)
        extract_tar_files(path_corpus, progress)

    console.log("[green]Gold standard papers have been downloaded and extracted.")


@app.command()
def download_repositories(
    path_manual_eval: Path = "case-studies/arxiv-corpus/manual_eval.csv",
    path_corpus: Path = "case-studies/arxiv-corpus/gold_standard/repo",  # Adjust path_corpus to include /repo
):
    df = pd.read_csv(path_manual_eval)
    df = df.iloc[1:-1]  # drop the first and last rows of df
    repo_urls = df["code_avail_url"].dropna().tolist()
    arxiv_ids = df["paper"].dropna().tolist()  # get arxiv ids
    path_corpus = Path(path_corpus)
    path_corpus.mkdir(parents=True, exist_ok=True)
    repo_eval.clone_repos(arxiv_ids, repo_urls, path_corpus)  # pass arxiv ids to clone_repos
    console.log("[green]Repositories have been cloned.")


@app.command()
def run_evaluation_modules(
    path_corpus: Path = "case-studies/arxiv-corpus/gold_standard/",
    path_manual_eval: Path = "case-studies/arxiv-corpus/manual_eval.csv",
):
    repo_eval_heatmaps.evaluate_and_save_plots(path_corpus, path_manual_eval)
    tex_eval_heatmaps.evaluate_and_save_plots(path_corpus, path_manual_eval)
    console.log("[green]Repo and tex evaluations have been run.")


if __name__ == "__main__":
    app()
