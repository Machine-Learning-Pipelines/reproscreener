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
    def __init__(self, api_key: str, engine: str = "gpt-4"):
        openai.api_key = api_key
        self.engine = engine

        prompt_path = Path(__file__).parent.resolve() / "prompt.txt"
        with open(prompt_path, "r") as f:
            first_half_prompt = f.read()
        self.prompt = first_half_prompt + "Here is the abstract to check:\n'{}'"

        self.path = Path("case-studies/arxiv-corpus/gold_standard/abstracts")
        self.files = list(self.path.glob("*.txt"))

    def read_abstract(self, file):
        with open(file, "r") as f:
            abstract = f.read().replace("\n", " ")
        return abstract

    def analyze_abstracts(
        self,
        max_papers: int = None,
        output_path: Path = Path("case-studies/arxiv-corpus/gold_standard/output/llm_output"),
    ) -> pd.DataFrame:
        output_path.mkdir(parents=True, exist_ok=True)
        files = self.files[:max_papers] if max_papers else self.files

        with Progress() as progress:
            abstract_task = progress.add_task("[cyan]Analyzing abstracts...", total=len(files))

            for file in files:
                log.info(f"Processing paper: {file.stem}")
                abstract = self.read_abstract(file)
                result = self._analyze_abstract(abstract, file.stem)  # passing file.stem as an argument
                df = pd.DataFrame(result, index=[0])  # convert the result to a dataframe
                df.to_csv(output_path / f"{file.stem}_llm_results.csv", index=False)  # save the dataframe to a csv file

                progress.advance(abstract_task)

    def _analyze_abstract(self, abstract: str, file_stem: str) -> dict:  # added new argument file_stem
        log.info(f"Processing prompt")
        prompt = self.prompt.format(abstract)
        prompt_tokens = num_tokens_from_string(prompt, "p50k_base")

        # New chat-based request
        response = openai.ChatCompletion.create(
            model=self.engine,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=5192 - prompt_tokens - 350,
        )
        console.print(response, style="bold cyan")
        console.print(f"Tokens in prompt: {prompt_tokens}", style="bold red")
        text = response.choices[0].message["content"].strip()
        return {"paper": file_stem, "response_text": text}  # use file_stem instead of file.stem

    def combine_results(
        self, output_path: Path = Path("case-studies/arxiv-corpus/gold_standard/output/llm_output")
    ) -> pd.DataFrame:
        dfs = []
        for file in output_path.glob("*.csv"):
            dfs.append(pd.read_csv(file))

        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df

    def get_summary_statistics(self, df: pd.DataFrame):
        return df.describe(include="all")


if __name__ == "__main__":
    openai_llm = OpenAILLM(os.getenv("OPENAI_API_KEY"))
    openai_llm.analyze_abstracts(max_papers=5)

    combined_df = openai_llm.combine_results()
    print(combined_df)
    summary = openai_llm.get_summary_statistics(combined_df)
    print(summary)
