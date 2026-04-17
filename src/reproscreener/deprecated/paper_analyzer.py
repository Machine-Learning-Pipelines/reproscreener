import glob
import urllib.parse
from pathlib import Path
from typing import List, Set, Tuple, Dict
import logging
import re

import feedparser
import requests
import tarfile
from flashtext import KeywordProcessor
from urlextract import URLExtract
import pandas as pd
from docling.document_converter import DocumentConverter

from analysis.keywords import generate_gunderson_dict

log = logging.getLogger(__name__)

labels_mapping = {
    "experiment_setup": "Experimental setup",
    "hypothesis": "Hypothesis",
    "method_source_code": "Method source code",
    "objective": "Objective/Goal",
    "prediction": "Prediction",
    "problem": "Research problem",
    "pseudocode": "Pseudocode",
    "research_method": "Research method",
    "research_questions": "Research questions",
    "dataset": "Dataset",
}

ARXIV_PREFIXES = {"abs", "pdf", "src", "e-print", "format"}

def parse_arxiv_id(arxiv_url: str) -> str:
    """Extract the canonical arXiv identifier (without version or extension)
    from *arxiv_url* which may be any of:
    • https://arxiv.org/abs/1909.00066v1
    • https://arxiv.org/pdf/1909.00066.pdf
    • https://arxiv.org/pdf/1909.00066v2.pdf
    • https://arxiv.org/src/1909.00066
    • https://arxiv.org/e-print/1909.00066
    Returns the bare identifier, e.g. ``1909.00066``.
    """
    parsed = urllib.parse.urlparse(arxiv_url)
    path_parts = [p for p in parsed.path.split("/") if p]

    if not path_parts:
        raise ValueError(f"Cannot parse arXiv ID from URL: {arxiv_url}")

    # Discard leading folder like 'abs', 'pdf', etc.
    if path_parts[0] in ARXIV_PREFIXES and len(path_parts) > 1:
        remaining = path_parts[1:]
        candidate = "/".join(remaining)
    else:
        candidate = path_parts[0]

    # Remove extension (.pdf, .ps, .gz, etc.)
    candidate = re.sub(r"\.(pdf|ps|gz|tar)$", "", candidate, flags=re.IGNORECASE)

    # Remove version suffix (v\d+)
    candidate = re.sub(r"v\d+$", "", candidate)

    return candidate

def download_extract_source(arxiv_url: str, path_download: Path) -> Tuple[str, Path]:
    """
    Downloads and extracts the source code of an ArXiv paper from its URL.
    Also retrieves the paper title from the arXiv API.
    Returns the paper title and the download directory path.
    """
    arxiv_id = parse_arxiv_id(arxiv_url)

    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    feed = feedparser.parse(api_url)
    if not feed.entries:
        raise ValueError(f"Could not fetch paper details for arXiv ID: {arxiv_id}")
    title = feed.entries[0].title

    if path_download.exists() and any(path_download.iterdir()):
        log.info(f"Source for {arxiv_id} already exists at {path_download}. Skipping download.")
        return title, path_download

    log.info(f"[bold green]Downloading and processing paper {arxiv_id}...")

    source_url = f"https://arxiv.org/e-print/{arxiv_id}"
    
    path_download.mkdir(parents=True, exist_ok=True)

    try:
        response = requests.get(source_url, stream=True, timeout=10)
        response.raise_for_status()
        with tarfile.open(fileobj=response.raw, mode="r|gz") as tar:
            tar.extractall(path_download)
    except requests.exceptions.RequestException as e:
        log.error(f"Error downloading {source_url}: {e}")
        raise
    except tarfile.TarError as e:
        log.error(f"Error extracting {source_url} to {path_download}: {e}")
        raise
    
    log.info(f"Downloaded source: {source_url} to {path_download}")
    return title, path_download

def download_pdf_and_convert(arxiv_url: str, path_download: Path) -> Tuple[str, Path]:
    """
    Downloads a PDF from arXiv and converts it to markdown using docling.
    Returns the paper title and the path to the markdown file.
    """
    arxiv_id = parse_arxiv_id(arxiv_url)

    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    feed = feedparser.parse(api_url)
    if not feed.entries:
        raise ValueError(f"Could not fetch paper details for arXiv ID: {arxiv_id}")
    title = feed.entries[0].title

    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
    path_download.mkdir(parents=True, exist_ok=True)
    markdown_path = path_download / f"{arxiv_id}.md"

    if markdown_path.exists() and markdown_path.stat().st_size > 0:
        log.info(f"Markdown for {arxiv_id} already exists at {markdown_path}. Skipping download and conversion.")
        return title, path_download

    log.info(f"Downloading and processing PDF paper {arxiv_id}...")

    try:
        converter = DocumentConverter()
        result = converter.convert(pdf_url)
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(result.document.export_to_markdown())
        log.info(f"Downloaded and converted PDF: {pdf_url} to {markdown_path}")
    except Exception as e:
        log.error(f"Error downloading and converting PDF {pdf_url}: {e}")
        raise
    
    return title, path_download

def combine_files_in_folder(folder_path: Path, file_extensions: List[str] = [".tex", ".md", ".txt"]) -> Path:
    """
    Combine all files with specified extensions in a given directory into a single file.
    """
    combined_path = folder_path / "combined.txt"
    with open(combined_path, "w", encoding="utf-8", errors="replace") as outfile:
        for extension in file_extensions:
            for name in glob.glob(f"{folder_path}/*{extension}"):
                try:
                    with open(name, encoding="utf-8", errors="replace") as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    log.warning(f"Could not read file {name}: {e}")
    return combined_path

def find_variables(combined_path: Path):
    """Return a list of (variable_category, matched_phrase) pairs found in the paper."""
    keyword_dict = generate_gunderson_dict()

    pattern_to_category = {}
    keyword_processor = KeywordProcessor(case_sensitive=True)

    for category, phrases in keyword_dict.items():
        for phrase in phrases:
            keyword_processor.add_keyword(phrase)
            pattern_to_category[phrase] = category

    found: Dict[str, set] = {cat: set() for cat in keyword_dict.keys()}
    try:
        with open(combined_path, "r", errors="replace", encoding="utf-8") as f:
            for line in f:
                matches = keyword_processor.extract_keywords(line, span_info=False)
                for m in matches:
                    cat = pattern_to_category.get(m)
                    if cat:
                        found[cat].add(m)
    except Exception as e:
        log.warning(f"Could not process combined file for variables: {e}")

    # Convert sets to sorted lists and drop empty categories
    return {cat: sorted(list(phrases)) for cat, phrases in found.items() if phrases}

def extract_urls(combined_path: Path) -> Set[str]:
    """
    Extract URLs from the combined file.
    """
    urls: Set[str] = set()
    try:
        with open(combined_path, "r", errors="replace", encoding="utf-8") as f:
            data = f.read()
        extractor = URLExtract()
        urls = set(extractor.find_urls(data))
        log.debug("All urls:\n %s \n", urls)
    except Exception as e:
        log.warning(f"Could not process combined file for URLs: {e}")
    return urls

def find_data_repository_links(
    url_list: Set[str], allowed_domains: List[str] = ["github", "gitlab", "bitbucket", "zenodo"]
) -> List[str]:
    """
    Find URLs belonging to allowed domains.
    """
    found_list = []
    for url in url_list:
        try:
            parsed_url = urllib.parse.urlparse(url)
            if any(domain in parsed_url.netloc for domain in allowed_domains):
                found_list.append(url)
                log.debug(f"Found {parsed_url.netloc} link: {url}")
        except Exception as e:
            log.warning(f"Could not parse URL {url}: {e}")
    return found_list

def analyze_content(
    folder_path: Path, paper_id: str, title: str
) -> pd.DataFrame:
    """
    Evaluate a paper by extracting variables and URLs from its files.
    Returns a DataFrame with evaluation results.
    """
    combined_path = combine_files_in_folder(folder_path)
    if not combined_path.exists() or combined_path.stat().st_size == 0:
        log.warning(f"combined.txt is empty or not found for {paper_id}. Skipping analysis.")
        return pd.DataFrame({
            "Paper ID": [paper_id],
            "Title": [title],
            "Found Variables": [[]],
            "Found Links": [[]],
            "Error": ["No content to analyze"]
        })
        
    found_vars = find_variables(combined_path)
    found_urls = extract_urls(combined_path)
    found_links = find_data_repository_links(found_urls)

    return pd.DataFrame({
        "Paper ID": [paper_id],
        "Title": [title],
        "Found Variables": [found_vars],
        "Found Links": [sorted(list(found_links))],
    })

def analyze_arxiv_paper(arxiv_url: str, download_dir: Path, url_type: str = "tex") -> pd.DataFrame:
    """
    Main function to download, extract, and analyze an arXiv paper.
    
    Parameters:
    -----------
    arxiv_url : str
        The arXiv URL of the paper
    download_dir : Path
        Directory to download and store the paper
    url_type : str
        Type of arXiv URL, either "tex" or "pdf"
        
    Returns:
    --------
    pd.DataFrame
        Analysis results as a DataFrame
    """
    paper_id = parse_arxiv_id(arxiv_url)
    
    paper_download_path = download_dir / paper_id / "paper_source"
    
    try:
        if url_type == "tex":
            title, extracted_path = download_extract_source(arxiv_url, paper_download_path)
        else:  # pdf
            title, extracted_path = download_pdf_and_convert(arxiv_url, paper_download_path)
            
        log.info(f"Successfully processed {arxiv_url} to {extracted_path}")
        
        analysis_results = analyze_content(extracted_path, paper_id, title)
        return analysis_results
    except Exception as e:
        log.error(f"Failed to analyze arXiv paper {arxiv_url}: {e}")
        return pd.DataFrame({
            "Paper ID": [paper_id],
            "Title": ["Error fetching title"],
            "Found Variables": [[]],
            "Found Links": [[]],
            "Error": [str(e)]
        })

def _build_keyword_processor_and_map() -> Tuple[KeywordProcessor, Dict[str, str]]:
    """
    Build a KeywordProcessor and a reverse map from phrase -> category using
    the Gunderson keyword dictionary.
    """
    keyword_dict = generate_gunderson_dict()
    pattern_to_category: Dict[str, str] = {}
    keyword_processor = KeywordProcessor(case_sensitive=True)

    for category, phrases in keyword_dict.items():
        for phrase in phrases:
            keyword_processor.add_keyword(phrase)
            pattern_to_category[phrase] = category

    return keyword_processor, pattern_to_category

def extract_category_presence_from_text(text: str) -> Dict[str, bool]:
    """
    Given raw text (e.g., an abstract), return boolean presence for each
    category relevant to the gold-standard CSV output.

    Output keys (CSV columns):
    - problem
    - objective
    - research_method
    - research_questions
    - pseudocode
    - dataset
    - hypothesis
    - prediction
    - code_available (mapped from method_source_code)
    - software_dependencies
    - experiment_setup
    """
    # Initialize all as False
    presence: Dict[str, bool] = {
        "problem": False,
        "objective": False,
        "research_method": False,
        "research_questions": False,
        "pseudocode": False,
        "dataset": False,
        "hypothesis": False,
        "prediction": False,
        "code_available": False,  # maps from method_source_code
        "software_dependencies": False,
        "experiment_setup": False,
    }

    keyword_processor, pattern_to_category = _build_keyword_processor_and_map()

    # Extract keywords across entire text at once
    matches = keyword_processor.extract_keywords(text, span_info=False)
    for m in matches:
        category = pattern_to_category.get(m)
        if not category:
            continue
        if category == "method_source_code":
            presence["code_available"] = True
        elif category in presence:
            presence[category] = True
        # Categories not requested in CSV (e.g., hardware_specifications) are ignored

    return presence

def analyze_abstract_file(abstract_path: Path) -> Dict[str, object]:
    """
    Analyze a single abstract .txt file and return a row dict for the CSV.
    The paper_id is derived from the filename stem.
    """
    try:
        text = abstract_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        log.warning(f"Could not read abstract file {abstract_path}: {e}")
        text = ""

    paper_id = abstract_path.stem
    presence = extract_category_presence_from_text(text)

    row: Dict[str, object] = {"paper_id": paper_id}
    row.update(presence)
    return row

def analyze_abstracts_directory(abstracts_dir: Path) -> pd.DataFrame:
    """
    Analyze all .txt abstracts in a directory and return a DataFrame with
    the expected CSV columns.
    """
    abstracts = sorted(abstracts_dir.glob("*.txt"))
    rows: List[Dict[str, object]] = []
    for path in abstracts:
        rows.append(analyze_abstract_file(path))

    # Ensure exact column order as requested
    columns = [
        "paper_id",
        "problem",
        "objective",
        "research_method",
        "research_questions",
        "pseudocode",
        "dataset",
        "hypothesis",
        "prediction",
        "code_available",
        "software_dependencies",
        "experiment_setup",
    ]

    if not rows:
        # Return empty DataFrame with the correct columns
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(rows)
    # Fill missing columns with False
    for col in columns:
        if col not in df.columns:
            df[col] = False
    df = df[columns]
    return df

def main():
    logging.basicConfig(level=logging.INFO)
    sample_arxiv_url = "https://arxiv.org/abs/2111.12673"
    temp_download_dir = Path("./temp_arxiv_downloads")
    results = analyze_arxiv_paper(sample_arxiv_url, temp_download_dir)
    print("\nPaper Analysis Results:")
    print(results)

if __name__ == '__main__':
    main()