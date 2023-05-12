import argparse
import tarfile
from pathlib import Path

import requests
from rich import print as rprint
from rich.progress import Progress

from reproscreener import read_tex, repo_eval


def download_extract_source(arxiv_url, path_download) -> None:
    paper_id = arxiv_url.split("/")[-1]  # extract paper id from arxiv url
    path_paper = Path(path_download) / paper_id
    path_paper.mkdir(parents=True, exist_ok=True)

    response = requests.get(arxiv_url, stream=True)
    with tarfile.open(fileobj=response.raw, mode="r|gz") as tar:
        tar.extractall(path_paper)

        rprint("Downloaded source:", arxiv_url)
    return path_paper


def main(args):
    path_download = Path("case-studies/individual")
    path_download.mkdir(parents=True, exist_ok=True)

    # Initialize rich Progress
    progress = Progress()
    progress.start()
    # Download and extract the source
    path_paper = download_extract_source(args.arxiv, path_download)
    progress.stop()

    # Download the repo
    repo_url = args.repo
    paper_id = args.arxiv.split("/")[-1]  # Extract paper id from the arxiv URL
    repo_eval.download_repo(repo_url, path_paper, paper_id)

    # Perform evaluation
    df = read_tex.get_found_vars_tex(path_paper)
    paper_table = read_tex.init_repro_eval(path_paper, df)
    rprint(paper_table)

    # Perform repo evaluation
    repo_df, unique_matches_df = repo_eval.evaluate_repo(path_paper)
    repo_eval.display_dataframe(repo_df, title="Repo Evaluation - Matches")
    repo_eval.display_dataframe(
        unique_matches_df, title="Repo Evaluation - All unique matches"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ReproScreener")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--arxiv", metavar="URL", help="Arxiv URL to download and parse")
    group.add_argument("--source", metavar="PATH", help="Path to the source folder")
    parser.add_argument("--repo", metavar="URL", help="Git repo to evaluate")
    args = parser.parse_args()

    main(args)
