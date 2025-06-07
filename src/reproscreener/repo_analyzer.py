import re
from pathlib import Path
from typing import List, Tuple, Dict, Any
import logging
import json
import shutil

import git
import pandas as pd

log = logging.getLogger(__name__)

ext_mapping = {
    "run": [".py", ".sh"],
    "main": [".py", ".sh"],
    "run_all": [".py", ".sh"],
    "run_experiments": [".py", ".sh"],
    "Dockerfile": [],
    "requirements": [".txt"],
    "setup": [".py"],
    "environment": [".yml"],
    "Pipfile": [],
    "pyproject": [".toml"],
    "pip_reqs": [".txt"],
    "conda_reqs": [".txt"],
    "MAKEFILE": [],
    "Makefile": [],
    # For readme sections
    "readme_requirements": [], 
    "readme_dependencies": [],
    "readme_setup": [],
    "readme_install": [],
}

def clone_repo(repo_url: str, cloned_path: Path, overwrite: bool = False) -> Path:
    """
    Clone a repository from the given URL to the given path.
    If the repository already exists, it won't be overwritten unless specified.
    """
    if cloned_path.exists() and not overwrite:
        log.info(f"Repo directory already exists: {cloned_path}, skipping clone.")
        return cloned_path
    elif cloned_path.exists() and overwrite:
        log.info(f"Overwriting existing directory: {cloned_path}")
        try:
            shutil.rmtree(cloned_path)
        except Exception as e:
            log.error(f"Failed to remove existing directory {cloned_path}: {e}")
            raise

    cloned_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        log.info(f"Cloning repo {repo_url} to {cloned_path}...")
        git.Repo.clone_from(repo_url, str(cloned_path))
        log.info(f"Successfully cloned repo: {repo_url} to {cloned_path}")
        return cloned_path
    except git.exc.GitCommandError as error:
        log.error(f"Failed to clone repo: {repo_url}. Error: {error}")
        raise

def check_files(dir_path: Path, files_to_check: List[str], current_ext_mapping: Dict[str, List[str]]) -> Tuple[List[str], List[str]]:
    """
    Check if the given files exist in the directory based on ext_mapping.
    """
    found_files = []
    not_found_files = list(files_to_check)

    for f_path in dir_path.glob("*"):
        f_stem = f_path.stem
        f_name_no_ext = f_path.name.split('.')[0] # For files like Dockerfile with no stem
        
        # Check against files_to_check using stem or name (for files like Dockerfile)
        check_stem = f_stem if f_stem in files_to_check else f_name_no_ext

        if check_stem in files_to_check:
            allowed_extensions = current_ext_mapping.get(check_stem, [])
            # If no extensions are specified (e.g., Dockerfile, Pipfile), or if suffix matches
            if not allowed_extensions or f_path.suffix in allowed_extensions:
                found_files.append(f_path.name)
                if check_stem in not_found_files:
                    not_found_files.remove(check_stem)
    
    return found_files, not_found_files

def check_dependencies(dir_path: Path) -> Tuple[List[str], List[str]]:
    dependency_files = [
        "Dockerfile", "requirements", "setup", "environment", 
        "Pipfile", "pyproject", "pip_reqs", "conda_reqs"
    ]
    return check_files(dir_path, dependency_files, ext_mapping)

def check_wrapper_scripts(dir_path: Path) -> Tuple[List[str], List[str]]:
    wrapper_files = [
        "run", "main", "run_all", "run_experiments", 
        "MAKEFILE", "Makefile", "Dockerfile"
    ]
    return check_files(dir_path, wrapper_files, ext_mapping)

def check_parsed_readme(dir_path: Path) -> Tuple[List[str], List[str]]:
    readme_path_md = dir_path / "README.md"
    readme_path_rst = dir_path / "README.rst"
    readme_path = None

    if readme_path_md.is_file():
        readme_path = readme_path_md
    elif readme_path_rst.is_file():
        readme_path = readme_path_rst
        
    possible_headers = ["requirements", "dependencies", "setup", "install"]
    found_headers_clean: List[str] = [] # e.g. ['requirements']
    
    if readme_path and readme_path.is_file():
        try:
            with open(readme_path, "r", encoding="utf-8", errors="replace") as file:
                content = file.read()
                # Regex for Markdown and RST headers
                # For Markdown: ^\s*#{1,6}\s*(...)
                # For RST: ^(...)\n[=-`:'."~^_*#+]{3,}\s*$
                found_headers_raw = re.findall(
                    r"^\s*(?:#{1,6}\s*|\*\*\s*)(\b(?:" + "|".join(possible_headers) + r")\b)[	 ]*(?:\*\*|:)?\s*\n?", 
                    content, 
                    re.MULTILINE | re.IGNORECASE
                )
                found_headers_clean = [header.lower() for header in found_headers_raw]
                found_headers_clean = sorted(list(set(found_headers_clean))) 

        except Exception as e:
            log.warning(f"Could not parse README {readme_path}: {e}")

    not_found_headers = list(set(possible_headers) - set(found_headers_clean))
    return ["readme_" + header for header in found_headers_clean], ["readme_" + header for header in not_found_headers]

def analyze_repository_structure(repo_path: Path) -> pd.DataFrame:
    """
    Evaluate a repository by checking the existence of certain files and sections in README.
    Returns a DataFrame with the evaluation results.
    """
    ## Dependencies
    dependency_items = [
        "Dockerfile", "requirements", "setup", "environment",
        "Pipfile", "pyproject", "pip_reqs", "conda_reqs",
    ]
    # Map stem -> full filename (e.g. {"requirements": "requirements.txt"})
    dep_found_files, _ = check_dependencies(repo_path)
    dep_found_map = {Path(f).stem: f for f in dep_found_files}

    data: list[list[Any]] = []

    for item in dependency_items:
        found = item in dep_found_map
        variable_name = dep_found_map.get(item, item)
        found_extension = Path(variable_name).suffix if found else ""
        data.append([
            "Dependencies",
            variable_name,
            found,
            ext_mapping.get(item, []),
            found_extension,
        ])

    ## Wrapper scripts
    wrapper_items = [
        "run", "main", "run_all", "run_experiments",
        "MAKEFILE", "Makefile", "Dockerfile",
    ]
    wrapper_found_files, _ = check_wrapper_scripts(repo_path)
    wrapper_found_map = {Path(f).stem: f for f in wrapper_found_files}

    for item in wrapper_items:
        found = item in wrapper_found_map
        variable_name = wrapper_found_map.get(item, item)
        found_extension = Path(variable_name).suffix if found else ""
        data.append([
            "Wrapper Scripts",
            variable_name,
            found,
            ext_mapping.get(item, []),
            found_extension,
        ])

    ## Parsed README
    readme_headers = ["requirements", "dependencies", "setup", "install"]
    readme_found_headers, _ = check_parsed_readme(repo_path)
    readme_found_set = set(readme_found_headers)

    for header in readme_headers:
        item = f"readme_{header}"
        found = item in readme_found_set
        data.append([
            "Parsed Readme",
            item,
            found,
            ext_mapping.get(item, []),
            "",
        ])

    return pd.DataFrame(
        data,
        columns=["Category", "Variable", "Found?", "Extensions", "Found_Extension"],
    )

def analyze_github_repo(repo_url: str, clone_dir: Path) -> Dict[str, Any]:
    """
    Main function to clone and analyze a GitHub repository.
    """
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_clone_path = clone_dir / repo_name

    results: Dict[str, Any] = {
        "Repo URL": repo_url,
        "Clone Path": str(repo_clone_path),
    }
    try:
        cloned_path = clone_repo(repo_url, repo_clone_path, overwrite=True) # Overwrite
        log.info(f"Successfully cloned {repo_url} to {cloned_path}")
        
        df_repo_results = analyze_repository_structure(cloned_path)
        results["Analysis"] = df_repo_results.to_dict(orient='records')
        results["Error"] = None
        
    except Exception as e:
        log.error(f"Failed to analyze GitHub repo {repo_url}: {e}")
        results["Analysis"] = []
        results["Error"] = str(e)
    
    return results

def main():
    logging.basicConfig(level=logging.INFO)
    sample_repo_url = "https://github.com/HanGuo97/soft-Q-learning-for-text-generation"
    temp_clone_dir = Path("./temp_repo_clones")
    repo_analysis = analyze_github_repo(sample_repo_url, temp_clone_dir)
    print("\nRepo Analysis Results:")
    print(json.dumps(repo_analysis, indent=2))

if __name__ == '__main__':
    main()