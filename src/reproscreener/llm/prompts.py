import os
import openai
import pandas as pd
from pathlib import Path
from rich.table import Table
from rich.progress import Progress
from reproscreener.utils import log, console


class OpenAILLM:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.prompts = [
            "What is the problem the research seeks to solve?",
            "What is the objective of the research?",
            "What is the research method used?",
            "What are the research questions asked?",
            "Is there any method described using pseudo code?",
            "Is the datset made available or shared?",
            "What are the hypotheses that the authors make prior to conducting the experiment?",
            "What are the predicted results by the authors?",
            "Is the code for the research open source and shared?",
            "What are the software dependencies?",
            "Is the experimental setup described?",
        ]
        self.path = Path("case-studies/arxiv-corpus/gold_standard/abstracts")
        self.files = list(self.path.glob("*.txt"))

    def analyze_abstracts(
        self, max_papers: int = None, output_path: Path = Path("case-studies/arxiv-corpus/gold_standard/output")
    ) -> pd.DataFrame:
        data = {"paper": [], "metric": [], "matched_text": [], "value": []}

        files = self.files[:max_papers] if max_papers else self.files

        with Progress() as progress:
            abstract_task = progress.add_task("[cyan]Analyzing abstracts...", total=len(files))

            for file in files:
                log.info(f"Processing paper: {file.stem}")
                with open(file, "r") as f:
                    abstract = f.read().replace("\n", " ")
                result = self._analyze_abstract(abstract, progress)
                for metric, text in result.items():
                    data["paper"].append(file.stem)
                    data["metric"].append(metric)
                    data["matched_text"].append(text)
                    data["value"].append(1 if text else 0)
                progress.advance(abstract_task)

        df = pd.DataFrame(data)
        df.to_csv(output_path / "llm_results.csv", index=False)

        return df

    def _analyze_abstract(self, abstract: str, progress: Progress) -> dict:
        results = {}
        prompt_task = progress.add_task("[cyan]Processing prompts...", total=len(self.prompts))

        for prompt in self.prompts:
            log.info(f"Processing prompt: {prompt}")
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"This is an abstract from a research paper: '{abstract}'. {prompt}",
                temperature=0.5,
                max_tokens=150,
            )
            results[prompt] = response.choices[0].text.strip()
            progress.advance(prompt_task)

        progress.reset(prompt_task)
        return results


if __name__ == "__main__":
    openai_llm = OpenAILLM(os.getenv("OPENAI_API_KEY"))
    df = openai_llm.analyze_abstracts(max_papers=1)
    print(df)
