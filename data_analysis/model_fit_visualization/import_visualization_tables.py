#!/usr/bin/env python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "pandas>=3.1.1",
#   "petab[vis]>=0.10.0",
# ]
# ///
"""Import visualization tables from a newer PEtab benchmark collection.

The benchmark collection version used in the study (v2024.11.11) lacks
visualization tables for some problems, or has unhelpful ones. This copies
visualization tables from a newer collection version, where they are
compatible with the study version of the problem.

For each problem, writes to ``<problem_id>/``:

* ``visualizations.tsv``: the newer visualization table
* ``dataset_ids.tsv``: (only if the datasetIds differ from the study
  version) mapping of measurement keys to the newer datasetIds

Usage:

    uv run --script import_visualization_tables.py \\
        <old Benchmark-Models dir> <new problems dir> [problem_id ...]
"""

import shutil
import sys
from pathlib import Path

import pandas as pd
from petab.v1 import C as ptC
from petab.v1 import Problem, get_measurement_df, get_visualization_df
from petab.v1.visualize.lint import validate_visualization_df

OUT_DIR = Path(__file__).resolve().parent
PROBLEM_OVERVIEW_PATH = (
    OUT_DIR.parent.parent / "data" / "problem_overview_table.csv"
)
KEY_COLS = [
    ptC.OBSERVABLE_ID,
    ptC.PREEQUILIBRATION_CONDITION_ID,
    ptC.SIMULATION_CONDITION_ID,
    ptC.TIME,
]


def measurement_keys(df: pd.DataFrame) -> pd.DataFrame:
    """Get the key columns of a measurement table, with empty strings for
    missing preequilibration conditions."""
    df = df.copy()
    if ptC.PREEQUILIBRATION_CONDITION_ID not in df:
        df[ptC.PREEQUILIBRATION_CONDITION_ID] = ""
    df[ptC.PREEQUILIBRATION_CONDITION_ID] = (
        df[ptC.PREEQUILIBRATION_CONDITION_ID].astype("str").fillna("")
    )
    return df[KEY_COLS + ([ptC.DATASET_ID] if ptC.DATASET_ID in df else [])]


def get_dataset_ids(
    old_mdf: pd.DataFrame, new_mdf: pd.DataFrame
) -> pd.DataFrame:
    """Map datasetIds of the new measurement table to the old one.

    Raises if the mapping is not unique or incomplete.
    """
    new_keys = measurement_keys(new_mdf).drop_duplicates()
    if new_keys.duplicated(KEY_COLS).any():
        raise ValueError("datasetId not unique for measurement keys")
    old_keys = measurement_keys(old_mdf)[KEY_COLS].drop_duplicates()
    mapping = old_keys.merge(new_keys, on=KEY_COLS, how="left")
    if mapping[ptC.DATASET_ID].isna().any():
        raise ValueError("Measurement keys missing in new measurement table")
    return mapping


def import_one(problem_id: str, old_dir: Path, new_dir: Path) -> str:
    """Import the visualization table for a single problem."""
    yaml_path = old_dir / problem_id / f"{problem_id}.yaml"
    if not yaml_path.exists():
        yaml_path = yaml_path.with_name("problem.yaml")
    problem = Problem.from_yaml(yaml_path)

    new_problem_dir = new_dir / problem_id / "v1"
    (new_vis_file,) = new_problem_dir.glob("visualization*.tsv")
    new_vis_df = get_visualization_df(new_vis_file)
    if (
        problem.visualization_df is not None
        and problem.visualization_df.equals(new_vis_df)
    ):
        return "unchanged"

    (new_meas_file,) = new_problem_dir.glob("measurement*.tsv")
    new_mdf = get_measurement_df(new_meas_file)
    dataset_ids = None
    if ptC.DATASET_ID in new_mdf:
        dataset_ids = get_dataset_ids(problem.measurement_df, new_mdf)
        merged = measurement_keys(problem.measurement_df)[KEY_COLS].merge(
            dataset_ids, on=KEY_COLS, how="left"
        )
        if (
            ptC.DATASET_ID in problem.measurement_df
            and (
                problem.measurement_df[ptC.DATASET_ID].values
                == merged[ptC.DATASET_ID].values
            ).all()
        ):
            dataset_ids = None
        else:
            problem.measurement_df = problem.measurement_df.assign(
                datasetId=merged[ptC.DATASET_ID].values
            )

    problem.visualization_df = new_vis_df
    if validate_visualization_df(problem):
        raise ValueError("Invalid visualization table")

    out_dir = OUT_DIR / problem_id
    out_dir.mkdir(exist_ok=True)
    shutil.copyfile(new_vis_file, out_dir / "visualizations.tsv")
    if dataset_ids is not None:
        dataset_ids.to_csv(out_dir / "dataset_ids.tsv", sep="\t", index=False)
        return "imported (with datasetIds)"
    return "imported"


def main():
    old_dir, new_dir = map(Path, sys.argv[1:3])
    problem_ids = sys.argv[3:] or list(
        pd.read_csv(PROBLEM_OVERVIEW_PATH)["id"]
    )
    for problem_id in problem_ids:
        try:
            status = import_one(problem_id, old_dir, new_dir)
        except Exception as e:  # noqa: BLE001
            status = f"skipped: {type(e).__name__}: {e}"
        print(f"{problem_id}: {status}")


if __name__ == "__main__":
    main()
