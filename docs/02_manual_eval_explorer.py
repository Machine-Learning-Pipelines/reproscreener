import marimo

__generated_with = "0.14.11"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Manual Evaluation Explorer""")
    return


@app.cell(hide_code=True)
def _():
    import pandas as pd
    import numpy as np
    return np, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Reproscreener (regex) vs. Manual evaluations of preprint manuscripts""")
    return


@app.cell
def _(pd):
    df_manuscript = pd.read_csv("https://huggingface.co/datasets/adbX/reproscreener_manual_evaluations/resolve/main/manuscript.csv")

    df_manuscript.set_index("paper_id", inplace=True)
    df_manuscript = df_manuscript.drop(
        columns=["evaluation_type", "source_file"]
        + [col for col in df_manuscript.columns if "_description" in col]
    )

    df_manuscript
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Summary of GPT vs. Manual evaluations on preprint abstracts""")
    return


@app.cell(hide_code=True)
def _(mo, np, pd):
    df_agreement_gpt = pd.read_csv("https://huggingface.co/datasets/adbX/reproscreener_manual_evaluations/resolve/main/agreement_gpt.csv")

    # Clean up columns - exclude metadata and description columns
    # Make "paper_id" the index
    df_agreement_gpt = df_agreement_gpt.set_index("paper_id")

    df_agreement_gpt = df_agreement_gpt.drop(
        columns=["evaluation_type", "source_file"]
        + [col for col in df_agreement_gpt.columns if "_description" in col]
    )

    # Remove gpt_ prefix from column names
    df_agreement_gpt = df_agreement_gpt.rename(
        columns={
            col: col.replace("gpt_", "")
            for col in df_agreement_gpt.columns
            if col.startswith("gpt_")
        }
    )

    all_columns = df_agreement_gpt.columns.tolist()
    metric_columns = [col for col in all_columns if not col.endswith("_agreement")]
    results = {}
    for metric in metric_columns:
        gpt_col = metric
        agreement_col = f"{metric}_agreement"

        if agreement_col in df_agreement_gpt.columns:
            gpt_vals = df_agreement_gpt[gpt_col].astype(bool)
            agreement_vals = df_agreement_gpt[agreement_col]

            # Calculate revised manual evaluation: keep GPT when agreement=1, invert when agreement=0
            manual_vals = np.where(agreement_vals == 1, gpt_vals, ~gpt_vals)

            # Add manual_vals to the agreement_gpt DataFrame
            df_agreement_gpt[f"manual_{metric}"] = manual_vals.astype(bool)

            results[metric] = {
                'gpt_sum': gpt_vals.sum(),
                'manual_sum': manual_vals.sum(),
                'gpt_proportion': gpt_vals.mean(),
                'manual_proportion': manual_vals.mean(),
                'gpt_manual_agreement': agreement_vals.mean(),
                'total_n': len(gpt_vals)
            }
    results_df = pd.DataFrame(results).T

    tab_decimal = results_df
    tab_percent = results_df.copy()
    tab_percent['gpt_proportion'] = tab_percent['gpt_proportion'].mul(100).round(0).astype(int).astype(str).add('%')
    tab_percent['manual_proportion'] = tab_percent['manual_proportion'].mul(100).round(0).astype(int).astype(str).add('%')
    tab_percent['gpt_manual_agreement'] = tab_percent['gpt_manual_agreement'].mul(100).round(0).astype(int).astype(str).add('%')

    tabs = mo.ui.tabs({"percent": tab_percent, "decimal": tab_decimal})
    tabs
    return df_agreement_gpt, metric_columns


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Select a metric to view evaluation results for each paper""")
    return


@app.cell(hide_code=True)
def _(metric_columns, mo):
    dropdown = mo.ui.dropdown(metric_columns, value=metric_columns[0] if metric_columns else None)
    dropdown
    return (dropdown,)


@app.cell(hide_code=True)
def _(df_agreement_gpt, dropdown, pd):
    if dropdown.value:
        selected_metric = dropdown.value
        selected_metric_df = pd.DataFrame({
            'gpt': df_agreement_gpt[selected_metric].astype(bool),
            'manual': df_agreement_gpt[f"manual_{selected_metric}"].astype(bool),
            'agreement': df_agreement_gpt[f"{selected_metric}_agreement"],
        })
        selected_metric_df
    else:
        pd.DataFrame()
    selected_metric_df
    return


if __name__ == "__main__":
    app.run()
