---
hide:
  - navigation
---

# Manual Evaluation Explorer

The manual evaluation datasets are available on [Hugging Face - adbX/reproscreener_manual_evaluations](https://huggingface.co/datasets/adbX/reproscreener_manual_evaluations).

/// marimo-embed
    height: 400px
    mode: read
    app_width: wide
    include_code: false

```python
@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Manual Evaluation Explorer""")
    return


@app.cell(hide_code=True)
def _():
    import pandas as pd
    import numpy as np
    return np, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Reproscreener (regex) vs. Manual evaluations of preprint manuscripts""")
    return


@app.cell
def _(pd):
    df_manuscript = pd.read_csv("https://huggingface.co/datasets/adbX/reproscreener_manual_evaluations/resolve/main/manuscript.csv")

    df_manuscript.set_index("paper_id", inplace=True)
    df_manuscript = df_manuscript.drop(
        columns=["evaluation_type", "source_file"]
        + [col for col in df_manuscript.columns if "_description" in col]
    )

    df_manuscript
    return
```

///

/// marimo-embed-file
    filepath: ./docs/02_manual_eval_explorer.py
///