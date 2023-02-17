import tarfile
from pathlib import Path
from time import sleep
from rich.progress import track
from rich.console import Console
from rich import inspect
from rich.progress import (
    Progress,
    TaskID,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    MofNCompleteColumn,
)

from loguru import logger
from concurrent.futures import ThreadPoolExecutor
import signal
from threading import Event
from time import perf_counter

import arxivscraper
import pandas as pd
import requests
from bs4 import BeautifulSoup
from grobid_client.grobid_client import GrobidClient

done_event = Event()


def handle_sigint(signum, frame):
    done_event.set()


signal.signal(signal.SIGINT, handle_sigint)


def filter_category(df_full, cat1, cat2, cond="cond1"):
    """Filter condition for arxiv categories

    Args:
        df_full (_type_): _description_
        cat1 (_type_): _description_
        cat2 (_type_): _description_
        cond (str, optional): "cond1" is cs.lg & stat.ml
                            "cond2" is (cs.lg & stat.ml | cs.lg)
                            Defaults to "cond1".

    Returns:
        _type_: _description_
    """
    if cond == "cond1":
        df_filtered = df_full[
            df_full["categories"].str.contains(cat1)
            & df_full["categories"].str.contains(cat2)
        ]
    elif cond == "cond2":
        df_filtered = df_full[
            (
                df_full["categories"].str.contains("cs.lg")
                & df_full["categories"].str.contains("stat.ml")
            )
            | df_full["categories"].str.contains("cs.lg")
        ]
    return df_filtered.reset_index()


def init_paths(basedir, folder_name):
    path_corpus = basedir + folder_name
    Path(path_corpus).mkdir(parents=True, exist_ok=True)
    Path("logs/").mkdir(parents=True, exist_ok=True)
    Path(path_corpus + "pdf/").mkdir(parents=True, exist_ok=True)
    Path(path_corpus + "html/").mkdir(parents=True, exist_ok=True)
    Path(path_corpus + "parsed_xml/").mkdir(parents=True, exist_ok=True)
    Path(path_corpus + "source/").mkdir(parents=True, exist_ok=True)
    Path(path_corpus + "output/").mkdir(parents=True, exist_ok=True)
    return path_corpus


def init_scrape_arxiv(
    path_corpus,
    max_articles,
    to_query=True,
    date_from="2022-10-24",
    date_until="2022-10-25",
    filter_cond="cond1",
):

    if to_query:
        scraper = arxivscraper.Scraper(
            category="cs",
            date_from=date_from,
            date_until=date_until,
            t=10,
            filters={"categories": ["cs.lg"]},
        )
        df_full = scraper.scrape()
        cols = (
            "id",
            "title",
            "categories",
            "abstract",
            "doi",
            "created",
            "updated",
            "authors",
        )
        df_full = pd.DataFrame(df_full, columns=cols)
        df_filt = filter_category(df_full, "cs.lg", "stat.ml", cond=filter_cond)

        df_filt[:max_articles].to_csv(
            path_corpus + "scrape_df.csv", index_label="index"
        )
        df_filt.to_csv(path_corpus + "scrape_df_full.csv", index_label="index")

    else:
        df_filt = pd.read_csv(path_corpus + "scrape_df.csv")

    df_filt["url_pdf"] = "https://arxiv.org/pdf/" + df_filt["id"].apply(str) + ".pdf"
    df_filt["url_html"] = "https://arxiv.org/abs/" + df_filt["id"].apply(str)
    df_filt["url_source"] = "https://arxiv.org/e-print/" + df_filt["id"].apply(str)
    return df_filt


def download_pdf(task_id: TaskID, row, path_corpus, progress) -> None:
    response = requests.get(row[1]["url_pdf"])
    path_pdf = path_corpus + "pdf/" + str(row[1]["id"]) + ".pdf"
    with open(path_pdf, "wb") as f:
        f.write(response.content)
        progress.update(task_id, advance=1)

        article_link = row[1]["url_html"]
        progress.console.print(
            "Downloaded PDF:",
            row[1]["id"],
            style="link " + str(article_link),
        )
        logger.info(f"Downloaded PDF: {str(row[1]['id'])} - {str(article_link)}")

        if done_event.is_set():
            return


def download_html(task_id: TaskID, row, path_corpus, progress) -> None:
    response = requests.get(row[1]["url_html"])
    soup = BeautifulSoup(response.content, "html.parser")
    filename = path_corpus + "html/" + str(row[1]["id"]) + ".html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(soup))
        progress.update(task_id, advance=1)

        article_link = row[1]["url_html"]
        progress.console.print(
            "Downloaded HTML:",
            row[1]["id"],
            style="link " + str(article_link),
        )
        logger.info(f"Downloaded HTML: {str(row[1]['id'])} - {str(article_link)}")

        if done_event.is_set():
            return


def download_extract_source(task_id: TaskID, row, path_corpus, progress) -> None:
    response = requests.get(row[1]["url_source"], stream=True)
    with tarfile.open(fileobj=response.raw, mode="r|gz") as tar:
        tar.extractall(path_corpus + "source/" + str(row[1]["id"]) + "/")
        progress.update(task_id, advance=1)

        article_link = row[1]["url_html"]
        progress.console.print(
            "Downloaded source:",
            row[1]["id"],
            style="link " + str(article_link),
        )
        logger.info(f"Downloaded source: {str(row[1]['id'])} - {str(article_link)}")

        if done_event.is_set():
            return


# def download_extract_source(row, path_corpus, progress, task_download_source):
#     progress.update(task_download_source, advance=1, name=str(row[1]["id"]))
#     response = requests.get(row[1]["url_source"], stream=True)
#     with tarfile.open(fileobj=response.raw, mode="r|gz") as tar:
#         tar.extractall(path_corpus + "source/" + str(row[1]["id"]) + "/")


def scrape_arxiv(dff, path_corpus, grobid_parse=False):
    progress = Progress(
        TextColumn("{task.description}"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    )

    with progress:
        task_download_pdf = progress.add_task(
            "[red]Downloading PDFs...", total=max_articles
        )
        task_download_html = progress.add_task(
            "[magenta]Downloading HTML pages...", total=max_articles
        )
        task_download_source = progress.add_task(
            "[green]Downloading and extracting source...",
            total=max_articles,
        )
        with ThreadPoolExecutor() as pool:

            # if grobid_parse:
            #     task_grobid = progress.add_task(
            #         "[cyan]Parsing PDFs with GROBID...",  name="article_id", total=max_articles, start=False
            #     )

            [
                pool.submit(download_pdf, task_download_pdf, row, path_corpus, progress)
                for row in dff[:max_articles].iterrows()
            ]

            [
                pool.submit(
                    download_html, task_download_html, row, path_corpus, progress
                )
                for row in dff[:max_articles].iterrows()
            ]

            [
                pool.submit(
                    download_extract_source,
                    task_download_source,
                    row,
                    path_corpus,
                    progress,
                )
                for row in dff[:max_articles].iterrows()
            ]

            # for row in dff[:max_articles].iterrows():
            #     pool.submit(download_pdf, task_download_pdf, row, path_corpus, progress)
            #     pool.submit(download_html, task_download_html, row, path_corpus, progress)
            #     pool.submit(download_extract_source, task_download_source, row, path_corpus, progress)

            # sleep(1)

            # if grobid_parse:
            #     client = GrobidClient(
            #         config_path=path_grobid_python + "config.json"
            #     )
            #     client.process(
            #         "processFulltextDocument",
            #         path_corpus + "pdf/",
            #         output=path_corpus + "parsed_xml/",
            #         n=20,
            #     )
            #     progress.update(task_grobid, advance=1)
    return True


if __name__ == "__main__":
    tic = perf_counter()
    # main_console = Console()

    max_articles = 98
    folder_name = "mine98-andor/"

    logger.add(f"logs/scrape{str(max_articles)}.log")

    base_dir = "./case-studies/arxiv-corpus/"
    path_grobid_python = "../grobid_client_python/"

    path_corpus = init_paths(base_dir, folder_name)
    query_df = init_scrape_arxiv(
        path_corpus, max_articles, to_query=True, filter_cond="cond2"
    )

    scrape_arxiv(query_df, path_corpus, grobid_parse=False)

    toc = perf_counter()
    # main_console.print(f"Run in {toc - tic:0.4f} seconds")
    logger.info(f"Run in {toc - tic:0.4f} seconds")
