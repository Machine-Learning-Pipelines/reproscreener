#!/usr/bin/env python
"""Export manual evaluation tables to files that can be served with a WASM notebook.

This script should be run **offline** (regular CPython). It parses all manual
evaluation CSVs using `ManualEvaluationParser` and writes each resulting
DataFrame to a Parquet file inside `notebooks/public/`, alongside
`02_manual_eval_explorer.py`.  Marimo bundles that folder automatically when
exporting the notebook to WASM HTML, so the data will be available in the
browser without requiring any server-side code.

Run it from the project root:

    python scripts/export_manual_eval_tables.py

Optional arguments allow changing the destination directory or output format::

    python scripts/export_manual_eval_tables.py --dest notebooks/public --fmt csv

"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Literal

import pandas as pd

try:
    from reproscreener.manual_evaluations.manual_eval import ManualEvaluationParser
except ImportError as exc:
    raise SystemExit(
        "Could not import reproscreener. Make sure you run this script from the project root "
        "with the package installed in your environment."
    ) from exc

LOG = logging.getLogger(__name__)


ALLOWED_FMTS: tuple[str, ...] = ("parquet", "csv", "feather")


def export_tables(dest_dir: Path, file_fmt: Literal["parquet", "csv", "feather"] = "parquet") -> None:
    """Parse evaluation files and export each DataFrame to *dest_dir*.

    The filename pattern is ``{dataset_name}.{file_fmt}``, where *dataset_name*
    refers to the keys returned by ``ManualEvaluationParser().load_all_evaluations()``.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)

    parser = ManualEvaluationParser()
    evaluations = parser.load_all_evaluations()

    for name, df in evaluations.items():
        if df.empty:
            LOG.warning("Dataset '%s' is empty – skipping export.", name)
            continue

        path_out = dest_dir / f"{name}.{file_fmt}"
        # Display a nice relative path when possible, but fall back to absolute
        try:
            display_path = path_out.resolve().relative_to(Path.cwd())
        except ValueError:
            display_path = path_out

        LOG.info("Writing %s (%d rows) to %s", name, len(df), display_path)

        if file_fmt == "parquet":
            df.to_parquet(path_out, index=False)
        elif file_fmt == "csv":
            df.to_csv(path_out, index=False)
        elif file_fmt == "feather":
            df.reset_index(drop=True).to_feather(path_out)
        else:
            raise ValueError(f"Unsupported format: {file_fmt}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:  # noqa: D401
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Export manual evaluation tables for WASM notebooks.")
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path("notebooks/public"),
        help="Destination directory (defaults to notebooks/public).",
    )
    parser.add_argument(
        "--fmt",
        choices=ALLOWED_FMTS,
        default="parquet",
        help="Output file format (parquet, csv, feather). Default: parquet.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress info-level logging.",
    )
    return parser.parse_args()


def main() -> None:  # noqa: D401
    args = _parse_args()
    logging.basicConfig(level=logging.INFO if not args.quiet else logging.WARNING, format="%(levelname)s: %(message)s")

    export_tables(args.dest, args.fmt)  # type: ignore[arg-type]
    LOG.info("Export complete ✓")


if __name__ == "__main__":
    main()