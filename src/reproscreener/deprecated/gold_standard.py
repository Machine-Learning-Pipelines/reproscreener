import pandas as pd
from gdrive_downloader import gdrive_get_manual_eval
from pathlib import Path
from typing import List

tex_map_dict = {
    "Research questions": "research_questions",
    "Research problem": "problem",
    "Research method": "research_method",
    "Objective/Goal": "objective",
    "Prediction": "prediction",
    "Method source code": "code_avail_article",
    "Hypothesis": "hypothesis",
    "Training data": "dataset",
    "Experimental setup": "experiment_setup",
}

repo_map_dict = {
    "Dependencies": "software_dependencies",
    "Wrapper Scripts": "wrapper_scripts",
    "Parsed Readme - Requirements": "readme_requirements",
    "Parsed Readme - Dependencies": "readme_dependencies",
    "Parsed Readme - Setup": "readme_setup",
    "Parsed Readme - Install": "readme_install",
}


def split_parsed_readme(df, column):
    dummies = df[column].str.get_dummies(sep=", ")
    df = pd.concat([df, dummies], axis=1)
    return df


def get_gold_standard_ids_from_manual(manual_path: Path) -> List[str]:
    manual_df = gdrive_get_manual_eval(overwrite=False, manual_path=manual_path)
    return manual_df["paper"].tolist()


def summary_table(df, column, number_of_papers):
    variable_counts = df[column].value_counts()
    percentage = variable_counts / number_of_papers * 100

    summary_table = pd.DataFrame(
        {"Reproscreener_Article_Count": variable_counts, "Reproscreener_Percentage": percentage}
    )
    summary_table = summary_table.sort_values(by="Reproscreener_Article_Count", ascending=False)
    summary_table["Reproscreener_Percentage"] = summary_table["Reproscreener_Percentage"].map("{:.2f}%".format)
    return summary_table


def prepare_pivot(df, id_column, map_dict, var_column=None, match_column=None):
    if var_column and match_column:
        df["Mapped_Category"] = df[var_column].map(map_dict)
        df.loc[df[var_column] == "Parsed Readme", "Mapped_Category"] = df.loc[
            df[var_column] == "Parsed Readme", match_column
        ]
        parsed_columns = df["Mapped_Category"].str.get_dummies(sep=", ")
        for col in parsed_columns.columns:
            if col not in df.columns:
                df[col] = parsed_columns[col]
    else:
        df["Mapped_Variable"] = df[var_column].map(map_dict)

    df["Value"] = 1
    if var_column and match_column:
        pivot_df = df.pivot_table(values="Value", index=id_column, columns="Mapped_Category", fill_value=0)
    else:
        pivot_df = df.pivot_table(values="Value", index=id_column, columns="Mapped_Variable", fill_value=0)

    return pivot_df


def compare_with_manual(
    auto_eval_df, manual_eval_df, map_dict, id_column="Paper_ID", total_articles=50, output_format="count"
):
    merged_df = pd.merge(auto_eval_df, manual_eval_df, on=id_column, how="outer")

    results_df = pd.DataFrame(
        columns=[
            "Variable",
            "False_Positives",
            "False_Negatives",
            "Total_Mistakes",
            "Reproscreener_Found",
            "Manual_Found",
        ]
    )

    for key, col in map_dict.items():
        reproscreener_count = merged_df[col + "_reproscreener"].sum()
        manual_count = merged_df[col + "_manual"].sum()

        false_positives = (merged_df[col + "_reproscreener"] > merged_df[col + "_manual"]).sum()
        false_negatives = (merged_df[col + "_reproscreener"] < merged_df[col + "_manual"]).sum()

        total_mistakes = false_positives + false_negatives

        if output_format == "percent":
            # convert counts to percentages
            reproscreener_count = (reproscreener_count / total_articles) * 100
            manual_count = (manual_count / total_articles) * 100
            false_positives = (false_positives / total_articles) * 100
            false_negatives = (false_negatives / total_articles) * 100
            total_mistakes = (total_mistakes / total_articles) * 100

        temp_df = pd.DataFrame(
            {
                "Variable": [key],
                "False_Positives": [false_positives],
                "False_Negatives": [false_negatives],
                "Total_Mistakes": [total_mistakes],
                "Reproscreener_Found": [reproscreener_count],
                "Manual_Found": [manual_count],
            }
        )
        results_df = pd.concat([results_df, temp_df])

    return results_df


if __name__ == "__main__":
    manual_path = Path("case-studies/arxiv-corpus/manual_eval.csv")
    gold_standard_ids = get_gold_standard_ids_from_manual(manual_path=manual_path)
