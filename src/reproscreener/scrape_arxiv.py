import signal
import tarfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePath
from threading import Event

import arxiv
import pandas as pd
from rich.progress import Progress

from utils import console

progress = Progress(console=console)
done_event = Event()


def handle_sigint(signum, frame):
    done_event.set()


signal.signal(signal.SIGINT, handle_sigint)


def init_paths(basedir, folder_name):
    path_corpus = Path(basedir) / folder_name
    (path_corpus / "pdfs").mkdir(parents=True, exist_ok=True)
    (path_corpus / "abstracts").mkdir(parents=True, exist_ok=True)
    (path_corpus / "source").mkdir(parents=True, exist_ok=True)
    (path_corpus / "output").mkdir(parents=True, exist_ok=True)
    (path_corpus / "repo").mkdir(parents=True, exist_ok=True)
    return path_corpus


def get_paper_ids(path_manual_eval):
    df = pd.read_csv(path_manual_eval)
    df = df.iloc[1:-1]  # drop the first and last rows of df (Title description and Total)
    return df["paper"].values


def scrape_arxiv(paper_ids, path_corpus, progress, task_id):
    with ThreadPoolExecutor() as pool:
        for paper_id in paper_ids:
            pool.submit(download_pdf_and_source, task_id, paper_id, path_corpus, progress)
    console.log("[green]All files have been downloaded.")


def extract_tar_files(path_corpus, progress):
    source_path = path_corpus / "source"
    files = list(source_path.glob("*.tar.gz"))

    task_id = progress.add_task("[cyan]Extracting...", total=len(files))
    for file in files:
        filename = PurePath(file.stem).stem
        with tarfile.open(file, "r:gz") as tar:
            tar.extractall(path=str(source_path / filename))
        file.unlink()
        progress.update(task_id, advance=1)


def download_pdf_and_source(task_id, paper_id, path_corpus, progress) -> None:
    paper = next(arxiv.Search(id_list=[paper_id]).results())
    paper.download_pdf(dirpath=str(path_corpus / "pdfs"), filename=f"{paper_id}.pdf")
    paper.download_source(dirpath=str(path_corpus / "source"), filename=f"{paper_id}.tar.gz")

    with open(path_corpus / "abstracts" / f"{paper_id}.txt", "w") as f:
        f.write(paper.summary)

    progress.update(task_id, advance=1)

    if done_event.is_set():
        return


if __name__ == "__main__":
    path_manual_eval = Path("case-studies/arxiv-corpus/manual_eval.csv")
    folder_name = "gold_standard_v2/"
    base_dir = "./case-studies/arxiv-corpus/"

    path_corpus = init_paths(base_dir, folder_name)
    paper_ids = get_paper_ids(path_manual_eval)

    with progress:
        task_id = progress.add_task("[cyan]Downloading...", total=len(paper_ids))
        scrape_arxiv(paper_ids, path_corpus, progress, task_id)
        extract_tar_files(path_corpus, progress)
        console.log("[green]All tar files have been extracted.")
