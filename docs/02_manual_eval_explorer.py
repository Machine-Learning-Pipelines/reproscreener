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

    all_columns = [
      "problem",
      "problem_agreement",
      "objective",
      "objective_agreement",
      "research_method",
      "research_method_agreement",
      "research_questions",
      "research_questions_agreement",
      "pseudocode",
      "pseudocode_agreement",
      "dataset",
      "dataset_agreement",
      "hypothesis",
      "hypothesis_agreement",
      "prediction",
      "prediction_agreement",
      "code_available",
      "code_available_agreement",
      "software_dependencies",
      "software_dependencies_agreement",
      "experiment_setup",
      "experiment_setup_agreement"
    ]
    metric_columns = [col for col in all_columns if not col.endswith("_agreement")]
    return metric_columns, np, pd


@app.cell
def _(pd):
    df_manuscript_manual = pd.read_csv("https://huggingface.co/datasets/adbX/reproscreener_manual_evaluations/resolve/main/manuscript.csv")
    df_manuscript_manual.set_index("paper_id", inplace=True)
    df_manuscript_manual = df_manuscript_manual.drop(
        columns=["evaluation_type", "source_file"]
        + [col for col in df_manuscript_manual.columns if "_description" in col]
    )
    df_manuscript_manual = df_manuscript_manual.rename(columns={"code_available_in_article": "code_available"})
    df_manuscript_manual
    return (df_manuscript_manual,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Reproscreener (regex) vs. Manual evaluations of full manuscripts""")
    return


@app.cell(hide_code=True)
def _(metric_columns, pd):
    df_manuscript_regex = pd.read_csv("https://huggingface.co/datasets/adbX/reproscreener_manual_evaluations/resolve/main/repro_eval_tex.csv")
    df_manuscript_regex = df_manuscript_regex.rename(columns={"method_source_code": "code_available", "id": "paper_id"})
    df_manuscript_regex.set_index("paper_id", inplace=True)
    df_manuscript_regex['dataset'] = df_manuscript_regex['training_data'].astype(bool) + df_manuscript_regex['test_data'].astype(bool) + df_manuscript_regex['validation_data'].astype(bool) + df_manuscript_regex['training_data'].astype(bool)
    df_manuscript_regex = df_manuscript_regex.drop(columns=["index","training_data", "test_data", "validation_data", "title"])
    df_manuscript_regex[metric_columns] = df_manuscript_regex[metric_columns].astype(bool)
    return (df_manuscript_regex,)


@app.cell(hide_code=True)
def _(df_manuscript_manual, df_manuscript_regex, metric_columns, mo, pd):
    # Align indices across manual and regex dataframes and compute agreement
    common_idx = df_manuscript_manual.index.intersection(df_manuscript_regex.index)
    manual_bool = df_manuscript_manual.loc[common_idx, metric_columns].astype(bool)
    regex_bool = df_manuscript_regex.loc[common_idx, metric_columns].astype(bool)

    results_manuscript = {}
    for manuscript_metric in metric_columns:
        manuscript_regex_vals = regex_bool[manuscript_metric]
        manuscript_manual_vals = manual_bool[manuscript_metric]

        results_manuscript[manuscript_metric] = {
            'regex_sum': int(manuscript_regex_vals.sum()),
            'manual_sum': int(manuscript_manual_vals.sum()),
            'regex_proportion': float(manuscript_regex_vals.mean()),
            'regex_manual_agreement': float((manuscript_regex_vals == manuscript_manual_vals).mean()),
            'manual_proportion': float(manuscript_manual_vals.mean()),
            'total_n': int(len(manuscript_regex_vals))
        }

    manuscript_results_df = pd.DataFrame(results_manuscript).T

    tab_decimal_manu = manuscript_results_df
    tab_percent_manu = manuscript_results_df.copy()
    tab_percent_manu['regex_proportion'] = tab_percent_manu['regex_proportion'].mul(100).round(0).astype(int).astype(str).add('%')
    tab_percent_manu['manual_proportion'] = tab_percent_manu['manual_proportion'].mul(100).round(0).astype(int).astype(str).add('%')
    tab_percent_manu['regex_manual_agreement'] = tab_percent_manu['regex_manual_agreement'].mul(100).round(0).astype(int).astype(str).add('%')

    tabs_manu = mo.ui.tabs({"percent": tab_percent_manu, "decimal": tab_decimal_manu})
    tabs_manu
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Reproscreener (regex) vs. Manual evaluations of abstracts""")
    return


@app.cell(hide_code=True)
def _(metric_columns, pd):
    # Load regex results for abstracts computed locally
    df_abstract_regex = pd.read_csv("reports/tables/abstract_regex_gs.csv")
    df_abstract_regex = df_abstract_regex.set_index("paper_id")
    # Ensure boolean dtype for metrics
    available_cols = [c for c in metric_columns if c in df_abstract_regex.columns]
    df_abstract_regex[available_cols] = df_abstract_regex[available_cols].astype(bool)
    df_abstract_regex
    return (df_abstract_regex,)


@app.cell(hide_code=True)
def _(metric_columns, np, pd):
    # Load GPT agreement for abstracts and derive manual columns from agreement
    df_abs_gpt_agreement = pd.read_csv("https://huggingface.co/datasets/adbX/reproscreener_manual_evaluations/resolve/main/agreement_gpt.csv")

    # Clean up columns - exclude metadata and description columns
    df_abs_gpt_agreement = df_abs_gpt_agreement.set_index("paper_id")
    df_abs_gpt_agreement = df_abs_gpt_agreement.drop(
        columns=["evaluation_type", "source_file"]
        + [col for col in df_abs_gpt_agreement.columns if "_description" in col]
    )

    # Remove gpt_ prefix from column names
    df_abs_gpt_agreement = df_abs_gpt_agreement.rename(
        columns={
            col: col.replace("gpt_", "")
            for col in df_abs_gpt_agreement.columns
            if col.startswith("gpt_")
        }
    )

    # Compute manual_<metric> using agreement flip rule
    for abs_metric in metric_columns:
        abs_agreement_col = f"{abs_metric}_agreement"
        if abs_metric in df_abs_gpt_agreement.columns and abs_agreement_col in df_abs_gpt_agreement.columns:
            abs_gpt_vals = df_abs_gpt_agreement[abs_metric].astype(bool)
            abs_agreement_vals = df_abs_gpt_agreement[abs_agreement_col]
            abs_manual_vals = np.where(abs_agreement_vals == 1, abs_gpt_vals, ~abs_gpt_vals)
            df_abs_gpt_agreement[f"manual_{abs_metric}"] = abs_manual_vals.astype(bool)

    return (df_abs_gpt_agreement,)


@app.cell(hide_code=True)
def _(df_abs_gpt_agreement, metric_columns):
    # Build manual abstract evaluations from df_abs_gpt_agreement manual_ columns
    abs_manual_cols_map = {
        f"manual_{m}": m for m in metric_columns if f"manual_{m}" in df_abs_gpt_agreement.columns
    }
    df_abstract_manual = df_abs_gpt_agreement[list(abs_manual_cols_map.keys())].rename(columns=abs_manual_cols_map)
    # Ensure boolean dtype
    df_abstract_manual = df_abstract_manual.astype(bool)
    return (df_abstract_manual,)


@app.cell(hide_code=True)
def _(df_abstract_manual, df_abstract_regex, metric_columns, mo, pd):
    # Align indices and compute agreement for abstracts
    common_idx_abs = df_abstract_manual.index.intersection(df_abstract_regex.index)
    manual_bool_abs = df_abstract_manual.loc[common_idx_abs]
    regex_bool_abs = df_abstract_regex.loc[common_idx_abs]

    abstract_metrics = [m for m in metric_columns if m in manual_bool_abs.columns and m in regex_bool_abs.columns]

    results_abs = {}
    for metric in abstract_metrics:
        regex_vals = regex_bool_abs[metric].astype(bool)
        manual_vals = manual_bool_abs[metric].astype(bool)

        results_abs[metric] = {
            'regex_sum': int(regex_vals.sum()),
            'manual_sum': int(manual_vals.sum()),
            'regex_proportion': float(regex_vals.mean()),
            'regex_manual_agreement': float((regex_vals == manual_vals).mean()),
            'manual_proportion': float(manual_vals.mean()),
            'total_n': int(len(regex_vals)),
        }

    abstract_results_regex_df = pd.DataFrame(results_abs).T

    tab_decimal_abs = abstract_results_regex_df
    tab_percent_abs = abstract_results_regex_df.copy()
    tab_percent_abs['regex_proportion'] = tab_percent_abs['regex_proportion'].mul(100).round(0).astype(int).astype(str).add('%')
    tab_percent_abs['manual_proportion'] = tab_percent_abs['manual_proportion'].mul(100).round(0).astype(int).astype(str).add('%')
    tab_percent_abs['regex_manual_agreement'] = tab_percent_abs['regex_manual_agreement'].mul(100).round(0).astype(int).astype(str).add('%')

    tabs_abs = mo.ui.tabs({"percent": tab_percent_abs, "decimal": tab_decimal_abs})
    tabs_abs
    return (abstract_results_regex_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## GPT-4 vs. Manual evaluations of manuscript abstracts""")
    return


@app.cell(hide_code=True)
def _(metric_columns, mo, np, pd):
    df_gpt_agreement_manu = pd.read_csv("https://huggingface.co/datasets/adbX/reproscreener_manual_evaluations/resolve/main/agreement_gpt.csv")

    # Clean up columns - exclude metadata and description columns
    # Make "paper_id" the index
    df_gpt_agreement_manu = df_gpt_agreement_manu.set_index("paper_id")

    df_gpt_agreement_manu = df_gpt_agreement_manu.drop(
        columns=["evaluation_type", "source_file"]
        + [col for col in df_gpt_agreement_manu.columns if "_description" in col]
    )

    # Remove gpt_ prefix from column names
    df_gpt_agreement_manu = df_gpt_agreement_manu.rename(
        columns={
            col: col.replace("gpt_", "")
            for col in df_gpt_agreement_manu.columns
            if col.startswith("gpt_")
        }
    )

    results = {}
    for manu_metric in metric_columns:
        gpt_col = manu_metric
        agreement_col = f"{manu_metric}_agreement"

        if agreement_col in df_gpt_agreement_manu.columns:
            gpt_vals = df_gpt_agreement_manu[gpt_col].astype(bool)
            agreement_vals = df_gpt_agreement_manu[agreement_col]

            # Calculate revised manual evaluation: keep GPT when agreement=1, invert when agreement=0
            manual_vals_gpt_abs = np.where(agreement_vals == 1, gpt_vals, ~gpt_vals)

            # Add manual_vals_gpt_abs to the agreement_gpt DataFrame
            df_gpt_agreement_manu[f"manual_{manu_metric}"] = manual_vals_gpt_abs.astype(bool)

            results[manu_metric] = {
                'gpt_sum': gpt_vals.sum(),
                'manual_sum': manual_vals_gpt_abs.sum(),
                'gpt_proportion': gpt_vals.mean(),
                'gpt_manual_agreement': agreement_vals.mean(),
                'manual_proportion': manual_vals_gpt_abs.mean(),
                'total_n': len(gpt_vals)
            }
    abstract_results_gpt4_df = pd.DataFrame(results).T

    tab_decimal = abstract_results_gpt4_df
    tab_percent = abstract_results_gpt4_df.copy()
    tab_percent['gpt_proportion'] = tab_percent['gpt_proportion'].mul(100).round(0).astype(int).astype(str).add('%')
    tab_percent['manual_proportion'] = tab_percent['manual_proportion'].mul(100).round(0).astype(int).astype(str).add('%')
    tab_percent['gpt_manual_agreement'] = tab_percent['gpt_manual_agreement'].mul(100).round(0).astype(int).astype(str).add('%')

    tabs = mo.ui.tabs({"percent": tab_percent, "decimal": tab_decimal})
    tabs
    return abstract_results_gpt4_df, df_gpt_agreement_manu


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
def _(df_gpt_agreement_manu, dropdown, pd):
    if dropdown.value:
        selected_metric = dropdown.value
        selected_metric_df = pd.DataFrame({
            'gpt': df_gpt_agreement_manu[selected_metric].astype(bool),
            'manual': df_gpt_agreement_manu[f"manual_{selected_metric}"].astype(bool),
            'agreement': df_gpt_agreement_manu[f"{selected_metric}_agreement"],
        })
        selected_metric_df
    else:
        pd.DataFrame()
    selected_metric_df
    return


@app.cell
def _(abstract_results_gpt4_df, abstract_results_regex_df):
    import matplotlib.pyplot as plt
    import scienceplots
    plt.style.use('science')

    abstract_results_regex_df.regex_manual_agreement
    abstract_results_gpt4_df.gpt_manual_agreement

    return


if __name__ == "__main__":
    app.run()
