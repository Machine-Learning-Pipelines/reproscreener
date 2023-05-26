from pathlib import Path
import logging
import time
import gradio as gr
from reproscreener import tex_eval, repo_eval, report
from reproscreener.utils import log, console
from reproscreener.download_arxiv import download_extract_source


# Mapping from command-line strings to logging levels
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def evaluate_paper(arxiv: str = None, local_arxiv: str = None, log_level: str = "info", progress=gr.Progress()):
    # Set the logging level based on the command-line option
    log.setLevel(LOG_LEVELS[log_level])
    path_download = Path("case-studies/individual")
    path_download.mkdir(parents=True, exist_ok=True)

    if arxiv:
        paper_id = arxiv.split("/")[-1]
        console.rule(f"\nPaper evaluation: {paper_id}")
        path_base = path_download / paper_id
        paper_title, path_paper = download_extract_source(arxiv, path_base / "paper")
    elif local_arxiv:
        path_paper = Path(local_arxiv)
        paper_id = path_paper.name
        console.rule("")
    else:
        path_paper = None

    if path_paper is not None:
        combined_tex = tex_eval.combine_tex_in_folder(path_paper)
        found_vars = tex_eval.find_tex_variables(combined_tex)
        urls = tex_eval.extract_tex_urls(combined_tex)
        found_links = tex_eval.find_data_repository_links(urls)
        _, df_paper_results = tex_eval.paper_evaluation_results(paper_id, paper_title, found_vars, found_links)
        progress(1.0)  # Mark progress as complete
        return df_paper_results


def evaluate_repo(repo: str = None, local_repo: str = None, log_level: str = "info", progress=gr.Progress()):
    # Set the logging level based on the command-line option
    log.setLevel(LOG_LEVELS[log_level])
    path_download = Path("case-studies/individual")
    path_download.mkdir(parents=True, exist_ok=True)

    if repo:
        repo_name = repo.split("/")[-1].split(".git")[0]
        cloned_path = repo_eval.clone_repo(repo, path_download / repo_name)
    elif local_repo:
        cloned_path = Path(local_repo)
    else:
        cloned_path = None

    if cloned_path is not None:
        df_repo_results = repo_eval.evaluate_repo(cloned_path)
        repo_results = repo_eval.repo_eval_table(df_repo_results)
        progress(1.0)  # Mark progress as complete
        return repo_results


with gr.Blocks() as demo:
    gr.Markdown("Reproscreener tool: Evaluate ArXiv papers and Git repositories.")

    with gr.Tab("Evaluate Paper"):
        with gr.Row():
            arxiv_input = gr.Textbox(lines=2, label="arXiv URL")
            local_arxiv_input = gr.Textbox(lines=2, label="Local arXiv Directory")
            log_level_input = gr.Dropdown(choices=["debug", "info", "warning", "error", "critical"], label="Log Level")
            evaluate_paper_button = gr.Button("Evaluate Paper")
        paper_result_output = gr.Textbox()

    evaluate_paper_button.click(
        evaluate_paper,
        inputs=[arxiv_input, local_arxiv_input, log_level_input],
        outputs=paper_result_output,
    )

    with gr.Tab("Evaluate Repo"):
        with gr.Row():
            repo_input = gr.Textbox(lines=2, label="Repo URL")
            local_repo_input = gr.Textbox(lines=2, label="Local Repo Directory")
            log_level_input = gr.Dropdown(choices=["debug", "info", "warning", "error", "critical"], label="Log Level")
            evaluate_repo_button = gr.Button("Evaluate Repo")
        repo_result_output = gr.Textbox()

    evaluate_repo_button.click(
        evaluate_repo,
        inputs=[repo_input, local_repo_input, log_level_input],
        outputs=repo_result_output,
    )

if __name__ == "__main__":
    demo.queue()
    demo.launch()
