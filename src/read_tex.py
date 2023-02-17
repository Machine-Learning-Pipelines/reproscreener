import glob
import os
from pathlib import Path
import keywords
import shutil
import evaluate_guidance as eg
from flashtext import KeywordProcessor
from urlextract import URLExtract
import urllib.parse

# from console import console
from r_logger import log


def combine_tex_in_folder(folder_path, replace=False):
    """_summary_
    Combine all tex files in folder into one for searching
    """
    combined_path = folder_path + "combined.tex"
    if replace == True:
        Path.unlink(Path(combined_path))
    if replace == True or Path.is_file(Path(combined_path)) == False:
        tex_list = glob.glob(folder_path + "*.tex", recursive=True)
        with open(combined_path, "wb") as outfile:
            for tex in tex_list:
                with open(tex, "rb") as infile:
                    shutil.copyfileobj(infile, outfile)
        log.debug("Combining tex files...")
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


def find_data_repository_links_tex(url_list):
    found_list = []
    for url in url_list:
        parsed_url = urllib.parse.urlparse(url)
        # print(parsed_url)
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
        lambda x: find_data_repository_links_tex(
            extract_urls_tex(combine_tex_in_folder(path_corpus + "source/" + x + "/"))
        )
    )
    df["link_count"] = df["found_links"].apply(lambda x: len(x))
    return df


def get_found_vars_tex(path_corpus, df):
    log.debug("Finding variables in files...")
    df["found_vars"] = df["id"].apply(
        lambda x: find_vars_tex(
            combine_tex_in_folder(path_corpus + "source/" + x + "/")
        )
    )
    df["title"] = df["id"]
    return df[["id", "title", "found_vars"]]


if __name__ == "__main__":

    # comb = combine_tex_in_folder(
    #     "./case-studies/arxiv-corpus/mine50-csLG/source/1909.00931/", replace=True
    # )
    # comb2 = combine_tex_in_folder(
    #     "./case-studies/arxiv-corpus/mine50-csLG/source/2105.15197/",
    #     replace=True,
    # )

    # console.rule()
    log.debug(f"Searching: 1909.00931/")
    find_data_repository_links_tex(extract_urls_tex(comb))
    extract_emails_tex(comb)
    # console.rule()

    log.debug(f"Searching: 2009.01947/")
    find_data_repository_links_tex(extract_urls_tex(comb2))
    extract_emails_tex(comb2)
    # console.rule()
