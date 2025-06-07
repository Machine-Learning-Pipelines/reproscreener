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
poetry add ipykernel streamlit types-tabulate pdfx jupyter-contrib-nbextensions tabulate mkdocs mkdocs-bibtex mkdocs-material pymdown-extensions mkdocstrings-python mkdocs-jupyter mkdocs-macros-plugin markdown-it-py linkify-it-py plotly graphviz pygraphviz --group explore
```

```
idna platformdirs dnspython
```