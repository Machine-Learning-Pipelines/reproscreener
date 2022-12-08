import glob
import os
from pathlib import Path
import keywords
import shutil
import evaluate_guidance as eg
from flashtext import KeywordProcessor


def combine_tex_in_folder(folder_path):
    """_summary_
    Combine all tex files in folder into one for searching
    """
    combined_path = folder_path + "combined.tex"
    if Path.is_file(Path(combined_path)):
        Path.unlink(Path(combined_path))

    tex_list = glob.glob(folder_path + "*.tex", recursive=True)
    with open(combined_path, "wb") as outfile:
        for tex in tex_list:
            with open(tex, "rb") as infile:
                # print("combining:", tex)
                shutil.copyfileobj(infile, outfile)
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
    with open(combined_path, "r") as f:
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


def get_found_vars_tex(path_corpus, df):
    print("Finding variables in files...")
    df["found_vars"] = df["id"].apply(
        lambda x: find_vars_tex(
            combine_tex_in_folder(path_corpus + "source/" + x + "/")
        )
    )
    df["title"] = df["id"]
    return df[["id", "title", "found_vars"]]


# comb = combine_tex_in_folder('./case-studies/arxiv-corpus/mine50/source/2010.04261/')
# find_vars_tex(comb)
# print()
