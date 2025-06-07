# Architecture

This page documents the public API of the three core modules that power **reproscreener**.

## `paper_analyzer` module

The `paper_analyzer` module is responsible for analysing individual research papers hosted on arXiv.
It can:

- Parse canonical arXiv identifiers from arbitrary arXiv URLs.
- Download either the TeX source bundle (**e-print**) or the PDF of the paper.
- Optionally convert PDFs to Markdown via `docling` for easier text processing.
- Extract reproducibility variables (problem statements, dataset mentions, hypotheses, etc.).
- Detect external links such as source-code or data repositories contained in the manuscript.
- Return the results as a convenient `pandas.DataFrame`.

::: reproscreener.paper_analyzer
    options:
      show_source: false
      heading_level: 3

## `repo_analyzer` module

The `repo_analyzer` module evaluates the structure of a Git repository that claims to implement the research.
Its main tasks are:

- Cloning public repositories (GitHub, GitLab, Bitbucket, …).
- Searching for dependency specification files (e.g. `requirements.txt`, `environment.yml`, `pyproject.toml`, `Dockerfile`, …).
- Detecting wrapper scripts or entry-point files (`run.py`, `main.sh`, `Makefile`, …).
- Parsing the project's `README` for sections that describe installation or requirements.
- Aggregating the findings into a tabular report.

::: reproscreener.repo_analyzer
    options:
      show_source: false
      heading_level: 3

## `keywords` module

The `keywords` module generates the lists of keywords/regular-expression patterns that are used by the analyser modules to identify important concepts inside paper text.
Currently it implements the metrics from [@bhaskarReproscreenerLeveragingLLMs2024].

::: reproscreener.keywords
    options:
      show_source: false
      heading_level: 3 