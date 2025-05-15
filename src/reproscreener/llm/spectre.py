from pathlib import Path

import pandas as pd
import torch
from utils import console
from rich.console import Console
from rich.table import Table
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer
from scipy.spatial.distance import cosine, euclidean, cityblock


class AbstractEvaluator:
    def __init__(self, model_name: str, device="cpu", similarity_measure="cosine"):
        self.device = torch.device(device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.similarity_measure = similarity_measure

    def tokenize(self, text: str):
        return self.tokenizer.encode(text, return_tensors="pt").to(self.device)

    def embed_text(self, text: str):
        input_ids = self.tokenize(text)
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids)
            return outputs.last_hidden_state.mean(dim=1).cpu()

    def get_similarity(self, em, em2):
        em = em.detach().numpy().reshape(-1)
        em2 = em2.detach().numpy().reshape(-1)
        if self.similarity_measure == "cosine":
            return 1 - cosine(em, em2)
        elif self.similarity_measure == "euclidean":
            return -euclidean(em, em2)
        elif self.similarity_measure == "manhattan":
            return -cityblock(em, em2)
        else:
            raise ValueError(f"Unknown similarity measure: {self.similarity_measure}")

    def evaluate_abstract(self, abstract: str, metrics: dict, thresholds: dict):
        console.print(abstract)
        results = {}
        metrics_embeddings = {metric: self.embed_text(description) for metric, description in metrics.items()}

        for sentence in abstract.split("."):
            sentence_embedding = self.embed_text(sentence)
            for metric, description_embedding in metrics_embeddings.items():
                score = self.get_similarity(sentence_embedding, description_embedding)
                threshold = thresholds.get(
                    metric, 0.5
                )  # Use a default threshold of 0.5 if none is provided for this metric
                if score > threshold and (metric not in results or score > results[metric]):
                    results[metric] = score
        return results

    def find_best_match(self, abstract: str, description: str):
        max_score = 0
        for sentence in abstract.split("."):
            score = self.get_similarity(self.embed_text(sentence), self.embed_text(description))
            if score > max_score:
                max_score = score
        return max_score, ""


def process_abstracts(
    evaluator: AbstractEvaluator,
    abstract_folder: Path,
    output_folder: Path,
    console: Console,
    metrics: dict,
    limit: int = None,
):
    abstract_paths = list(abstract_folder.glob("*.txt"))

    # Limit the number of papers if limit is set
    if limit is not None:
        abstract_paths = abstract_paths[:limit]

    all_results = []

    for abstract_path in tqdm(abstract_paths, desc="Processing abstracts", dynamic_ncols=True):
        with open(abstract_path, "r") as file:
            abstract = file.read()

        results = evaluator.evaluate_abstract(abstract, metrics)
        results["Abstract file"] = abstract_path.stem
        all_results.append(results)

        results_path = output_folder / f"{abstract_path.stem}.csv"
        pd.DataFrame([results]).to_csv(results_path, index=False)

    df = pd.DataFrame(all_results)
    df.set_index("Abstract file", inplace=True)

    # Create a new table
    table = Table(show_header=True, header_style="bold magenta")

    # Add a column for paper id's
    table.add_column("Paper ID")

    # Add columns for each metric
    for column in df.columns:
        table.add_column(column)

    # Add rows
    for index, row in df.iterrows():
        table.add_row(index, *[f"{value:.3f}" for value in row.values])

    console.print(table)


def test_abstract(evaluator: AbstractEvaluator, abstract: str, metrics: dict, thresholds: dict):
    results = evaluator.evaluate_abstract(abstract, metrics, thresholds)
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric")
    table.add_column("Score")
    for metric, score in results.items():
        table.add_row(metric, f"{score:.3f}")
    console.print(table)


if __name__ == "__main__":
    # metrics = {
    #     "Problem": "The problem the research seeks to solve",
    #     "Objective": "The objective of the research",
    #     "Research method": "The research method used",
    #     "Research questions": "The research question(s) asked",
    #     "Pseudocode": "Method described using pseudo code",
    #     "Dataset": "Is the dataset made available or shared",
    #     "Hypothesis": "Hypotheses that the authors make prior to conducting the experiment",
    #     "Prediction": "The predicted results by the authors",
    #     "Method source code": "Is the code for the research open source and shared?",
    #     "Software dependencies": "Software packages/dependencies used to run the code",
    #     "Experiment setup": "Is the experimental setup described?",
    # }

    metrics = {
        "Problem": "research problem, problem, problem statement",
        "Objective": "goal of the paper, objective of the paper, aim of the paper",
        "Research method": "research method used, systematic review, statistical significance",
        "Research questions": "research question, RQ",
        "Pseudocode": "pseudocode, Algorithm",
        "Dataset": "training set, test set, validation set, dataset shared",
        "Hypothesis": "hypothesis, authors' hypothesis",
        "Prediction": "prediction, authors' prediction",
        "Method source code": "open source code, code shared, GitHub, GitLab",
        "Software dependencies": "software packages, software dependencies",
        "Experiment setup": "experimental setup, hyperparameters, initial values, selected models",
    }

    cosine_thresholds = {
        "Problem": 0.75,
        "Objective": 0.75,
        "Research method": 0.75,
        "Research questions": 0.75,
        "Pseudocode": 0.75,
        "Dataset": 0.75,
        "Hypothesis": 0.75,
        "Prediction": 0.75,
        "Method source code": 0.75,
        "Software dependencies": 0.75,
        "Experiment setup": 0.75,
    }

    euclidean_thresholds = {
        "Problem": -0.7,
        "Objective": -0.7,
        "Research method": -0.7,
        "Research questions": -0.7,
        "Pseudocode": -0.7,
        "Dataset": -0.7,
        "Hypothesis": -0.7,
        "Prediction": -0.7,
        "Method source code": -0.7,
        "Software dependencies": -0.7,
        "Experiment setup": -0.7,
    }

    manhattan_thresholds = {
        "Problem": -0.7,
        "Objective": -0.7,
        "Research method": -0.7,
        "Research questions": -0.7,
        "Pseudocode": -0.7,
        "Dataset": -0.7,
        "Hypothesis": -0.7,
        "Prediction": -0.7,
        "Method source code": -0.7,
        "Software dependencies": -0.7,
        "Experiment setup": -0.7,
    }

    device = "cuda" if torch.cuda.is_available() else "cpu"
    console.print(f"Using device: {device}\n")
    # evaluator = AbstractEvaluator("allenai/specter2", device=device)
    evaluator1 = AbstractEvaluator("allenai/specter2", device=device, similarity_measure="cosine")
    evaluator2 = AbstractEvaluator("allenai/specter2", device=device, similarity_measure="euclidean")
    evaluator3 = AbstractEvaluator("allenai/specter2", device=device, similarity_measure="manhattan")

    abstract_folder_path = Path("case-studies/arxiv-corpus/gold_standard/abstracts/")
    output_folder = Path("outputs")
    output_folder.mkdir(parents=True, exist_ok=True)

    # process_abstracts(evaluator, abstract_folder_path, output_folder, console, metrics)
    abstract = "Deep Learning (DL) methods have emerged as one of the most powerful tools for functional approximation and prediction. While the representation properties of DL have been well studied, uncertainty quantification remains challenging and largely unexplored. Data augmentation techniques are a natural approach to provide uncertainty quantification and to incorporate stochastic Monte Carlo search into stochastic gradient descent (SGD) methods. The purpose of our paper is to show that training DL architectures with data augmentation leads to efficiency gains. We use the theory of scale mixtures of normals to derive data augmentation strategies for deep learning. This allows variants of the expectation-maximization and MCMC algorithms to be brought to bear on these high dimensional nonline"
    abstract = "hello my name is adhithya. problem."

    test_abstract(evaluator1, abstract, metrics, cosine_thresholds)
    test_abstract(evaluator2, abstract, metrics, euclidean_thresholds)
    test_abstract(evaluator3, abstract, metrics, manhattan_thresholds)
