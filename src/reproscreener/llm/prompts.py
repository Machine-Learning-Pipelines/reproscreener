import os
import openai
import pandas as pd
import tiktoken
from pathlib import Path
from rich.progress import Progress
from reproscreener.utils import log, console


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


class OpenAILLM:
    def __init__(self, api_key: str):
        openai.api_key = api_key

        prompt_path = Path(__file__).parent.resolve() / "prompt.txt"
        with open(prompt_path, "r") as f:
            first_half_prompt = f.read()
        self.prompt = first_half_prompt + "Here is the abstract to check:\n'{}'"

        self.path = Path("case-studies/arxiv-corpus/gold_standard/abstracts")
        self.files = list(self.path.glob("*.txt"))

    def analyze_abstracts(
        self, max_papers: int = None, output_path: Path = Path("case-studies/arxiv-corpus/gold_standard/output")
    ) -> pd.DataFrame:
        data = {
            "paper": [],
            "response_text": [],
        }
        files = self.files[:max_papers] if max_papers else self.files

        with Progress() as progress:
            abstract_task = progress.add_task("[cyan]Analyzing abstracts...", total=len(files))

            for file in files:
                log.info(f"Processing paper: {file.stem}")
                with open(file, "r") as f:
                    abstract = f.read().replace("\n", " ")
                result = self._analyze_abstract(abstract)
                data["paper"].append(file.stem)
                data["response_text"].append(result["response_text"])

                progress.advance(abstract_task)

        df = pd.DataFrame(data)
        df.to_csv(output_path / "llm_results.csv", index=False)

        return df

    def _analyze_abstract(self, abstract: str) -> dict:
        log.info(f"Processing prompt")
        prompt_tokens = num_tokens_from_string(self.prompt.format(abstract), "p50k_base")
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=self.prompt.format(abstract),
            temperature=0.5,
            max_tokens=4096 - len(self.prompt.format(abstract).split()) - 350,
        )
        console.print(response, style="bold cyan")
        console.print(f"Tokens in prompt: {prompt_tokens}", style="bold red")
        text = response.choices[0].text.strip()
        return {"response_text": text}


if __name__ == "__main__":
    openai_llm = OpenAILLM(os.getenv("OPENAI_API_KEY"))
    df = openai_llm.analyze_abstracts(max_papers=2)
    for index, row in df.iterrows():
        console.print(f"Paper: {row['paper']}\nResponse Text:\n{row['response_text']}\n")
