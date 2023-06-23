from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
import pandas as pd
from reproscreener.gdrive_downloader import gdrive_get_manual_eval
from pathlib import Path
from typing import List


def get_gold_standard_ids_from_manual(manual_path: Path) -> List[str]:
    manual_df = gdrive_get_manual_eval(overwrite=False, manual_path=manual_path)
    return manual_df["paper"].tolist()


def process_parsed_readme(
    df, manual_eval, mapped_category_col="Mapped_Category", matched_file_col="Matched_File", paper_id_col="Paper_ID"
):
    parsed_readme_mask = df[mapped_category_col] == "parsed_readme"
    df.loc[df[parsed_readme_mask][paper_id_col], "parsed_readme"] = df[parsed_readme_mask][matched_file_col]

    # Convert the 'parsed_readme' column in manual_eval to the same format
    manual_eval["parsed_readme"] = manual_eval["parsed_readme"].apply(lambda x: "Parsed Readme" if x else "No Readme")


def process_no_code_provided(df, category_col="Category", matched_file_col="Matched_File"):
    df["no_code_provided"] = ((df[category_col] == "Others") & (df[matched_file_col] == "No code provided")).astype(int)
    df["code_provided_no_match"] = (
        (df[category_col] == "Others") & (df[matched_file_col] == "Code provided but no matches")
    ).astype(int)


def prepare_pivot(df, id_column, map_column, value_column, map_dict):
    df["Mapped_Variable"] = df[map_column].map(map_dict)
    df["Value"] = 1  # Assign 1 to found variables
    pivot_df = df.pivot_table(values="Value", index=id_column, columns="Mapped_Variable", fill_value=0)
    return pivot_df


def summary_table(df, column, number_of_papers):
    variable_counts = df[column].value_counts()
    percentage = variable_counts / number_of_papers * 100

    summary_table = pd.DataFrame({"Count": variable_counts, "Percentage": percentage})
    summary_table = summary_table.sort_values(by="Count", ascending=False)
    summary_table["Percentage"] = summary_table["Percentage"].map("{:.2f}%".format)
    return summary_table


def calc_metrics(df, col1, col2):
    precision = precision_score(df[col1], df[col2])
    recall = recall_score(df[col1], df[col2])
    f1 = f1_score(df[col1], df[col2])
    accuracy = accuracy_score(df[col1], df[col2])

    return precision, recall, f1, accuracy


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
    # Add other mappings if necessary
}

if __name__ == "__main__":
    manual_path = Path("case-studies/arxiv-corpus/manual_eval.csv")
    gold_standard_ids = get_gold_standard_ids_from_manual(manual_path=manual_path)
