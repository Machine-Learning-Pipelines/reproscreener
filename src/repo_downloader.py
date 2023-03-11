import pandas as pd
from pathlib import Path
from git import Repo
import numpy as np

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from console import console
from read_tex import find_data_repository_links_from_list

from git import RemoteProgress


class GitProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=""):
        print(
            op_code,
            cur_count,
            max_count,
            cur_count / (max_count or 100.0),
            message or "NO MESSAGE",
        )


def gdrive_authenticate():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive


def gdrive_download_manual_eval(drive, manual_path):
    file_list = drive.ListFile({"q": "'root' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        if file1["title"] == "repro-screener":
            file_list2 = drive.ListFile(
                {"q": "'%s' in parents and trashed=false" % file1["id"]}
            ).GetList()
            for file2 in file_list2:
                if file2["id"] == "12FpKYUWtM8zLREZkdZGYR0eRWxcsbJhHwMbS_yuE46s":
                    file3 = drive.CreateFile({"id": file2["id"]})
                    file3.GetContentFile(
                        filename=manual_path,
                        mimetype="text/csv",
                    )
                    console.print("Downloaded file: %s" % file2["title"])
                    return manual_path


def gdrive_get_manual_eval(
    overwrite=False, manual_path="case-studies/arxiv-corpus/manual_eval.csv"
):
    dtypes_manual = {
        "paper": str,
        "notes": str,
        "empirical_dataset": str,
        "article_link_avail": float,
        "code_available_article_desc": str,
        "code_avail_url": str,
        "pwc_link_avail": float,
        "pwc_link_match": float,
        "pwc_link_desc": str,
        "result_replication_code_avail": float,
        "code_language": str,
        "package": float,
        "wrapper_script": str,
        "hardware_specifications": str,
        "software_dependencies": str,
        "will_it_reproduce": float,
    }
    path_exists = Path(manual_path).is_file()

    if path_exists and not overwrite:
        console.print(
            "Manual eval file already exists, use the overwrite flag to download"
        )

    if (not path_exists) or (path_exists and overwrite):
        drive = gdrive_authenticate()
        manual_path = gdrive_download_manual_eval(drive, manual_path)

    manual_eval = pd.read_csv(manual_path)
    manual_eval.replace("nan", np.nan)
    manual_eval = manual_eval.drop(index=[0, 51])
    manual_eval = manual_eval.astype(dtypes_manual)
    return manual_eval


def get_manual_eval_urls(manual_df):
    manual_df = manual_df[
        [
            "paper",
            "article_link_avail",
            "code_avail_url",
            "result_replication_code_avail",
        ]
    ].copy()
    # convert string with new line chars to list and then call find_data_repository_links_from_list
    manual_df["found_repo_url"] = manual_df.code_avail_url.apply(
        lambda x: find_data_repository_links_from_list([x])
    )
    return manual_df


def download_repos(path_corpus, manual_eval: pd.DataFrame, overwrite=False):
    for index, row in manual_eval.iterrows():
        path_paper = path_corpus / "repo" / row["paper"]
        path_exists = path_paper.is_dir()

        if path_exists and not overwrite:
            console.print(
                "Repo directory already exists: {path_paper}, use the overwrite flag to download"
            )

        if (not path_exists) or (path_exists and overwrite):
            Path(path_paper).mkdir(parents=True, exist_ok=True)

            try:
                with console.status("Cloning repo...", spinner="dots"):
                    Repo.clone_from(
                        row["found_repo_url"][0],
                        path_paper,
                    )
                    console.status(
                        "Successfully cloned repo: %s" % row["found_repo_url"]
                    )
                    console.print(
                        "Successfully cloned repo: %s" % row["found_repo_url"]
                    )
            except:
                console.print("Failed to clone repo: %s" % row["found_repo_url"])


if __name__ == "__main__":
    path_corpus = Path("case-studies/arxiv-corpus/mine50-andor")
    df_manual = gdrive_get_manual_eval(overwrite=False)
    df_manual = df_manual[df_manual["code_avail_url"] != "nan"]
    df_manual = get_manual_eval_urls(df_manual)

    download_repos(path_corpus, df_manual)
    console.print(df_manual[["paper", "found_repo_url"]])
