import pandas as pd
from pathlib import Path
from git import Repo

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def gdrive_authenticate():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive


def download_manual_eval(auth):
    file_list = drive.ListFile({"q": "'root' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        #   print('title: %s, id: %s' % (file1['title'], file1['id']))
        if file1["title"] == "repro-screener":
            file_list2 = drive.ListFile(
                {"q": "'%s' in parents and trashed=false" % file1["id"]}
            ).GetList()
            for file2 in file_list2:
                print("title: %s, id: %s" % (file2["title"], file2["id"]))
                if file2["id"] == "12FpKYUWtM8zLREZkdZGYR0eRWxcsbJhHwMbS_yuE46s":
                    file3 = drive.CreateFile({"id": file2["id"]})
                    file3.GetContentFile(
                        filename="manual_eval.csv", mimetype="text/csv"
                    )
                    print("Downloaded file: %s" % file2["title"])

def 

if __name__ == "__main__":
    # drive = gdrive_authenticate()
    # download_manual_eval(drive)
