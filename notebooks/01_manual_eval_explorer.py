import marimo

__generated_with = "0.13.15"
app = marimo.App(width="full")


@app.cell
def _():
    import numpy as np
    import marimo as mo
    return mo, np


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Manual Evaluation Explorer""")
    return


@app.cell
def _():
    import pandas as pd
    from sklearn.metrics import jaccard_score
    from pathlib import Path
    import sys

    module_path = Path("../src/reproscreener")


    sys.path.append(str(module_path))
    sys.path.append(str("src/reproscreener/"))
    from manual_eval import ManualEvaluationParser

    parser = ManualEvaluationParser(str("src/reproscreener/manual_evaluations"))
    evaluations = parser.load_all_evaluations()
    dataset_names = list(evaluations.keys())
    dataset_names
    return evaluations, pd


@app.cell
def _():
    # parser.standardized_metrics.keys()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 1. `abstract`""")
    return


@app.cell
def _(evaluations):
    df_abstract = evaluations['abstract']
    # exclude all columns with names containing "_description"
    df_abstract = df_abstract.drop(columns=["evaluation_type", "source_file", "paper_id"]
                                   +[col for col in df_abstract.columns if "_description" in col])
    df_abstract.head()
    return (df_abstract,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 1. `agreement_gpt`""")
    return


@app.cell
def _(evaluations):
    df_agreement_gpt = evaluations["agreement_gpt"]
    # exclude all columns with names containing "_description"
    df_agreement_gpt = df_agreement_gpt.drop(
        columns=["evaluation_type", "source_file", "paper_id"]
        + [col for col in df_agreement_gpt.columns if "_description" in col]
    )
    # rename all columns to remove the "gpt_" prefix
    df_agreement_gpt = df_agreement_gpt.rename(
        columns={
            col: col.replace("gpt_", "")
            for col in df_agreement_gpt.columns
            if col.startswith("gpt_")
        }
    )
    df_agreement_gpt.head()
    return (df_agreement_gpt,)


@app.cell
def _(df_abstract, mo):
    dropdown = mo.ui.dropdown(df_abstract.columns.tolist(), value="problem")
    dropdown
    return (dropdown,)


@app.cell
def _(df_abstract, df_agreement_gpt, dropdown, np, pd):
    selected_metric = dropdown.value

    # Define column names for clarity
    gpt_col = selected_metric                      # GPT prediction column
    manual_col = selected_metric                   # Original manual label column
    agreement_col = f"{selected_metric}_agreement"  # Agreement indicator column

    # Collect the relevant columns into a single dataframe (aligned on the index)
    evals_per_metric = pd.concat(
        [
            df_agreement_gpt[gpt_col].rename("gpt"),
            df_abstract[manual_col].rename("manual"),
            df_agreement_gpt[agreement_col].rename("agreement"),
        ],
        axis=1,
    )

    # Ensure boolean dtype for logical operations
    evals_per_metric["gpt"] = evals_per_metric["gpt"].astype(bool)
    evals_per_metric["manual"] = evals_per_metric["manual"].astype(bool)

    # Derive the revised manual score: keep GPT value when agreement == 1, otherwise invert it
    evals_per_metric["manual_rev"] = np.where(
        evals_per_metric["agreement"] == 1,
        evals_per_metric["gpt"],
        ~evals_per_metric["gpt"],
    )

    evals_per_metric["manual_vs_manual_rev"] = (
        evals_per_metric["manual"] == evals_per_metric["manual_rev"]
    )
    evals_per_metric["gpt_vs_manual"] = (
        evals_per_metric["gpt"] == evals_per_metric["manual"]
    )
    evals_per_metric["gpt_vs_manual_rev"] = (
        evals_per_metric["gpt"] == evals_per_metric["manual_rev"]
    )

    evals_per_metric

    return (evals_per_metric,)


@app.cell
def _(evals_per_metric, pd):
    # Calculate summary statistics
    summary_df = pd.DataFrame()

    # Add sum of trues
    summary_df["sum_true"] = evals_per_metric[[
        "manual_vs_manual_rev",
        "gpt_vs_manual",
        "gpt_vs_manual_rev",
    ]].sum()

    # Add total count (n)
    summary_df["total_n"] = len(evals_per_metric)

    # Add proportion true
    summary_df["proportion_true"] = evals_per_metric[[
        "manual_vs_manual_rev",
        "gpt_vs_manual",
        "gpt_vs_manual_rev",
    ]].mean()

    # Transpose for better readability
    summary_df = summary_df.T

    summary_df
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 1. `manuscript`""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 1. `abstract`""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 1. `combined_abstract`""")
    return


if __name__ == "__main__":
    app.run()
