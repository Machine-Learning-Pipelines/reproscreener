import pandas as pd
from reproscreener.gdrive_downloader import gdrive_get_manual_eval
from pathlib import Path
from typing import List


def get_gold_standard_ids_from_manual(manual_path: Path) -> List[str]:
    manual_df = gdrive_get_manual_eval(overwrite=False, manual_path=manual_path)
    return manual_df["paper"].tolist()


def summary_table(df, column, number_of_papers):
    variable_counts = df[column].value_counts()
    percentage = variable_counts / number_of_papers * 100

    summary_table = pd.DataFrame({"Count": variable_counts, "Percentage": percentage})
    summary_table = summary_table.sort_values(by="Count", ascending=False)
    summary_table["Percentage"] = summary_table["Percentage"].map("{:.2f}%".format)
    return summary_table


def prepare_pivot(df, id_column, map_dict, var_column=None, match_column=None, value_column=None):
    if var_column and match_column:
        df["Mapped_Category"] = df[var_column].map(map_dict)
        df.loc[df[var_column] == "Parsed Readme", "Mapped_Category"] = df.loc[
            df[var_column] == "Parsed Readme", match_column
        ]
    else:
        df["Mapped_Variable"] = df[var_column].map(map_dict)

    df["Value"] = 1
    if var_column and match_column:
        pivot_df = df.pivot_table(values="Value", index=id_column, columns="Mapped_Category", fill_value=0)
    else:
        pivot_df = df.pivot_table(values="Value", index=id_column, columns="Mapped_Variable", fill_value=0)

    return pivot_df


# def calc_metrics(df, manual_label, auto_label):
#     precision = precision_score(df[manual_label], df[auto_label])
#     recall = recall_score(df[manual_label], df[auto_label])
#     f1 = f1_score(df[manual_label], df[auto_label])
#     accuracy = accuracy_score(df[manual_label], df[auto_label])
#     kappa = cohen_kappa_score(df[manual_label], df[auto_label])

#     return precision, recall, f1, accuracy, kappa


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


def run_evaluation_repo(df, map_dict, manual_eval):
    summary_df = pd.DataFrame(columns=["Category", "Found_Articles", "Percentage"])

    total_articles = len(df)

    for col in map_dict.values():
        if col in df.columns:
            found_articles = df[col].sum()
            percentage = (found_articles / total_articles) * 100

            temp_df = pd.DataFrame(
                {
                    "Category": [col],
                    "Found_Articles": [found_articles],
                    "Percentage": [percentage],
                }
            )
            summary_df = pd.concat([summary_df, temp_df])
        else:
            temp_df = pd.DataFrame(
                {
                    "Category": [col],
                    "Found_Articles": [0],
                    "Percentage": [0],
                }
            )
            summary_df = pd.concat([summary_df, temp_df])

    return summary_df


def run_evaluation_tex(df, map_dict, manual_eval):
    summary_df = pd.DataFrame(columns=["Category", "Found_Articles", "Percentage"])

    total_articles = len(df)

    for col in map_dict.values():
        if col in df.columns:
            found_articles = df[col].sum()
            percentage = (found_articles / total_articles) * 100

            temp_df = pd.DataFrame(
                {
                    "Category": [col],
                    "Found_Articles": [found_articles],
                    "Percentage": [percentage],
                }
            )
            summary_df = pd.concat([summary_df, temp_df])
        else:
            temp_df = pd.DataFrame(
                {
                    "Category": [col],
                    "Found_Articles": [0],
                    "Percentage": [0],
                }
            )
            summary_df = pd.concat([summary_df, temp_df])

    return summary_df


if __name__ == "__main__":
    manual_path = Path("case-studies/arxiv-corpus/manual_eval.csv")
    gold_standard_ids = get_gold_standard_ids_from_manual(manual_path=manual_path)
