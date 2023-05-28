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
