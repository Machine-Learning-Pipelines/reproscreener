# ReproScreener

ReproScreener aims to address challenges in robustness, transparency and interpretability of ML models by automating verification of machine learning models at scale.

## Project structure

- `run.sh` is the script used to run ReproScreener
- `case-studies` contains the papers that ReproScreener is developed and tested on
- `guidance` contains the set of metrics that ReproScreener will check for 
- `tests` contains scripts and notebooks used during development
- `src` contains the main python scripts

## Features

- [x] *In Progress:* Automatically check specific guidances to improve correctness of ML models
- [] Predict, capture and identify differences in model output at scale (due to architecture, non-determinism, etc.)
- [] Enable comparison of model code through
    - Checks for modularity, file structure, dependencies
    - Checks for steps/scripts to create figures & visualizations
    - Track model benchmarks and provenance

## Case studies

The initial development dataset `mine50` contains the 50 most recent articles from [arxiv.org in the cs.LG subcategory](https://arxiv.org/list/cs.LG/recent), between the dates 2022-10-24 and 2022-10-25.

## Requirements

## References

`references.bib` contains references used in this project.

## Installation instructions

## Run instructions