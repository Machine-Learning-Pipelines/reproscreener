import evaluate_guidance as eg
from pandas import concat, merge


def run_reproscreener():
    """_summary_
    fall subfunctions to run processing steps
    """
    gunderson_vars = [
        "problem",
        "objective",
        "research_method",
        "research_questions",
        "pseudocode",
        "training_data",
        "validation_data",
        "test_data",
        "results",
        "hypothesis",
        "prediction",
        "method_source_code",
        "hardware_specifications",
        "software_dependencies",
        "experiment_setup",
        "experiment_source_code",
        "affiliation",
    ]

    path_corpus, num_articles = eg.init_paths(folder_name="mine50-csLG/")
    repro_eval = eg.init_repro_eval(path_corpus, num_articles)
    found_vars = eg.get_found_vars(path_corpus, repro_eval)
    repro_eval_filled = eg.set_repro_eval_scores(
        concat([repro_eval, found_vars], axis=0, join="inner"), gunderson_vars
    )
    output_repro_eval = merge(
        found_vars[["id", "title"]],
        repro_eval_filled,
        left_index=True,
        right_index=True,
    ).drop_duplicates(subset=["id"])

    # print(output_repro_eval)
    # print(eg.get_manual_eval(path_corpus))
    output_repro_eval.to_csv(path_corpus + "output/repro_eval.csv", index_label="index")
    manual_df = eg.get_manual_eval(path_corpus)
    eg.compare_available_manual(output_repro_eval, manual_df, gunderson_vars)

    return output_repro_eval


run_reproscreener()
