# Todo

## Features

- [x] *In Progress:* Automatically check specific guidances to improve correctness of ML models
- [] Predict, capture and identify differences in model output at scale (due to architecture, non-determinism, etc.)
- [] Enable comparison of model code through
  - Checks for modularity, file structure, dependencies
  - Checks for steps/scripts to create figures & visualizations
  - Track model benchmarks and provenance
- [] Progress bar (scrape): (<https://rich.readthedocs.io/en/latest/progress.html>)

## Development notes

- Non binary values in JSON guidance format would require custom keyword seach functions
- Include a way to add keywords to JSON and have it assigned to keywordparser
- Refactor so keywords functions are independent of guidance type
- MKDocs over Sphinx?
- Using shutil.copyfileobj to merge all tex files in an article's source folder into 1 file and *then* running keyword search on it. Would likely be more efficient than search over each file and combining the scores.
