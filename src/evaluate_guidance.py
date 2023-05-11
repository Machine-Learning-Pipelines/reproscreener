from pathlib import Path

import pandas as pd
from rich.progress import track
from rich.table import Table
from rich.console import Console

import keywords

console = Console()


def init_repro_eval(path_corpus: Path):
    repro_eval = pd.read_csv(path_corpus / "scrape_df.csv", dtype=object)
    return repro_eval[["id"]]


def get_found_vars(path_corpus: Path, df: pd.DataFrame):
    console.log("Reading files...")
    df["soup"] = df["id"].apply(
        lambda x: keywords.read_tei(path_corpus / "parsed_xml" / f"{x}.tei.xml")
    )
    df["title"] = df["soup"].apply(lambda x: x.title.getText())
    console.log("Finding variables in files...")
    df["found_vars"] = df["soup"].apply(lambda x: keywords.find_vars(x))
    df["affiliation_calc"] = df["soup"].apply(lambda x: keywords.find_affiliation(x))
    return df[["id", "title", "found_vars", "affiliation_calc"]]


def calc_found_vars_array(found_vars, variables):
    vars_array = [0] * len(variables)
    for i, var in enumerate(variables):
        vars_array[i] = 1 if var in found_vars else 0
    return vars_array


def set_repro_eval_scores(df, variables, skip_affiliation=False):
    df["found_vars_array"] = df["found_vars"].apply(
        lambda x: calc_found_vars_array(x, variables)
    )
    scores = pd.DataFrame(
        df.found_vars_array.to_list(), index=df.index, columns=variables
    )
    scores["affiliation"] = -1
    if not skip_affiliation:
        scores["affiliation"] = df["affiliation_calc"]
    return scores


def get_manual_eval(path_corpus: Path):
    manual_eval = pd.read_csv(path_corpus / ".." / "manual_eval.csv")
    return manual_eval.drop(columns="index")


def compare_available_manual(repro_df_pdf, repro_df_tex, manual_df, variables):
    avail_manual = manual_df.dropna().drop(columns=["id"])
    repro_df_pdf = repro_df_pdf.drop(columns=["id"])
    repro_df_tex = repro_df_tex.drop(columns=["id"])

    for i in track(range(len(avail_manual)), description="Comparing evaluations..."):
        console.print(f"\n{repro_df_pdf.title[i]}", style="bold")

        df_compare = pd.DataFrame(
            [
                avail_manual.iloc[i][:].values,
                repro_df_pdf.iloc[i][1:].values,
                repro_df_tex.iloc[i][1:].values,
            ],
            columns=variables,
            index=["manual_eval", "repro_pdf_eval", "repro_tex_eval"],
        )

        table = Table(title="Comparison", show_header=True, header_style="bold")
        table.add_column("Variable")
        table.add_column("Manual Evaluation")
        table.add_column("PDF Evaluation")
        table.add_column("TeX Evaluation")

        for var, manual, pdf, tex in df_compare.T.itertuples():
            table.add_row(var, str(manual), str(pdf), str(tex))

        console.print(table)
