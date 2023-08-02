from pathlib import Path
from typing import List

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from reproscreener import repo_eval, tex_eval
from reproscreener.gold_standard import (
    get_gold_standard_ids_from_manual,
    repo_map_dict,
    tex_map_dict,
    split_parsed_readme,
)
from reproscreener.utils import console, labels_mapping, reverse_mapping


background_colors = [
    "#F0F8FF",
    "#FAEBD7",
    "#7FFFD4",
    "#F5F5DC",
    "#FFE4C4",
    "#FF7F50",
    "#FFD700",
    "#7CFC00",
    "#ADFF2F",
]

#                                (empty, filled)
custom_cmap = ListedColormap(["#F3E9E3", "#E74C3C"])

display_name_mapping = {
    "readme_dependencies": 'Readme has a "dependencies" section',
    "readme_install": 'Readme has an "install" section',
    "readme_requirements": 'Readme has a "requirements" section',
    "readme_setup": 'Readme has a "setup" section',
}


def plot_repo_heatmap(
    heatmap_df: pd.DataFrame,
    filename="heatmap_repo.png",
    dpi=1000,
    path_plots: Path = Path("plots"),
    sort_x=False,
    sort_y=False,
):
    binary_df = heatmap_df.set_index("Paper_ID").apply(lambda x: x.notnull()).astype(int)
    binary_df = binary_df.replace({1: True, 0: False}).applymap(float).T

    if sort_y:
        # Sort by column frequency
        column_order = binary_df.sum().sort_values(ascending=False).index
        binary_df = binary_df[column_order]
        filename = filename.replace(".png", "_sorted_y.png")

    if sort_x:
        # Sort by row frequency
        row_order = binary_df.T.sum().sort_values(ascending=False).index
        binary_df = binary_df.loc[row_order]
        filename = filename.replace(".png", "_sorted_x.png")

    # Update y-axis labels with display names
    y_labels = binary_df.index
    y_labels = [display_name_mapping.get(label, label) for label in y_labels]

    fig, ax = plt.subplots(figsize=(12, 4), tight_layout={"pad": 1.5})
    sns.set_style("whitegrid")
    ax.axhline(y=0, color="k", linewidth=1)
    ax.axvline(x=0, color="k", linewidth=1)
    ax.axhline(y=binary_df.shape[0], color="k", linewidth=1)
    ax.axvline(x=binary_df.shape[1], color="k", linewidth=1)
    sns.heatmap(binary_df, cmap=custom_cmap, cbar=False, linewidths=1, ax=ax)
    ax.set_yticklabels(y_labels)  # Set y-axis labels
    plt.subplots_adjust(top=0.95, left=0.15, right=0.95)
    ax.set(xlabel=None, ylabel=None)

    if path_plots is None:
        plt.show()

    else:
        plt.savefig(path_plots / filename, dpi=dpi, bbox_inches="tight")
        console.print(f"Heatmap saved to {path_plots / filename}")
        plt.close()


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


def evaluate_and_save_plots(
    path_manual: Path = Path("case-studies/arxiv-corpus/manual_eval.csv"),
    path_output: Path = Path("case-studies/arxiv-corpus/gold_standard/output"),
    path_plots: Path = Path("plots"),
):
    path_output.mkdir(parents=True, exist_ok=True)
    path_plots.mkdir(parents=True, exist_ok=True)

    manual_eval = pd.read_csv(path_manual)
    manual_eval = split_parsed_readme(manual_eval, "parsed_readme")
    manual_eval.rename(columns=repo_map_dict, inplace=True)
    manual_eval.rename(columns=tex_map_dict, inplace=True)
    manual_eval.rename(columns={"paper": "Paper_ID"}, inplace=True)

    console.print(manual_eval.head())

    heatmap_df_repo = manual_eval[list(repo_map_dict.values()) + ["Paper_ID"]]
    heatmap_df_tex = manual_eval[list(tex_map_dict.values()) + ["Paper_ID"]]

    # save the transformed copy to a csv
    heatmap_df_repo.to_csv(path_output / "manual_repo_heatmap_df.csv", index=False)
    heatmap_df_tex.to_csv(path_output / "manual_tex_heatmap_df.csv", index=False)

    # plotting with original df
    plot_repo_heatmap(heatmap_df_repo, filename="heatmap_manual_repo.png", path_plots=path_plots)
    plot_repo_heatmap(
        heatmap_df_repo, filename="heatmap_manual_repo_sorted.png", sort_x=True, sort_y=False, path_plots=path_plots
    )
    plot_repo_heatmap(
        heatmap_df_repo, filename="heatmap_manual_repo_sorted.png", sort_x=False, sort_y=True, path_plots=path_plots
    )
    plot_repo_heatmap(
        heatmap_df_repo, filename="heatmap_manual_repo_sorted.png", sort_x=True, sort_y=True, path_plots=path_plots
    )

    plot_tex_heatmap(heatmap_df_tex, filename="heatmap_manual_tex.png", path_plots=path_plots)
    plot_tex_heatmap(heatmap_df_tex, filename="heatmap_manual_tex.png", sort_x=True, path_plots=path_plots)
    plot_tex_heatmap(heatmap_df_tex, filename="heatmap_manual_tex.png", sort_y=True, path_plots=path_plots)
    plot_tex_heatmap(heatmap_df_tex, filename="heatmap_manual_tex.png", sort_x=True, sort_y=True, path_plots=path_plots)


if __name__ == "__main__":
    evaluate_and_save_plots()
