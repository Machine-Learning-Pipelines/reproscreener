import datapane as dp
import pandas as pd
from pathlib import Path
from typing import List, Set


def create_html_report(
    paper_id: str,
    title: str,
    found_vars: Set[str],
    found_links: List[str],
    path: Path,
    df_tex: pd.DataFrame,
    df_repo: pd.DataFrame,
):
    """
    Create an HTML report using Datapane and save it to the provided path.

    Args:
        paper_id (str): ID of the paper.
        title (str): Title of the paper.
        found_vars (Set[str]): Set of found variables.
        found_links (List[str]): List of found URLs.
        path (Path): The path to save the HTML report.
        df_tex (pd.DataFrame): DataFrame containing the TeX evaluation results.
        df_repo (pd.DataFrame): DataFrame containing the repo evaluation results.
    """
    df_tex, df_repo = test_read_save_report_data(path.parent, df_tex, df_repo)

    # Create rich text outputs similar to CLI
    paper_id_text = dp.Text(f"**Paper ID:** {paper_id}")
    title_text = dp.Text(f"**Title:** {title}")
    found_vars_text = dp.Text(f"**Found Variables:**\n\n" + "\n".join([f"- {var}" for var in found_vars]))
    found_links_text = dp.Text(f"**Found Links:**\n\n" + "\n".join([f"- {link}" for link in found_links]))

    tex_intro_block = dp.Blocks(paper_id_text, title_text, found_vars_text, found_links_text)

    # Create data tables
    tex_table = dp.Table(df_tex)
    repo_table = dp.Table(df_repo)

    # Add the rich text and tables to the report
    report = dp.Blocks(
        dp.Page(title="TeX Evaluation Results", blocks=["## TeX Evaluation Results", tex_intro_block, tex_table]),
        dp.Page(title="Repo Evaluation Results", blocks=["## Repo Evaluation Results", repo_table]),
    )

    dp.save_report(report, path=path)


def test_read_save_report_data(path: Path, df_tex: pd.DataFrame, df_repo: pd.DataFrame):
    if path / "tex_eval.csv" and df_tex is None:
        df_tex = pd.read_csv(path / "tex_eval.csv")
    else:
        df_tex.to_csv(path / "tex_eval.csv")

    if path / "repo_eval.csv" and df_repo is None:
        df_repo = pd.read_csv(path / "repo_eval.csv")
    else:
        df_repo.to_csv(path / "repo_eval.csv")

    return df_tex, df_repo


if __name__ == "__main__":
    create_html_report(Path("case-studies/individual/2106.07704/report.html"), None, None)
