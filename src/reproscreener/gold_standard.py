from reproscreener.gdrive_downloader import gdrive_get_manual_eval
from pathlib import Path
from typing import List


def get_gold_standard_ids_from_manual(manual_path: Path) -> List[str]:
    manual_df = gdrive_get_manual_eval(overwrite=False, manual_path=manual_path)
    return manual_df["paper"].tolist()


if __name__ == "__main__":
    manual_path = Path("case-studies/arxiv-corpus/manual_eval.csv")
    gold_standard_ids = get_gold_standard_ids_from_manual(manual_path=manual_path)
