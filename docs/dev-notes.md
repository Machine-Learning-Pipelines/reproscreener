# Development notes

- Non binary values in JSON guidance format would require custom keyword seach functions
- Include a way to add keywords to JSON and have it assigned to keywordparser
- Refactor so keywords functions are independent of guidance type
- MKDocs over Sphinx?
- Using shutil.copyfileobj to merge all tex files in an article's source folder into 1 file and *then* running keyword search on it. Would likely be more efficient than search over each file and combining the scores.
- [] Dynamic progress (tests/dynamic_progress.py)
- Encoding error due to latin charaters in tex files (UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 in position 58: invalid continuation byte)

```
poetry add arxivscraper requests pandas numpy pathlib flashtext exrex lxml rich typer gitpython pydrive2 urlextract uritools beautifulsoup4
```

```
poetry add flake8 "black[jupyter]" mypy loguru beautifulsoup4 bandit seaborn types-requests pytest pytest-cov --group dev
```

```
poetry add ipykernel streamlit types-tabulate pdfx tabulate jupyter-contrib-nbextensions mkdocs mkdocs-bibtex mkdocs-material pymdown-extensions mkdocstrings-python mkdocs-jupyter mkdocs-macros-plugin markdown-it-py linkify-it-py plotly graphviz pygraphviz --group explore
```

```
idna platformdirs dnspython
```

uv run reproscreener --gold-abstracts-dir ../gold_standard/abstracts --out-csv reports/tables/abstract_regex_gs.csv

uv add     "docling>=2.32.0",
    "exrex>=0.12.0",
    "feedparser>=6.0.11",
    "flashtext>=2.7",
    "gitpython>=3.1.44",
    "highlight-text>=0.2",
    "latex>=0.7.0",
    "lovelyplots>=1.0.2",
    "marimo>=0.13.15",
    "matplotx[all]>=0.3.10",
    "mkdocs>=1.6.1",
    "mkdocs-bibtex>=4.2.5",
    "mkdocs-jupyter>=0.25.1",
    "mkdocs-macros-plugin>=1.3.7",
    "mkdocs-marimo>=0.2.1",
    "mkdocs-material>=9.6.14",
    "mkdocstrings-python>=1.16.12",
    "notebook>=7.4.2",
    "openai>=1.102.0",
    "pandas>=2.2.3",
    "pathlib>=1.0.1",
    "plotly>=6.1.1",
    "pymdown-extensions>=10.15",
    "pytest>=8.4.1",
    "requests>=2.32.3",
    "rich>=14.0.0",
    "scienceplots>=2.1.1",
    "scikit-learn>=1.6.1",
    "seaborn>=0.13.2",
    "streamlit>=1.45.1",
    "urlextract>=1.9.0",
    "watchdog>=6.0.0",

uv add --dev mkdocs mkdocs-bibtex mkdocs-material pymdown-extensions mkdocstrings-python mkdocs-jupyter mkdocs-macros-plugin ruff pytest notebook


