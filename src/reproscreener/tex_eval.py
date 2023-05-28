import glob
import urllib.parse
from pathlib import Path
from typing import List, Set

from multiprocessing import Manager
from concurrent.futures import ProcessPoolExecutor
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TimeElapsedColumn
from flashtext import KeywordProcessor
from rich import box
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from urlextract import URLExtract
import pandas as pd

from reproscreener import keywords
from reproscreener.utils import console, log


def combine_tex_in_folder(folder_path: Path) -> Path:
    """
    Combine all .tex files in a given directory into a single file.

    Args:
        folder_path (Path): Path to the directory containing .tex files.

    Returns:
        Path: Path to the combined .tex file.
    """
    # Create a combined file of all .tex files in folder_path directory
    combined_path = folder_path / "combined.tex"
    with open(combined_path, "w", encoding="utf-8") as outfile:
        for name in glob.glob(f"{folder_path}/*.tex"):
            with open(name, encoding="utf-8") as infile:
                outfile.write(infile.read())
    return combined_path


def find_tex_variables(combined_path: Path) -> Set[str]:
    """
    Find variables in the combined tex file.
    Uses the `KeywordProcessor` from `flashtext` package to extract variables.

    Args:
        combined_path (Path): Path to the combined .tex file.

    Returns:
        Set[str]: Set of found variables.
    """
    keyword_dict = keywords.generate_gunderson_dict()
    keyword_processor = KeywordProcessor(case_sensitive=True)
    keyword_processor.add_keywords_from_dict(keyword_dict)
    with open(combined_path, "r", errors="replace", encoding="utf-8") as f:
        data = f.readlines()
        all_found = [keyword_processor.extract_keywords(line, span_info=True) for line in data]
        non_empty_found = [x for x in all_found if x != []]
        # Using set comprehension to avoid duplicates
        found_vars = {j[0] for i in non_empty_found for j in i}
    return found_vars


def extract_tex_urls(combined_path: Path) -> Set[str]:
    """
    Extract URLs from the combined tex file.

    Args:
        combined_path (Path): Path to the combined .tex file.

    Returns:
        Set[str]: Set of found URLs.
    """
    with open(combined_path, "r", errors="replace", encoding="utf-8") as f:
        data = f.read()
    extractor = URLExtract()
    urls = extractor.find_urls(data)
    log.debug("All urls:\n %s \n", urls)
    return set(urls)


def find_data_repository_links(
    url_list: Set[str], allowed_domains: List[str] = ["github", "gitlab", "zenodo"]
) -> List[str]:
    """
    Find URLs belonging to allowed domains (default - github, gitlab, zenodo).

    Args:
        url_list (Set[str]): Set of URLs to process.
        allowed_domains (List[str], optional): List of allowed domain names. Defaults to ["github", "gitlab", "zenodo"].

    Returns:
        List[str]: List of found URLs belonging to allowed domains.
    """
    found_list = [
        url for url in url_list if any(domain in urllib.parse.urlparse(url).netloc for domain in allowed_domains)
    ]
    for url in found_list:
        log.debug(f"Found {urllib.parse.urlparse(url).netloc} link: {url}")
    return found_list


def evaluate_paper(tex_folder_path: Path, paper_id: str) -> pd.DataFrame:
    """
    Evaluate a paper by extracting variables and URLs from its tex files.

    Args:
        tex_folder_path (Path): Path to the directory containing the paper's .tex files.
        paper_id (str): ID of the paper.

    Returns:
        pd.DataFrame: A DataFrame with the evaluation results.
    """
    combined_path = combine_tex_in_folder(tex_folder_path)
    found_vars = find_tex_variables(combined_path)
    found_urls = extract_tex_urls(combined_path)
    found_links = find_data_repository_links(found_urls)

    _, evaluation_results = paper_evaluation_results(paper_id, found_vars, found_links)

    return evaluation_results


def long_running_fn(args):
    progress, task_id, paper_path, paper_id = args
    result = evaluate_paper(paper_path, paper_id)
    progress[task_id] = {"progress": 1, "total": 1}
    return paper_id, result


def evaluate_papers(path_corpus: Path, evaluation_dict: dict) -> dict:
    """
    Evaluate a list of papers by extracting variables and URLs from their tex files.

    Args:
        path_corpus (Path): Path to the directory containing all papers.
        evaluation_dict (dict): Dictionary to store the evaluation results.

    Returns:
        dict: Dictionary with the evaluation results.
    """
    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        refresh_per_second=1,
    ) as progress:
        futures = []
        with Manager() as manager:
            _progress = manager.dict()
            overall_progress_task = progress.add_task("[green]Tex evaluation on all papers:")
            with ProcessPoolExecutor() as executor:
                for subdir in path_corpus.glob("*"):
                    if subdir.is_dir():
                        paper_path = subdir
                        paper_id = subdir.name
                        task_id = progress.add_task(f"task {paper_id}", visible=False)
                        futures.append(executor.submit(long_running_fn, (_progress, task_id, paper_path, paper_id)))

                while (n_finished := sum([future.done() for future in futures])) < len(futures):
                    progress.update(overall_progress_task, completed=n_finished, total=len(futures))
                    for task_id, update_data in _progress.items():
                        latest = update_data["progress"]
                        total = update_data["total"]
                        progress.update(task_id, completed=latest, total=total, visible=latest < total)

                for future in futures:
                    paper_id, result = future.result()
                    evaluation_dict[paper_id] = result

    return evaluation_dict


def get_all_tex_eval_dict(path_corpus: Path) -> dict:
    """Evaluates all papers in the given corpus and returns a dictionary of evaluation data.

    Args:
        path_corpus: A Path object representing the path to the corpus of papers to evaluate.

    Returns:
        A dictionary where the keys are paper IDs and the values are DataFrames containing the tex_eval results.
    """
    evaluation_dict = {}

    evaluation_dict = evaluate_papers(path_corpus, evaluation_dict)

    return evaluation_dict


def paper_evaluation_results(
    paper_id: str,
    found_vars: Set[str],
    found_links: List[str],
    title: str = "No title found",
) -> (Panel, pd.DataFrame):
    """
    Create a rich Panel with the results of the paper evaluation.

    Args
        paper_id (str): ID of the paper.
        title (str): Title of the paper.
        found_vars (Set[str]): Set of found variables.
        found_links (List[str]): List of found URLs.
    """
    if not isinstance(paper_id, str):
        raise TypeError(f"Expected paper_id to be str, got {type(paper_id).__name__}.")
    if not isinstance(title, str):
        raise TypeError(f"Expected title to be str, got {type(title).__name__}.")
    if not isinstance(found_vars, set):
        raise TypeError(f"Expected found_vars to be set, got {type(found_vars).__name__}.")
    if not isinstance(found_links, list):
        raise TypeError(f"Expected found_links to be list, got {type(found_links).__name__}.")

    result_text = Text.assemble(
        ("\nPaper ID: ", "bold cyan"),
        (paper_id, "bold yellow"),
        ("\n\nTitle: ", "bold cyan"),
        (title, "bold yellow"),
        ("\n\nFound Variables:\n", "bold cyan"),
        *[(f"- {var}\n", "green") for var in found_vars],
        ("\nFound Links:\n", "bold cyan"),
    )
    for link in found_links:
        result_text.append(f"- ", style="bold cyan")
        result_text.append(link, style=Style(link=True, underline=True, color="blue"))
        result_text.append("\n")  # Add newline after each link

    result_panel = Panel(
        result_text,
        title=Text.assemble((f"Paper Evaluation: {paper_id}", "bold magenta")),
        box=box.ROUNDED,
        expand=False,
    )

    result_dataframe = pd.DataFrame(
        {
            "Paper ID": [paper_id],
            "Found Variables": [", ".join(found_vars)],
            "Found Links": [", ".join(found_links)],
        }
    )

    return result_panel, result_dataframe
