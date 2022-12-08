import evaluate_guidance as eg
from pandas import concat, merge
import streamlit as st
import read_tex
st.set_page_config(layout="wide")

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
    num_articles=50
    path_corpus = eg.init_paths(num_articles = 50, folder_name="mine50-csLG/")
    repro_eval = eg.init_repro_eval(path_corpus, num_articles)
    
    found_vars_pdf = eg.get_found_vars(path_corpus, repro_eval)
    found_vars_tex = read_tex.get_found_vars_tex(path_corpus, repro_eval)

    repro_eval_filled_pdf = eg.set_repro_eval_scores(
        concat([repro_eval, found_vars_pdf], axis=0, join="inner"),
        gunderson_vars
    )
    repro_eval_filled_tex = eg.set_repro_eval_scores(
        concat([repro_eval, found_vars_tex], axis=0, join="inner"),
        gunderson_vars,
        skip_affiliation=True
    )
    
    output_repro_eval_pdf = merge(
        found_vars_pdf[["id", "title"]],
        repro_eval_filled_pdf,
        left_index=True,
        right_index=True,
    ).drop_duplicates(subset=["id"])
    
    output_repro_eval_tex = merge(
        found_vars_tex[["id", "title"]],
        repro_eval_filled_tex,
        left_index=True,
        right_index=True,
    ).drop_duplicates(subset=["id"])

    # print(output_repro_eval_tex)
    # print(eg.get_manual_eval(path_corpus))
    output_repro_eval_pdf.to_csv(path_corpus + "output/repro_eval.csv", index_label="index")
    output_repro_eval_tex.to_csv(path_corpus + "output/repro_eval_tex.csv", index_label="index")
    
    eg.compare_available_manual(output_repro_eval_pdf, output_repro_eval_tex, eg.get_manual_eval(path_corpus), gunderson_vars)
    # eg.compare_available_manual(output_repro_eval_tex, eg.get_manual_eval(path_corpus), gunderson_vars)

    return output_repro_eval_pdf

st.dataframe(run_reproscreener(), use_container_width=True)
