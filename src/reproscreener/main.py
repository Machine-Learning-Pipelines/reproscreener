import argparse
import logging
from pathlib import Path

# from .analysis.paper_analyzer import analyze_abstracts_directory
from .analysis.repo_analyzer import analyze_repositories_from_csv
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
        "--manual-eval-csv",
        type=Path,
        default="notebooks/explore/manual_eval.csv",
        help="Path to CSV file containing manual evaluation data with repository URLs",
    )
    parser.add_argument(
        "--repo-clone-dir",
        type=Path,
        default="temp_repo_clones",
        help="Directory to clone repositories to for analysis",
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default="reports/tables/abstract_regex_gs.csv",
        help="Output CSV path for gold abstract evaluation (defaults to ./reports/tables/abstract_regex_gs.csv)",
    )
    parser.add_argument(
        "--repo-out-csv",
        type=Path,
        default="reports/tables/repo_evaluation_gs.csv",
        help="Output CSV path for repository evaluation (defaults to ./reports/tables/repo_evaluation_gs.csv)",
    )
    parser.add_argument(
        "--analyze-repos",
        action="store_true",
        help="Analyze repositories from manual evaluation CSV",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.analyze_repos:
        print(f"Analyzing repositories from {args.manual_eval_csv}")
        df = analyze_repositories_from_csv(args.manual_eval_csv, args.repo_clone_dir)
        out_csv = args.repo_out_csv
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_csv, index=False)
        print(f"Wrote repository evaluation to {out_csv}")
        print(f"Analyzed {len(df)} repositories")
        return

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
