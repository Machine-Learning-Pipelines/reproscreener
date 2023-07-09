from pathlib import Path
import pandas as pd
import torch
from rich.console import Console
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer
from reproscreener.utils import console


class AbstractEvaluator:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def tokenize(self, text: str):
        return self.tokenizer.encode(text, return_tensors="pt")

    def embed_text(self, text: str):
        input_ids = self.tokenize(text)
        with torch.no_grad():
            return self.model(input_ids=input_ids).pooler_output

    def get_similarity(self, em, em2):
        return cosine_similarity(em.detach().numpy(), em2.detach().numpy())[0][0]

    def evaluate_abstract(self, abstract: str, metrics: dict, threshold: float = 0.5):
        results = {}
        for metric, description in metrics.items():
            max_score, _ = self.find_best_match(abstract, description)
            if max_score < threshold:
                max_score = 0
            results[metric] = max_score
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
):
    abstract_paths = list(abstract_folder.glob("*.txt"))

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
    console.print(df.to_markdown())


if __name__ == "__main__":
    metrics = {
        "Problem": "The problem the research seeks to solve",
        "Objective": "The objective of the research",
        "Research method": "The research method used",
        "Research questions": "The research question(s) asked",
        "Pseudocode": "Method described using pseudo code",
        "Dataset": "Is the dataset made available or shared",
        "Hypothesis": "Hypotheses that the authors make prior to conducting the experiment",
        "Prediction": "The predicted results by the authors",
        "Method source code": "Is the code for the research open source and shared?",
        "Software dependencies": "Software packages/dependencies used to run the code",
        "Experiment setup": "Is the experimental setup described?",
    }

    evaluator = AbstractEvaluator("allenai/specter2")

    abstract_folder_path = Path("case-studies/arxiv-corpus/gold_standard/abstracts/")
    output_folder = Path("outputs")
    output_folder.mkdir(parents=True, exist_ok=True)

    process_abstracts(evaluator, abstract_folder_path, output_folder, console, metrics)
