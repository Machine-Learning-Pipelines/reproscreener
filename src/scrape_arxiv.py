import tarfile
from pathlib import Path
from time import sleep
from rich.progress import track
from rich.console import Console
from rich import inspect
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    MofNCompleteColumn,
)

from multiprocessing import Process

import arxivscraper
import pandas as pd
import requests
from bs4 import BeautifulSoup
from grobid_client.grobid_client import GrobidClient


def filter_category(df_full, cat1, cat2):
    # ? Could add n catagories as input
    df_filtered = df_full[
        df_full["categories"].str.contains(cat1)
        & df_full["categories"].str.contains(cat2)
    ]
    return df_filtered.reset_index()


def init_paths(basedir, folder_name):
    path_corpus = basedir + folder_name
    Path(path_corpus).mkdir(parents=True, exist_ok=True)
    Path(path_corpus + "pdf/").mkdir(parents=True, exist_ok=True)
    Path(path_corpus + "html/").mkdir(parents=True, exist_ok=True)
    Path(path_corpus + "parsed_xml/").mkdir(parents=True, exist_ok=True)
    Path(path_corpus + "source/").mkdir(parents=True, exist_ok=True)
    return path_corpus


def init_scrape_arxiv(
    path_corpus,
    max_articles,
    to_query=True,
    date_from="2022-10-24",
    date_until="2022-10-25",
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
        df_filt = filter_category(df_full, "cs.lg", "stat.ml")

        df_full[
            df_full["categories"].str.contains("cs.lg")
            & df_full["categories"].str.contains("stat.ml")
        ]
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


def download_pdf(row, path_corpus, progress, task_download_pdf):
    progress.update(task_download_pdf, advance=1, name=str(row[1]["id"]))
    response = requests.get(row[1]["url_pdf"])
    path_pdf = path_corpus + "pdf/" + str(row[1]["id"]) + ".pdf"
    with open(path_pdf, "wb") as f:
        f.write(response.content)


def download_html(row, path_corpus, progress, task_download_html):
    progress.update(task_download_html, advance=1, name=str(row[1]["id"]))
    response = requests.get(row[1]["url_html"])
    soup = BeautifulSoup(response.content, "html.parser")
    filename = path_corpus + "html/" + str(row[1]["id"]) + ".html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(soup))


def download_extract_source(row, path_corpus, progress, task_download_source):
    progress.update(task_download_source, advance=1, name=str(row[1]["id"]))
    response = requests.get(row[1]["url_source"], stream=True)
    with tarfile.open(fileobj=response.raw, mode="r|gz") as tar:
        tar.extractall(path_corpus + "source/" + str(row[1]["id"]) + "/")


def scrape_arxiv(dff, path_corpus, grobid_parse=False):
    progress = Progress(
        TextColumn("{task.description}"),
        TextColumn("{task.fields[name]}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    )

    with progress:
        task_download_pdf = progress.add_task(
            "[red]Downloading PDFs...", name="article_id", total=max_articles
        )
        task_download_html = progress.add_task(
            "[magenta]Downloading HTML pages...", name="article_id", total=max_articles
        )
        task_download_source = progress.add_task(
            "[green]Downloading and extracting source...",
            name="article_id",
            total=max_articles,
        )
        if grobid_parse:
            task_grobid = progress.add_task(
                "[cyan]Parsing PDFs with GROBID...", total=max_articles
            )

        while not progress.finished:
            for row in dff[:max_articles].iterrows():
                download_pdf(row, path_corpus, progress, task_download_pdf)
                download_html(row, path_corpus, progress, task_download_html)
                download_extract_source(
                    row, path_corpus, progress, task_download_source
                )

                article_link = row[1]["url_html"]
                progress.console.print(
                    "Completed article:",
                    row[1]["id"],
                    style="link " + str(article_link),
                )

                sleep(1)

                if grobid_parse:
                    client = GrobidClient(
                        config_path=path_grobid_python + "config.json"
                    )
                    client.process(
                        "processFulltextDocument",
                        path_corpus + "pdf/",
                        output=path_corpus + "parsed_xml/",
                        n=20,
                    )
                    progress.update(task_grobid, advance=1)


if __name__ == "__main__":
    max_articles = 5
    folder_name = "mine5/"

    base_dir = "./case-studies/arxiv-corpus/"
    path_grobid_python = "../grobid_client_python/"

    path_corpus = init_paths(base_dir, folder_name)
    query_df = init_scrape_arxiv(path_corpus, max_articles, to_query=False)
    scrape_arxiv(query_df, path_corpus, grobid_parse=False)
