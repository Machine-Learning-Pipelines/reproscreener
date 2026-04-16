# ReproScreener
## Review of packages
### Parsing
- 1.5k: [PyMuPDF](https://github.com/pymupdf/PyMuPDF)
- 4.1k: 2018, [PyPDF2](https://github.com/mstamy2/PyPDF2)
- 3.5k: [PDFMiner.six](https://github.com/pdfminer/pdfminer.six)
	- 3.3k: [Parsr](https://github.com/axa-group/Parsr)
	- 2.6k: [pdfplumber](https://github.com/jsvine/pdfplumber)
- 1.7k: [Grobid](https://github.com/kermitt2/grobid)
- [PDFBoT](https://github.com/yuchangfeng/PDFBoT)
- https://johannesfilter.com/python-and-pdf-a-review-of-existing-tools/
- https://medium.com/social-impact-analytics/comparing-4-methods-for-pdf-text-extraction-in-python-fd34531034f
### TeX
- 1.9k: [PyLaTeX](https://github.com/JelteF/PyLaTeX)
- Pandoc?
- 183: [TeXSoup](https://github.com/alvinwan/texsoup)
- 137: [pylatexenc](https://github.com/phfaist/pylatexenc/)
	- https://pylatexenc.readthedocs.io/en/latest/latexwalker/
### End-to-end
- https://github.com/allenai/science-parse
- Uses Grobid and Spacy: https://github.com/titipata/scipdf_parser

### Search tools
- [Flashtext](https://github.com/vi3k6i5/flashtext)
- 
## Features
- Ability to select which variables/factors to check against
- Ability to add different formats (latex, docx, text)
## Requirements
## Constraints
## Factors and variables [[@gundersen_state_2018]]
- Method (5)
	- Problem*: The problem the research seeks to solve
	- Objective/Goal*: The objective of the research
	- Research Method*: The research method used
	- Research questions*: The research question asked
	- Pseudo code: Method described using pseudo code
- Data (4)
	- Training data: Is the training set shared?
	- Validation data: Is the validation set shared?
	- Test data: Is the test set shared?
	- Results: Are the results shared?
- Experiment (7)
	- Hypothesis*: The hypothesis being investigated
	- Prediction*: Predictions related to the hypotheses
	- Method source code: Is the method open sourced
	- Hardware specifications: Hardware used
	- Software dependencies: For method or experiment
	- Experiment setup: Is the setup including hyper-parameters described?
	- Experiment source code: Is the experiment code open sourced?
- Miscellaneous (4)
	- Research type: Experimental (E) or theoretical (T)
	- Research outcome: Is the paper reporting a positive or a negative result (positive=1 and negative=0)
	- Affiliation: The affiliation of the authors 
		- Academia (0), collaboration (1) or industry (2)
		- Contribution*: Contribution of the research

| Name           | Detail                                  | Keyword(s)        |               |
| -------------- | --------------------------------------- | ----------------- | ------------- |
| Problem        | The problem the research seeks to solve | Problem Statement |               |
| Objective/Goal | The objective of the research           | Objective         | Research Goal |
|                |                                         |                   |               |
## Factors and variables [[@raghupathiReproducibilityComputingResearch2022]]
- Method (14)
	- Problem statement: Is there an explicit mention of the problem the research seeks to address?
	- Goal: Is the research goal explicitly mentioned?
	- Research question: Is there an explicit mention of the research question(s) addressed?
	- Research method: Is there an explicit mention of the research method used?
	- Algorithm: Is there an explicit mention of the algorithm(s) the research used?
	- Hypothesis: Is there an explicit mention of the hypotheses being investigated?
	- Prediction: Is there an explicit mention of prediction related to the hypotheses?
	- Experiment setup: Are the variable settings shared, such as hyper-parameters?
	- Contributions: Does the paper state the contributions or implications of the research?
	- Related study: Does the paper explicitly mention related literature?
	- Scope and limitations: Is there an explicit mention of scope and limitation of the research?
	- Machine learning: Is there an explicit mention of using machine learning for analysis?
	- Statistical analysis: Does the paper conduct any statistical analysis?
	- Conclusion: Is there an explicit outcome concluded in the paper?
- Data (9)
	- Model results: Is the output of the model constructed shared?
	- Training data: Is the training set shared?
	- Validation data: Is the validation set shared?
	- Test data: Is the test set shared?
	- Evaluation criteria: Is the evaluation metrics (e.g. Accuracy, R-squared, etc.) of the model shared?
	- Data preprocessing: Is the method of data preprocessing of the analysis shared, including data merging or feature engineering?
	- Publicly available data: Is the data available to the public?
	- Time series data: Does the paper use time series data for analysis (e.g. across multiple years or month)?
	- Data source: Does the paper explicitly state the data source?
- Experiment (2)
	- Method source code: Is the system code available as open source?
	- Software used: Is the software used in the research explicitly mentioned (Python, R, etc.)

## Todo
1. Get text from PDF
2. For each of 16 variables: check if present
3. Combine variables to factors
4. Print stats
## Issues

## ➕2023-05-11

- 

## Test
![[21-10-22 - HPC CARC#RSTA Metrics]]

`read_tex.py`

`keywords.py`

`evaluate_guidance.py`

`repo_checker.py`

`repo_downloader.py`

`scrape_arxiv.py`

### Commands

- `reproscreener gold-standard`: 
	- Query arXix
	- Download 50 from arXiv
	- Parse/combine tex
	- Evaluate & score

### End user objectives
- Inputs:
	- `source` folder for the paper containing relevant .`tex` files
	- arXiv link
	- Repo link
- Paper evaluation
	- Either read or 
- Code evaluation

## Qualifying exam

[[phd/phd-pages/reproscreener-mindmap]]

## components
- [[dev/software-development]]
- [[phd/journal-screeners]]
- [[phd/data-repositories]]
- [[phd/code-repositories]]
- [[phd/RAG]]
- [[phd/data extraction]]
- data connectors
	- https://github.com/run-llama/llama_inde

## Reproscreener's features
- Extensible metric sets
- Aimed at scientific community, not have software engineering experience

## What reproscreener is
- An extensible framework to assess computational reproducibility metrics in ML-based science
- An extensible framework for evaluating computational reproducibility metrics in ML-based science
- A journal screening framework for scientific research (specify) with code and data (JRNL.SCRNR)
- What it measures
	- What are the minimum necessary artifacts in a repository, manuscript, and other submitted metadata
- Computational eproducibility measurement tool
	- Plot and table differ (requires to be at results stage)
	- 
## What reproscreener is not
- dataset platform/storage
- model/artifact/provenance tracking
- workflow/pipeline management

## Why reproscreener
- Might be difficult to anonymize repositories (licenses, author names) as required by ICML [[@ICML2025Author|ICML2025Author]]

## statistical measures
- We have used **Spearman**’s rank correlation coefficient which is a non-parametric method of calculating correlation. 
## metrics

- [[@heyardScopingReviewMetrics2025]]
- [[@kapoorREFORMSConsensusbasedRecommendations2024|kapoorREFORMSConsensusbasedRecommendations2024]]
### manuscript


### code
- #phd/metrics/code/maintainability We do not consider software engineering perspectives [[@arditoToolBasedPerspectiveSoftware2020]]. Domains:
	- Documentation [[@mamunCorrelationsSoftwareCode2017]]
		- `comment_lines_density`
	- Size
		- `files`
		- `directories`
	- Complexity
		- `complexity_in_classes`
		- `file_complexity`
	- Duplications
		- `duplicated_files`
- #phd/metrics/code/executability
	- torchmetrics [[@detlefsenTorchMetricsMeasuringReproducibility2022|detlefsenTorchMetricsMeasuringReproducibility2022]]
### data

## tools
- singularity [[@sochatEnhancingReproducibilityScientific2017|sochatEnhancingReproducibilityScientific2017]]
# prompts

[[prompts/best datastructure]]
- What are current metrics that can empirically measure the reproducibility of code, data or manuscripts in scientific research?

