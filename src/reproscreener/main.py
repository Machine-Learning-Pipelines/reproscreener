import argparse
import logging
from pathlib import Path

from analysis.paper_analyzer import (
    main as paper_analyzer_main,
    analyze_abstracts_directory,
)
# from .repo_analyzer import main as repo_analyzer_main
# from .manual_evaluations.manual_eval import main as manual_eval_main


def main():
    parser = argparse.ArgumentParser(
        description="Reproscreener CLI"
    )
    parser.add_argument(
        "--gold-abstracts-dir",
        type=Path,
        default="../gold_standard/abstracts",
        help="Path to directory containing gold standard abstract .txt files",
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default="reports/tables/abstract_regex_gs.csv",
        help="Output CSV path for gold abstract evaluation (defaults to ./reports/tables/abstract_regex_gs.csv)",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.gold_abstracts_dir is not None:
        df = analyze_abstracts_directory(args.gold_abstracts_dir)
        out_csv = args.out_csv or Path("./gold_abstracts_eval.csv")
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_csv, index=False)
        print(f"Wrote gold abstract evaluation to {out_csv}")
        return

    # repo_analyzer_main()
    # manual_eval_main()
    return


if __name__ == "__main__":
    main()
