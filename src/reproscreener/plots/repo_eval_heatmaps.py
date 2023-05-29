import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patheffects as path_effects
from matplotlib.patches import Patch

from reproscreener import repo_eval
from reproscreener.utils import reverse_mapping, console
from reproscreener.gold_standard import get_gold_standard_ids_from_manual

from typing import List

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


def prepare_repo_heatmap_df(evaluation_dict: dict, gold_standard_ids: List[str]) -> pd.DataFrame:
    heatmap_results = []

    for paper_id in gold_standard_ids:
        if paper_id in evaluation_dict:
            df = evaluation_dict[paper_id]
            matched_files = df[df["Found?"]].Variable + df[df["Found?"]].Found_Extension

            if matched_files.empty:  # Check if there are any matches in this paper
                heatmap_results.append([paper_id, "Code provided but no matches", None])
            else:
                for file in matched_files:
                    # Add the paper id and the matched file name into heatmap_results
                    category = reverse_mapping.get(file, None)
                    heatmap_results.append([paper_id, file, category])
        else:
            heatmap_results.append([paper_id, "No code provided", None])  # For papers not in the evaluation_dict

    heatmap_df = pd.DataFrame(heatmap_results, columns=["Paper_ID", "Matched_File", "Category"]).drop_duplicates()

    return heatmap_df


def plot_repo_heatmap(
    heatmap_df: pd.DataFrame,
    filename="heatmap_repo.png",
    dpi=1000,
    path_plots: Path = Path("plots"),
    sort_x=False,
    sort_y=False,
):
    binary_df = pd.crosstab(heatmap_df["Paper_ID"], heatmap_df["Matched_File"]).replace({1: True, 0: False})
    binary_df = binary_df.applymap(float).T

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
    plt.savefig(path_plots / filename, dpi=dpi, bbox_inches="tight")
    console.print(f"Heatmap saved to {path_plots / filename}")
    plt.close()


def plot_repo_clustermap(
    heatmap_df: pd.DataFrame, filename="clustermap_repo.png", dpi=1000, path_plots: Path = Path("plots")
):
    sns.set_style("whitegrid")

    # When you apply the label mappings to your dataframe, use this instead:
    heatmap_df["Display_Label"] = heatmap_df["Matched_File"].map(display_name_mapping)
    heatmap_df["Category"] = heatmap_df["Matched_File"].map(reverse_mapping)
    # Ensure data is sorted by Category first, then Matched_File
    heatmap_df = heatmap_df.sort_values(by=["Category", "Matched_File"])
    binary_df = pd.crosstab(heatmap_df["Paper_ID"], heatmap_df["Matched_File"]).replace({1: True, 0: False})
    binary_df = binary_df.applymap(float).T

    # Create a categorical palette to identify the categories
    categories = heatmap_df["Category"].unique()
    category_pal = sns.husl_palette(len(categories), s=0.45)
    category_lut = dict(zip(categories, category_pal))

    console.print(heatmap_df)
    console.print(category_lut)

    # Convert the palette to vectors that will be drawn on the side of the matrix
    categories = binary_df.index.map(reverse_mapping)
    category_colors = pd.Series(categories, index=binary_df.index).map(category_lut)
    category_colors_df = pd.DataFrame(category_colors)
    category_colors_df.columns = ["Categories"]

    # Draw the full plot
    g = sns.clustermap(
        binary_df,
        cmap=custom_cmap,
        row_colors=category_colors_df,
        col_cluster=False,
        linewidths=1,
        cbar_pos=None,
        dendrogram_ratio=(0.05, 0.05),
        figsize=(12, 4),
    )

    # black borders around the heatmap
    heatmap = g.ax_heatmap
    heatmap.plot(
        [0, 0, binary_df.shape[1], binary_df.shape[1], 0], [0, binary_df.shape[0], binary_df.shape[0], 0, 0], color="k"
    )

    # Remove the y-axis dendrogram
    g.ax_row_dendrogram.remove()

    # Color y-axis labels and add outline
    for label in g.ax_heatmap.get_yticklabels():
        label_text = label.get_text()
        category = reverse_mapping.get(label_text, None)
        if category:
            label.set_color(category_lut[category])
            label.set_text(display_name_mapping.get(label_text, label_text))
            label.set_path_effects([path_effects.Stroke(linewidth=0.2, foreground="grey"), path_effects.Normal()])

    # Add category names to the legend with corresponding colors
    legend_patches = [Patch(color=color, label=category) for category, color in category_lut.items()]

    # Configure legend
    ax_legend = plt.gca()
    ax_legend.legend(handles=legend_patches, loc="lower right", bbox_to_anchor=(1.4, -0.4), fontsize=8)

    # Remove x and y axis labels
    g.ax_heatmap.set_xlabel("")
    g.ax_heatmap.set_ylabel("")

    plt.tight_layout()
    plt.savefig(path_plots / filename, dpi=dpi, bbox_inches="tight")
    console.print(f"Heatmap saved to {path_plots / filename}")
    plt.close()


if __name__ == "__main__":
    path_corpus = Path("case-studies/arxiv-corpus/mine50-andor/repo")
    path_manual = Path("case-studies/arxiv-corpus/manual_eval.csv")

    gold_standard_ids = get_gold_standard_ids_from_manual(path_manual)
    evaluation_dict = repo_eval.get_all_repo_eval_dict(path_corpus)
    heatmap_df = prepare_repo_heatmap_df(evaluation_dict, gold_standard_ids)
    # save the heatmap_df to a csv
    heatmap_df.to_csv(Path("plots/") / "repo_heatmap_df.csv", index=False)

    plot_repo_heatmap(heatmap_df, filename="heatmap_repo_eval.png")
    plot_repo_heatmap(heatmap_df, filename="heatmap_repo_eval_sorted.png", sort_x=True, sort_y=False)
    plot_repo_heatmap(heatmap_df, filename="heatmap_repo_eval_sorted.png", sort_x=False, sort_y=True)
    plot_repo_heatmap(heatmap_df, filename="heatmap_repo_eval_sorted.png", sort_x=True, sort_y=True)
    # plot_repo_clustermap(heatmap_df, filename="heatmap_repo_eval_grouped.png")
