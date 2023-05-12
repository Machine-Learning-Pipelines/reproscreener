import glob
import os
import shutil
import urllib.parse
from pathlib import Path

from flashtext import KeywordProcessor
from urlextract import URLExtract

import evaluate_guidance as eg
import keywords

from r_logger import log
import pandas as pd
from rich.table import Table


def combine_tex_in_folder(folder_path):
    folder_path = Path(folder_path)
    combined_path = folder_path / "combined.tex"
    with open(combined_path, "w") as outfile:
        for name in glob.glob(f"{folder_path}/*.tex"):
            with open(name) as infile:
                outfile.write(infile.read())
    return combined_path


def find_vars_tex(combined_path):
    """Find all variables per (Gunderson) metrics by reading the source tex files

    Args:
        combined_path (str): Path to the combined tex file from combine_tex_in_folder()

    Returns:
        found_vars (set): Set of variables found in the article
    """
    keyword_dict = keywords.generate_gunderson_dict()
    keyword_processor = KeywordProcessor(case_sensitive=True)
    keyword_processor.add_keywords_from_dict(keyword_dict)
    with open(combined_path, "r", errors="replace") as f:
        data = f.readlines()
        all_found = []
        for line in data:
            all_found.append(keyword_processor.extract_keywords(line, span_info=True))
    non_empty_found = [x for x in all_found if x != []]
    found_vars = set()
    for i in non_empty_found:
        for j in i:
            found_vars.add(j[0])
    return found_vars


def extract_urls_tex(combined_path):
    with open(combined_path, "r", errors="replace") as f:
        data = f.read()

    extractor = URLExtract()
    urls = extractor.find_urls(data)
    log.debug(f"All urls:\n {urls} \n")
    return urls


def extract_emails_tex(combined_path):
    with open(combined_path, "r", errors="replace") as f:
        data = f.read()

    extractor = URLExtract(extract_email=True)
    emails = list(filter(lambda x: "@" in x, extractor.find_urls(data)))
    log.debug(f"Found emails: {emails}")
    return emails


def find_data_repository_links_from_list(url_list):
    found_list = []
    for url in url_list:
        parsed_url = urllib.parse.urlparse(url)
        # print(found_list)
        if "github" in parsed_url.netloc:
            found_list.append(url)
            log.debug(f"Found github link: {url}")
        if "gitlab" in parsed_url.netloc:
            found_list.append(url)
            log.debug(f"Found gitlab link: {url}")
        if "zenodo" in parsed_url.netloc:
            found_list.append(url)
            log.debug(f"Found zenodo link: {url}")
    return found_list


def get_found_links_tex(path_corpus, df):
    log.debug("Finding links in files...")
    df["found_links"] = df["id"].apply(
        lambda x: find_data_repository_links_from_list(
            extract_urls_tex(combine_tex_in_folder(path_corpus + "source/" + x + "/"))
        )
    )
    df["link_count"] = df["found_links"].apply(lambda x: len(x))
    return df


def get_found_vars_tex(path_corpus):
    combined_path = combine_tex_in_folder(path_corpus)
    found_vars = find_vars_tex(combined_path)

    df = pd.DataFrame([{"id": "1", "title": "title", "found_vars": found_vars}])

    return df


def init_repro_eval(path_corpus, df):
    table = Table(title="Paper Evaluation")

    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Found Variables", justify="right", style="green")

    for _, row in df.iterrows():
        table.add_row(row["id"], row["title"], ", ".join(row["found_vars"]))

    return table


if __name__ == "__main__":
    # comb = combine_tex_in_folder(
    #     "./case-studies/arxiv-corpus/mine50-csLG/source/1909.00931/", replace=True
    # )
    # comb2 = combine_tex_in_folder(
    #     "./case-studies/arxiv-corpus/mine50-csLG/source/2105.15197/",
    #     replace=True,
    # )
    log.debug("__main__")
    # console.rule()
    # log.debug(f"Searching: 1909.00931/")
    # find_data_repository_links_from_list(extract_urls_tex(comb))
    # extract_emails_tex(comb)
    # console.rule()

    # log.debug(f"Searching: 2009.01947/")
    # find_data_repository_links_from_list(extract_urls_tex(comb2))
    # extract_emails_tex(comb2)
    # console.rule()
