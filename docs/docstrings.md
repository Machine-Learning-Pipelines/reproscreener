# Architecture

## `tex_eval` module

The `tex_eval` module is used to evaluate `.tex` files exttracted from the arXiv source tarball of the paper.

::: reproscreener.tex_eval
    options:
      show_source: false
      heading_level: 3

## `repo_eval` module

::: reproscreener.repo_eval
    options:
      show_source: false
      heading_level: 3

## `scrape_arxiv` module

The `scrape_arxiv` module is used to obtain the gold standard dataset from the arXiv. It includes the PDFs, source tarballs, and abstract for each paper.

::: reproscreener.scrape_arxiv
    options:
      show_source: false
      heading_level: 3

## `gold_standard` module

The `gold_standard` module is used to evaluate and compare the performance of `reproscreener` on the gold standard dataset. It uses the data from the `scrape_arxiv` module.

::: reproscreener.gold_standard
    options:
      show_source: false
      heading_level: 3