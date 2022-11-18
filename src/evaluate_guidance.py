from pathlib import Path
from pandas import DataFrame, read_csv
from tabulate import tabulate
import keywords


def init_paths(
    num_articles=50, folder_name="mine50/", base_dir="./case-studies/arxiv-corpus/"
):
    # Initialize paths
    # folder_name = folder_name_base + str(num_articles) + '/'
    path_corpus = base_dir + folder_name
    Path(path_corpus + "output/").mkdir(parents=True, exist_ok=True)
    return path_corpus, num_articles


def init_repro_eval(path_corpus, num_articles):
    repro_eval = read_csv(
        path_corpus + "scrape_df_" + str(num_articles) + ".csv", dtype=object
    )
    return repro_eval[["id"]]


def get_found_vars(path_corpus, df):
    # TODO increase PYDEVD_WARN_EVALUATION_TIMEOUT to 15-30s
    print("Reading files...")
    df["soup"] = df["id"].apply(
        lambda x: keywords.read_tei(path_corpus + "parsed_xml/" + x + ".tei.xml")
    )
    df["title"] = df["soup"].apply(lambda x: x.title.getText())
    print("Finding variables in files...")
    df["found_vars"] = df["soup"].apply(lambda x: keywords.find_vars(x))
    df["affiliation_calc"] = df["soup"].apply(lambda x: keywords.find_affiliation(x))
    return df[["id", "title", "found_vars", "affiliation_calc"]]


def calc_found_vars_array(found_vars, variables):
    vars_array = [0] * len(variables)
    for i, var in enumerate(variables):
        vars_array[i] = 1 if var in found_vars else 0
    return vars_array


def set_repro_eval_scores(df, variables):
    df["found_vars_array"] = df["found_vars"].apply(
        lambda x: calc_found_vars_array(x, variables)
    )
    scores = DataFrame(df.found_vars_array.to_list(), index=df.index, columns=variables)
    scores["affiliation"] = df["affiliation_calc"]
    return scores


def get_manual_eval(path_corpus):
    manual_eval = read_csv(path_corpus + "../manual_eval.csv")
    return manual_eval.drop(columns="index")


def compare_available_manual(repro_df, manual_df, variables):
    avail_manual = manual_df.dropna().drop(columns=["id"])
    repro_df = repro_df.drop(columns=["id"])
    for i in range(len(avail_manual)):
        print("\n", repro_df.title[i])
        df_compare = DataFrame(
            [avail_manual.iloc[i][:].values, repro_df.iloc[i][1:].values],
            columns=variables,
            index=["manual_eval", "reproscreener_eval"],
        )
        print(tabulate(df_compare.T, headers="keys", tablefmt="rounded_grid"))
