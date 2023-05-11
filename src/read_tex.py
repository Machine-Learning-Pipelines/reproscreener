import re
import pandas as pd
from pathlib import Path
import shutil
from flashtext import KeywordProcessor
from urlextract import URLExtract
import urllib.parse
import keywords
import evaluate_guidance as eg
from r_logger import log
from rich.progress import track


def combine_tex_in_folder(folder_path: Path, replace=False):
    combined_path = folder_path / "combined.tex"
    if replace or not combined_path.exists():
        with open(combined_path, "wb") as outfile:
            for tex_file in folder_path.glob("*.tex"):
                with open(tex_file, "rb") as infile:
                    shutil.copyfileobj(infile, outfile)
        log.debug("Combining tex files...")
    return str(combined_path)


def find_vars_tex(combined_path):
    keyword_dict = keywords.generate_gunderson_dict()
    keyword_processor = KeywordProcessor(case_sensitive=True)
    keyword_processor.add_keywords_from_dict(keyword_dict)
    with open(combined_path, "r", errors="replace") as f:
        data = f.readlines()
        all_found = []
        for line in track(data, description="Processing lines..."):
            all_found.append(keyword_processor.extract_keywords(line, span_info=True))
    non_empty_found = [x for x in all_found if x != []]
    found_vars = set()
    for i in non_empty_found:
        for j in i:
            found_vars.add(j[0])
    return found_vars


def extract_urls_and_emails(data):
    urls = []
    emails = []
    extractor = URLExtract()
    for line in data.split("\n"):
        urls += extractor.find_urls(line)
        emails += re.findall(r"\S+@\S+", line)
    return urls, emails


def find_data_repository_links_from_list(url_list):
    found_list = []
    for url in url_list:
        parsed_url = urllib.parse.urlparse(url)
        if (
            "github" in parsed_url.netloc
            or "gitlab" in parsed_url.netloc
            or "zenodo" in parsed_url.netloc
        ):
            found_list.append(url)
            log.debug(f"Found {parsed_url.netloc} link: {url}")
    return found_list


def get_found_links_tex(path_corpus: Path, df) -> pd.DataFrame:
    log.debug("Finding links in files...")
    df["found_links"] = df["id"].apply(
        lambda x: find_data_repository_links_from_list(
            extract_urls_and_emails(
                (path_corpus / "source" / x / "combined.tex").read_text()
            )[0]
        )
    )
    df["link_count"] = df["found_links"].apply(len)
    return df


def get_found_vars_tex(path_corpus: Path, df) -> pd.DataFrame:
    log.debug("Finding variables in files...")
    df["found_vars"] = df["id"].apply(
        lambda x: find_vars_tex(path_corpus / "source" / x / "combined.tex")
    )
    df["title"] = df["id"]
    return df[["id", "title", "found_vars"]]


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)

    log.debug("__main__")

    comb = combine_tex_in_folder(
        Path("./case-studies/arxiv-corpus/mine50-csLG/source/2009.01947/"),
        replace=True,
    )
    log.debug("Combined tex files.")

    print(extract_urls_and_emails("This is a line with an email: abc@example.com"))

    print(
        find_data_repository_links_from_list(
            ["https://github.com/data", "http://example.com"]
        )
    )

    df = pd.DataFrame({"id": ["2009.01947"]})
    log.debug("Finding links in tex files.")
    print(get_found_links_tex(Path("./case-studies/arxiv-corpus/mine50-csLG/"), df))

    log.debug("Finding variables in tex files.")
    print(get_found_vars_tex(Path("./case-studies/arxiv-corpus/mine50-csLG/"), df))
