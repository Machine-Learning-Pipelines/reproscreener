import pandas as pd
from pathlib import Path
import numpy as np

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from reproscreener.utils import console


def gdrive_authenticate():
    # TODO: Find a better way to specify the credentials file
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive


def gdrive_download_manual_eval(drive, manual_path):
    file_list = drive.ListFile({"q": "'root' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        if file1["title"] == "repro-screener":
            file_list2 = drive.ListFile({"q": "'%s' in parents and trashed=false" % file1["id"]}).GetList()
            for file2 in file_list2:
                if file2["id"] == "12FpKYUWtM8zLREZkdZGYR0eRWxcsbJhHwMbS_yuE46s":
                    file3 = drive.CreateFile({"id": file2["id"]})
                    file3.GetContentFile(
                        filename=manual_path,
                        mimetype="text/csv",
                    )
                    console.print("Downloaded file: %s" % file2["title"])
                    return manual_path


def gdrive_get_manual_eval(overwrite=False, manual_path="case-studies/arxiv-corpus/manual_eval.csv"):
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
        console.print("Manual eval file already exists, use the overwrite flag to download")

    if (not path_exists) or (path_exists and overwrite):
        drive = gdrive_authenticate()
        manual_path = gdrive_download_manual_eval(drive, manual_path)

    manual_eval = pd.read_csv(manual_path)
    manual_eval.replace("nan", np.nan)
    manual_eval = manual_eval.drop(index=[0, 51])
    manual_eval = manual_eval.astype(dtypes_manual)
    return manual_eval


if __name__ == "__main__":
    manual_path = Path("case-studies/arxiv-corpus/manual_eval.csv")
    manual = gdrive_get_manual_eval(overwrite=False, manual_path=manual_path)
    console.print(manual)
