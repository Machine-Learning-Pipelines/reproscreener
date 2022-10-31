# ReproScreener

ReproScreener aims to address challenges in robustness, transparency and interpretability of ML models by automating verification of machine learning models at scale.

## Project structure

- `case-studies` contain the papers that ReproScreener is tested on
- `guidance` contain the set of metrics that ReproScreener will check for 

## Features

- Automatically check specific guidances to improve correctness of ML models
- Predict, capture and identify differences in model output at scale (due to architecture, non-determinism, etc.)
- Enable comparison of model code through
    - Checks for modularity, file structure, dependencies
    - Checks for steps/scripts to create figures & visualizations
    - Track model benchmarks and provenance

## Case studies

## Requirements

conda install lxml
pip install flashtext
pip install exrex

## References

`references.bib` contains references used in this project.

## Installation instructions

grobid_client --input /Users/adb/stuff/repro-screener/case-studies/arxiv-corpus/mine50/pdf/ --output /Users/adb/stuff/repro-screener/case-studies/arxiv-corpus/mine50/parsed_xml/ processFulltextDocument

## Run instructions