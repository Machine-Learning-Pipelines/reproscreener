import glob
import urllib.parse
from pathlib import Path

import pandas as pd
from flashtext import KeywordProcessor
from urlextract import URLExtract

from rich import print as rprint
from rich.table import Table

from reproscreener import keywords
from reproscreener.utils import log


class TexProcessor:
    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)
        self.combined_path = self.folder_path / "combined.tex"
        self.combine_tex_in_folder()

    def combine_tex_in_folder(self):
        with open(self.combined_path, "w", encoding="utf-8") as outfile:
            for name in glob.glob(f"{self.folder_path}/*.tex"):
                with open(name, encoding="utf-8") as infile:
                    outfile.write(infile.read())
        return self.combined_path

    def find_vars_tex(self):
        keyword_dict = keywords.generate_gunderson_dict()
        keyword_processor = KeywordProcessor(case_sensitive=True)
        keyword_processor.add_keywords_from_dict(keyword_dict)
        with open(self.combined_path, "r", errors="replace", encoding="utf-8") as f:
            data = f.readlines()
            all_found = [
                keyword_processor.extract_keywords(line, span_info=True)
                for line in data
            ]
            non_empty_found = [x for x in all_found if x != []]
            found_vars = {j[0] for i in non_empty_found for j in i}
        return found_vars

    def extract_urls_tex(self):
        with open(self.combined_path, "r", errors="replace", encoding="utf-8") as f:
            data = f.read()
        extractor = URLExtract()
        urls = extractor.find_urls(data)
        log.debug("All urls:\n %s \n", urls)
        return urls

    def extract_emails_tex(self):
        with open(self.combined_path, "r", errors="replace", encoding="utf-8") as f:
            data = f.read()
        extractor = URLExtract(extract_email=True)
        emails = list(filter(lambda x: "@" in x, extractor.find_urls(data)))
        log.debug("Found emails: %s", emails)
        return emails


class RepoFinder:
    @staticmethod
    def find_data_repository_links_from_list(url_list):
        found_list = []
        for url in url_list:
            parsed_url = urllib.parse.urlparse(url)
            if "github" in parsed_url.netloc:
                found_list.append(url)
                log.debug("Found github link: %s", url)
            elif "gitlab" in parsed_url.netloc:
                found_list.append(url)
                log.debug("Found gitlab link: %s", url)
            elif "zenodo" in parsed_url.netloc:
                found_list.append(url)
                log.debug("Found zenodo link: %s", url)
        return found_list


def count_links(links):
    return len(links)


def get_found_links_tex(path_corpus, df_table):
    log.debug("Finding links in files...")
    tex_processor = TexProcessor(path_corpus + "source/" + df_table["id"] + "/")
    df_table["found_links"] = RepoFinder.find_data_repository_links_from_list(
        tex_processor.extract_urls_tex()
    )

    df_table["link_count"] = df_table["found_links"].apply(count_links)
    return df_table


def get_found_vars_tex(path_corpus):
    tex_processor = TexProcessor(path_corpus)
    found_vars = tex_processor.find_vars_tex()
    df = pd.DataFrame([{"id": "1", "title": "title", "found_vars": found_vars}])
    return df


def init_repro_eval(df_table):
    table = Table(title="Paper Evaluation")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Found Variables", justify="right", style="green")

    for _, row in df_table.iterrows():
        table.add_row(row["id"], row["title"], ", ".join(row["found_vars"]))

    return table


def main():
    # Initialize classes
    tex_processor = TexProcessor(
        "./case-studies/arxiv-corpus/mine50-csLG/source/1909.00931/"
    )

    # Process TeX and find repository links
    found_vars = tex_processor.find_vars_tex()
    df_table = pd.DataFrame([{"id": "1", "title": "title", "found_vars": found_vars}])

    # Find repository links and count them
    found_links = RepoFinder.find_data_repository_links_from_list(
        tex_processor.extract_urls_tex()
    )
    df_table["found_links"] = None  # Create 'found_links' column
    df_table.at[0, "found_links"] = [found_links]  # Assign found_links as a list
    df_table["link_count"] = df_table["found_links"].apply(len)

    # Display evaluation table
    table = init_repro_eval(df_table)
    rprint(table)


if __name__ == "__main__":
    main()
