import streamlit as st
from pathlib import Path
import logging
import pandas as pd
import torch
torch.classes.__path__ = [] # for the torch streamlit error RuntimeError: Tried to instantiate class '__path__._path', 

from analysis.paper_analyzer import analyze_arxiv_paper, parse_arxiv_id
from analysis.repo_analyzer import analyze_github_repo

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

BASE_DOWNLOAD_DIR = Path("./reproscreener_downloads")
ARXIV_DOWNLOAD_DIR = BASE_DOWNLOAD_DIR / "arxiv_papers"
REPO_CLONE_DIR = BASE_DOWNLOAD_DIR / "git_repos"

ARXIV_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPO_CLONE_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(layout="wide", page_title="ReproScreener", initial_sidebar_state="collapsed")

st.title("ReproScreener")
st.subheader("Automating reproducibility evaluations of papers and code")

def clean_title(title):
    """Clean up title text by replacing newlines with spaces"""
    if isinstance(title, str):
        return title.replace("\n", " ").strip()
    return title

def format_list_as_html(items_list):
    """Format a list as HTML bullet points"""
    if not items_list or len(items_list) == 0:
        return "None found"
    
    html = "<ul style='padding-left:1rem; margin-top:0.5rem; margin-bottom:0.5rem'>"
    for item in items_list:
        html += f"<li>{item}</li>"
    html += "</ul>"
    return html

def format_links_as_html(links_list):
    """Format a list of links as clickable HTML links"""
    if not links_list or len(links_list) == 0:
        return "None found"
    
    html = "<ul style='padding-left:1rem; margin-top:0.5rem; margin-bottom:0.5rem'>"
    for link in links_list:
        html += f"<li><a href='{link}' target='_blank'>{link}</a></li>"
    html += "</ul>"
    return html

def prepare_arxiv_display_df(df):
    """Prepare the dataframe for display in Streamlit"""
    if df.empty:
        return df
    
    display_df = df.copy()
    
    display_df["Title"] = display_df["Title"].apply(clean_title)
    
    # Convert lists to formatted HTML for variables and links
    if "Found Variables" in display_df.columns:
        display_df["Variables"] = display_df["Found Variables"].apply(format_list_as_html)
        
    if "Found Links" in display_df.columns:
        display_df["Links"] = display_df["Found Links"].apply(format_links_as_html)
    
    # Drop the original columns that have been transformed
    display_columns = ["Paper ID", "Title"]
    if "Variables" in display_df.columns:
        display_columns.append("Variables")
    if "Links" in display_df.columns:
        display_columns.append("Links")
    if "Error" in display_df.columns and df["Error"].notna().any():
        display_columns.append("Error")
    
    return display_df[display_columns]

def prepare_repo_display_df(df):
    """Prepare the repository dataframe for display"""
    if df.empty:
        return df
    
    display_df = df.copy()
    
    # Format any list columns
    for col in display_df.columns:
        if display_df[col].apply(lambda x: isinstance(x, list)).any():
            display_df[col] = display_df[col].apply(
                lambda x: ", ".join(x) if isinstance(x, list) and x else "None"
            )
    
    return display_df

tab1, tab2 = st.tabs(["Manuscript Evaluation (arXiv)", "Repository Evaluation (GitHub)"])
with tab1:
    # st.header("Manuscript Evaluation (arXiv)")
    # Persist results across interactions in session_state
    if "arxiv_results" not in st.session_state:
        st.session_state["arxiv_results"] = {"tex": pd.DataFrame(), "pdf": pd.DataFrame()}

    col1, col2 = st.columns(2)
    
    with col1:
        arxiv_url_type = st.radio("1. Select the type of arXiv URL to evaluate:", ("TeX", "PDF"))
        # Normalize selection to internal keys used throughout the app
        arxiv_url_type_key = "tex" if arxiv_url_type.strip().lower().startswith("tex") else "pdf"
    with col2:
        arxiv_urls_text = st.text_area("2. Enter arXiv URLs (one per line):", height=100, key="arxiv_urls")

    st.divider()
    evaluate_arxiv_button = st.button("Evaluate arXiv Manuscript(s)", key="eval_arxiv")
    
    # Placeholder for combined display
    combined_placeholder = st.container()

with tab2:
    # st.header("Repository Evaluation (GitHub)")
    repo_urls_text = st.text_area("Enter GitHub Repository URLs (one per line):", height=100, key="repo_urls")
    st.divider()
    evaluate_repo_button = st.button("Evaluate GitHub Repository(s)", key="eval_repo")
    
    repo_results_placeholder = st.empty()

if evaluate_arxiv_button and arxiv_urls_text:
    arxiv_urls = [url.strip() for url in arxiv_urls_text.split('\n') if url.strip()]
    if arxiv_urls:
        processing_placeholder = st.empty()
        processing_placeholder.info("Processing arXiv manuscripts...")
        all_paper_results = pd.DataFrame()
        
        for url in arxiv_urls:
            try:
                log.info(f"Analyzing arXiv URL: {url}")
                paper_id_for_path = parse_arxiv_id(url)
                paper_specific_download_dir = ARXIV_DOWNLOAD_DIR / paper_id_for_path
                result_df = analyze_arxiv_paper(url, paper_specific_download_dir, arxiv_url_type_key)
                all_paper_results = pd.concat([all_paper_results, result_df], ignore_index=True)
            except Exception as e:
                log.error(f"Error processing arXiv URL {url}: {e}")
                error_df = pd.DataFrame({
                    "Paper ID": [url.split('/')[-1]],
                    "Title": ["Error"],
                    "Found Variables": [[]],
                    "Found Links": [[]],
                    "Error": [str(e)]
                })
                all_paper_results = pd.concat([all_paper_results, error_df], ignore_index=True)
        
        # Store results in session state
        st.session_state["arxiv_results"][arxiv_url_type_key] = all_paper_results
        processing_placeholder.empty()
        st.success("arXiv manuscript evaluation complete!")
    else:
        st.warning("Please enter at least one arXiv URL.")

def render_combined_results():
    tex_df = st.session_state["arxiv_results"].get("tex", pd.DataFrame())
    pdf_df = st.session_state["arxiv_results"].get("pdf", pd.DataFrame())

    if tex_df.empty and pdf_df.empty:
        combined_placeholder.info("No evaluations yet.")
        return

    combined_placeholder.markdown("---")
    combined: dict = {}
    has_tex_results = not tex_df.empty
    has_pdf_results = not pdf_df.empty

    def _add_rows(df: pd.DataFrame, fmt: str):
        for _, row in df.iterrows():
            pid = row["Paper ID"]
            entry = combined.setdefault(pid, {
                "title": row["Title"],
                "tex_vars": {}, "pdf_vars": {},
                "tex_links": [], "pdf_links": []
            })
            if fmt == "tex":
                # merge variables
                for k, v in row["Found Variables"].items():
                    entry.setdefault("tex_vars", {}).setdefault(k, set()).update(v)
                entry["tex_links"].extend(row["Found Links"])
            else:
                for k, v in row["Found Variables"].items():
                    entry.setdefault("pdf_vars", {}).setdefault(k, set()).update(v)
                entry["pdf_links"].extend(row["Found Links"])

    if not tex_df.empty:
        _add_rows(tex_df, "tex")
    if not pdf_df.empty:
        _add_rows(pdf_df, "pdf")

    for pid, data in combined.items():
        combined_placeholder.subheader(f"{pid}: {clean_title(data['title'])}")

        # ------------ Variables ------------
        combined_placeholder.markdown("**Found Variables**")
        if has_tex_results and has_pdf_results:
            v_col_tex, v_col_pdf = combined_placeholder.columns(2)

            # TeX variables DataFrame
            if data["tex_vars"]:
                tex_var_df = pd.DataFrame([
                    {"Variable": k, "Matched Phrase": "\n".join(sorted(v))} for k, v in data["tex_vars"].items()
                ])
                v_col_tex.dataframe(tex_var_df, use_container_width=True)
            else:
                v_col_tex.info("No variables found in TeX")

            # PDF variables DataFrame
            if data["pdf_vars"]:
                pdf_var_df = pd.DataFrame([
                    {"Variable": k, "Matched Phrase": "\n".join(sorted(v))} for k, v in data["pdf_vars"].items()
                ])
                v_col_pdf.dataframe(pdf_var_df, use_container_width=True)
            else:
                v_col_pdf.info("No variables found in PDF")
        elif has_tex_results:
            v_col_tex = combined_placeholder.container()
            if data["tex_vars"]:
                tex_var_df = pd.DataFrame([
                    {"Variable": k, "Matched Phrase": "\n".join(sorted(v))} for k, v in data["tex_vars"].items()
                ])
                v_col_tex.dataframe(tex_var_df, use_container_width=True)
            else:
                v_col_tex.info("No variables found in TeX")
        elif has_pdf_results:
            v_col_pdf = combined_placeholder.container()
            if data["pdf_vars"]:
                pdf_var_df = pd.DataFrame([
                    {"Variable": k, "Matched Phrase": "\n".join(sorted(v))} for k, v in data["pdf_vars"].items()
                ])
                v_col_pdf.dataframe(pdf_var_df, use_container_width=True)
            else:
                v_col_pdf.info("No variables found in PDF")

        # ------------ Links ------------
        combined_placeholder.markdown("**Found Links**")
        if has_tex_results and has_pdf_results:
            l_col_tex, l_col_pdf = combined_placeholder.columns(2)

            if data["tex_links"]:
                tex_links_df = pd.DataFrame(sorted(set(data["tex_links"])), columns=["Link"])
                l_col_tex.dataframe(tex_links_df, use_container_width=True)
            else:
                l_col_tex.info("No links found in TeX")

            if data["pdf_links"]:
                pdf_links_df = pd.DataFrame(sorted(set(data["pdf_links"])), columns=["Link"])
                l_col_pdf.dataframe(pdf_links_df, use_container_width=True)
            else:
                l_col_pdf.info("No links found in PDF")
        elif has_tex_results:
            l_col_tex = combined_placeholder.container()
            if data["tex_links"]:
                tex_links_df = pd.DataFrame(sorted(set(data["tex_links"])), columns=["Link"])
                l_col_tex.dataframe(tex_links_df, use_container_width=True)
            else:
                l_col_tex.info("No links found in TeX")
        elif has_pdf_results:
            l_col_pdf = combined_placeholder.container()
            if data["pdf_links"]:
                pdf_links_df = pd.DataFrame(sorted(set(data["pdf_links"])), columns=["Link"])
                l_col_pdf.dataframe(pdf_links_df, use_container_width=True)
            else:
                l_col_pdf.info("No links found in PDF")

render_combined_results()

if evaluate_repo_button and repo_urls_text:
    repo_urls = [url.strip() for url in repo_urls_text.split('\n') if url.strip()]
    if repo_urls:
        repo_results_placeholder.info("Processing GitHub repositories...")
        all_repo_results = []
        
        for url in repo_urls:
            try:
                log.info(f"Analyzing GitHub URL: {url}")
                result = analyze_github_repo(url, REPO_CLONE_DIR)
                all_repo_results.append(result)
            except Exception as e:
                log.error(f"Error processing GitHub URL {url}: {e}")
                all_repo_results.append({"Repo URL": url, "Error": str(e)})
        
        with repo_results_placeholder.container():
            st.subheader("Repository Evaluation Results:")
            
            # Convert results to dataframe
            repo_df = pd.DataFrame()
            for res in all_repo_results:
                if res.get("Error"):
                    error_df = pd.DataFrame({
                        "Repo URL": [res.get("Repo URL", "N/A")],
                        "Error": [res.get("Error")]
                    })
                    repo_df = pd.concat([repo_df, error_df], ignore_index=True)
                else:
                    analysis_data = res.get("Analysis", [])
                    if analysis_data:
                        # Add Repo URL to each row
                        # for item in analysis_data:
                        #     item["Repo URL"] = res.get("Repo URL", "N/A")
                        df = pd.DataFrame(analysis_data)
                        repo_df = pd.concat([repo_df, df], ignore_index=True)
            
            if not repo_df.empty:
                # Prepare display dataframe
                display_df = prepare_repo_display_df(repo_df)
                st.write(display_df.to_html(escape=False), unsafe_allow_html=True)
                
                # Export option
                csv = repo_df.to_csv(index=False)
                current_time = pd.Timestamp.now().strftime("%Y-%m-%dT%H-%M")
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name=f"{current_time}_repo_export.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No results were obtained.")
                
            st.success("GitHub repository evaluation complete!")
    else:
        repo_results_placeholder.warning("Please enter at least one GitHub repository URL.")

st.sidebar.header("About ReproScreener")
st.sidebar.info(
    "This tool helps evaluate the reproducibility of research papers "
    "from arXiv and code repositories from GitHub. "
    "Enter URLs in the respective text areas and click evaluate."
) 