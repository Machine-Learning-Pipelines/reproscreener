import evaluate_guidance as eg
from pandas import concat, merge
import scrape_arxiv as sa

# import streamlit as st
import read_tex

# st.set_page_config(layout="wide")


def run_reproscreener(
    max_articles,
    path_corpus,
    eval_tex=True,
    eval_pdf=False,
    eval_manual=False,
    compare_manual=False,
):
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
    repro_eval = eg.init_repro_eval(path_corpus)

    if eval_tex:
        found_vars_tex = read_tex.get_found_vars_tex(path_corpus, repro_eval)
        repro_eval_filled_tex = eg.set_repro_eval_scores(
            concat([repro_eval, found_vars_tex], axis=0, join="inner"),
            gunderson_vars,
            skip_affiliation=True,
        )
        output_repro_eval_tex = merge(
            found_vars_tex[["id", "title"]],
            repro_eval_filled_tex,
            left_index=True,
            right_index=True,
        ).drop_duplicates(subset=["id"])
        output_repro_eval_tex.to_csv(
            path_corpus + "output/repro_eval_tex.csv", index_label="index"
        )

    if eval_pdf:
        found_vars_pdf = eg.get_found_vars(path_corpus, repro_eval)
        repro_eval_filled_pdf = eg.set_repro_eval_scores(
            concat([repro_eval, found_vars_pdf], axis=0, join="inner"), gunderson_vars
        )
        output_repro_eval_pdf = merge(
            found_vars_pdf[["id", "title"]],
            repro_eval_filled_pdf,
            left_index=True,
            right_index=True,
        ).drop_duplicates(subset=["id"])

        output_repro_eval_pdf.to_csv(
            path_corpus + "output/repro_eval.csv", index_label="index"
        )

    # print(output_repro_eval_tex)
    # print(eg.get_manual_eval(path_corpus))

    if compare_manual:
        eg.compare_available_manual(
            output_repro_eval_pdf,
            output_repro_eval_tex,
            eg.get_manual_eval(path_corpus),
            gunderson_vars,
        )
    # eg.compare_available_manual(output_repro_eval_tex, eg.get_manual_eval(path_corpus), gunderson_vars)

    return output_repro_eval_tex


if __name__ == "__main__":
    max_articles = 102
    folder_name = "mine102/"

    base_dir = "./case-studies/arxiv-corpus/"
    path_corpus = sa.init_paths(base_dir, folder_name)

    run_reproscreener(
        max_articles,
        path_corpus,
        eval_tex=True,
        eval_pdf=True,
        eval_manual=True,
        compare_manual=True,
    )
# st.dataframe(run_reproscreener(), use_container_width=True)
