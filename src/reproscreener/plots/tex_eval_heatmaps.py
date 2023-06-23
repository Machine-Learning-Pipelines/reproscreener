import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from reproscreener import tex_eval
from reproscreener.utils import console, labels_mapping
from reproscreener.gold_standard import get_gold_standard_ids_from_manual

from typing import List


def prepare_tex_heatmap_df(evaluation_dict: dict, gold_standard_ids: List[str]) -> pd.DataFrame:
    heatmap_results = []

    for paper_id in gold_standard_ids:
        if paper_id in evaluation_dict:
            df = evaluation_dict[paper_id]
            found_vars = df["Found Variables"].str.split(", ").values[0]

            # Check if there are any matches in this paper
            if not found_vars or all(var.strip() == "" for var in found_vars):
                heatmap_results.append([paper_id, "No variables found"])
            else:
                for var in found_vars:
                    # Add the paper id and the found variable into heatmap_results
                    var = labels_mapping.get(var, var)
                    # var = var.replace("_", " ").title()
                    heatmap_results.append([paper_id, var])
        else:
            heatmap_results.append([paper_id, "No tex/source files provided"])  # For papers not in the evaluation_dict

    heatmap_df = pd.DataFrame(heatmap_results, columns=["Paper_ID", "Found_Variable"]).drop_duplicates()

    return heatmap_df


def plot_tex_heatmap(
    heatmap_df: pd.DataFrame,
    filename="heatmap_tex.png",
    dpi=1000,
    sort_x=False,
    sort_y=False,
    path_plots: Path = Path("plots"),
):
    binary_df = pd.crosstab(heatmap_df["Paper_ID"], heatmap_df["Found_Variable"]).replace({1: True, 0: False})

    if sort_y:
        # sort by column frequency
        column_order = binary_df.sum().sort_values(ascending=False).index
        binary_df = binary_df[column_order]
        filename = filename.replace(".png", "_sorted_y.png")

    if sort_x:
        # sort by row frequency
        row_order = binary_df.T.sum().sort_values(ascending=False).index
        binary_df = binary_df.loc[row_order]
        filename = filename.replace(".png", "_sorted_x.png")

    binary_df = binary_df.applymap(float).T

    # (empty, filled)
    custom_cmap = ListedColormap(["#FFF0F0", "#E74C3C"])

    fig, ax = plt.subplots(figsize=(12, 4), tight_layout={"pad": 1.5})
    # sns.set_style("whitegrid")
    ax.axhline(y=0, color="k", linewidth=1)
    ax.axvline(x=0, color="k", linewidth=1)
    ax.axhline(y=binary_df.shape[0], color="k", linewidth=1)
    ax.axvline(x=binary_df.shape[1], color="k", linewidth=1)
    sns.heatmap(binary_df, cmap=custom_cmap, cbar=False, linewidths=1, ax=ax)
    plt.subplots_adjust(top=0.95, left=0.15, right=0.95)
    ax.set(xlabel=None, ylabel=None)

    if path_plots is None:
        plt.show()

    else:
        plt.savefig(path_plots / filename, dpi=dpi, bbox_inches="tight")
        console.print(f"Heatmap saved to {path_plots / filename}")
        plt.close()


if __name__ == "__main__":
    path_corpus = Path("case-studies/arxiv-corpus/gold_standard/source")
    path_manual = Path("case-studies/arxiv-corpus/manual_eval.csv")

    gold_standard_ids = get_gold_standard_ids_from_manual(manual_path=path_manual)
    evaluation_dict = tex_eval.get_all_tex_eval_dict(path_corpus)
    console.print(f"Number of papers in the tex evaluation dict: {len(evaluation_dict)}")
    # console.print(evaluation_dict)

    heatmap_df = prepare_tex_heatmap_df(evaluation_dict, gold_standard_ids)
    heatmap_df.to_csv(Path("plots/") / "tex_heatmap_df.csv", index=False)
    heatmap_df.to_csv(Path("case-studies/arxiv-corpus/gold_standard/output") / "tex_heatmap_df.csv", index=False)

    plot_tex_heatmap(heatmap_df, filename="heatmap_tex.png", dpi=1000, path_plots=Path("plots"))
    plot_tex_heatmap(heatmap_df, filename="heatmap_tex.png", dpi=1000, sort_x=True, path_plots=Path("plots"))
    plot_tex_heatmap(heatmap_df, filename="heatmap_tex.png", dpi=1000, sort_y=True, path_plots=Path("plots"))
    plot_tex_heatmap(
        heatmap_df, filename="heatmap_tex.png", dpi=1000, sort_x=True, sort_y=True, path_plots=Path("plots")
    )
