import logging

from rich.console import Console
from rich.logging import RichHandler

console = Console(
    quiet=False,
)


FORMAT = "%(message)s"
logging.basicConfig(
    level="WARNING",  # "NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)

log = logging.getLogger("rich")

ext_mapping = {
    "Dependencies": {
        "Dockerfile": [],
        "requirements": [".txt"],
        "setup": [".py"],
        "environment": [".yml"],
        "Pipfile": [],
        "pyproject": [".toml"],
        "pip_reqs": [".txt"],
        "conda_reqs": [".txt"],
    },
    "Wrapper Scripts": {
        "run": [".py", ".sh"],
        "main": [".py", ".sh"],
        "run_all": [".py", ".sh"],
        "run_experiments": [".py", ".sh"],
        "MAKEFILE": [],
        "Makefile": [],
        "Dockerfile": [],
    },
    "Parsed Readme": {
        "readme_requirements": [""],
        "readme_dependencies": [""],
        "readme_setup": [""],
        "readme_install": [""],
    },
    "Others": {
        "No code provided": [""],
        "Code provided but no matches": [""],
    },
}

# Create the reverse mapping
reverse_mapping = {
    file + ext: category
    for category, files in ext_mapping.items()
    for file, extensions in files.items()
    for ext in extensions
}

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
    "test_data": "Test data",
    "training_data": "Training data",
    "validation_data": "Validation data",
}
