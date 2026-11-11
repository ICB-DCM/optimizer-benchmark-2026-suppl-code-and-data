#!/usr/bin/env python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "matplotlib>=3.11.2",
#   "pandas>=3.1.1",
#   "petab[vis]>=0.10.0",
# ]
# ///
"""Plot model fits for the best parameters found in the benchmark.

Uses the simulation tables in ``data/best_parameters/simulations/`` and
the original PEtab problems (benchmark collection v2024.11.11, not part
of this repository) to create one model fit figure per problem via
``petab.v1.visualize.plot_problem``. Where available, visualization tables
from a newer benchmark collection version in ``model_fit_visualization/``
are used instead of the original ones.

Runs in its own environment (more recent petab than the main analysis):

    uv run --script visualize_model_fit.py [problem_id ...]
"""

import argparse
import json
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from petab.v1 import C as ptC
from petab.v1 import Problem, get_simulation_df, get_visualization_df
from petab.v1.visualize import plot_problem, plotter, plotting

BASE_DIR = Path(__file__).resolve().parent.parent
# same as in lib.py; not imported to keep this script's environment small
PROBLEM_OVERVIEW_PATH = BASE_DIR / "data" / "problem_overview_table.csv"
BENCHMARK_PROBLEMS_DIR = (
    BASE_DIR
    / "petab-benchmark-problems-23c10f8b79b528bd96cee3a2ee47abd53580bad2"
    / "Benchmark-Models"
)
BEST_PARAMETERS_DIR = BASE_DIR / "data" / "best_parameters"
DEFAULT_BEST_X_PATH = BEST_PARAMETERS_DIR / "best_x_within_walltime.json"
DEFAULT_SIM_DIR = BEST_PARAMETERS_DIR / "simulations"
DEFAULT_FIG_DIR = BASE_DIR / "data_analysis" / "out" / "model_fits"
VIS_OVERRIDE_DIR = BASE_DIR / "data_analysis" / "model_fit_visualization"

# Problems with many subplots that need a larger figure
LARGE_FIGSIZE = {
    "Raimundez": [80, 60],
    "Lucarelli": [80, 60],
}


def _measurement_keys(df: pd.DataFrame) -> pd.DataFrame:
    """Get the columns identifying a measurement, with empty strings for
    missing preequilibration conditions."""
    keys = pd.DataFrame(
        {
            ptC.OBSERVABLE_ID: df[ptC.OBSERVABLE_ID].values,
            ptC.PREEQUILIBRATION_CONDITION_ID: (
                df[ptC.PREEQUILIBRATION_CONDITION_ID].astype("str").fillna("")
                if ptC.PREEQUILIBRATION_CONDITION_ID in df
                else ""
            ),
            ptC.SIMULATION_CONDITION_ID: df[
                ptC.SIMULATION_CONDITION_ID
            ].values,
            ptC.TIME: df[ptC.TIME].values,
        }
    )
    return keys


def _set_dataset_ids(df: pd.DataFrame, dataset_ids: pd.DataFrame):
    """Set datasetIds in a measurement or simulation table."""
    keys = _measurement_keys(df)
    merged = keys.merge(dataset_ids, on=list(keys.columns), how="left")
    if len(merged) != len(df) or merged[ptC.DATASET_ID].isna().any():
        raise AssertionError("Incomplete datasetId mapping.")
    return df.assign(datasetId=merged[ptC.DATASET_ID].values)


def _join_truncated(values, max_n: int = 3) -> str:
    """Join values to a comma-separated string, truncated after `max_n`."""
    values = list(values)
    if len(values) <= max_n:
        return ", ".join(values)
    return ", ".join(values[:max_n]) + f", ... ({len(values)} total)"


def tidy_figure(fig: plt.Figure, width_factor: float = 1.6):
    """Make room for legends and long labels.

    Places all axes legends, without duplicate entries, to the right of
    their axes, wraps long axis labels, widens the figure by
    `width_factor`, and uses constrained layout.
    """
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            label = axis.label.get_text()
            # missing labels in the visualization table
            label = "" if label == "nan" else label
            axis.label.set_text(textwrap.fill(label, 30))
        if ax.get_legend() is None:
            continue
        # bar plots repeat "measurement"/"simulation" for each dataset
        handles, labels = ax.get_legend_handles_labels()
        unique = dict(zip(labels, handles, strict=True))
        ax.legend(
            unique.values(),
            unique.keys(),
            loc="upper left",
            bbox_to_anchor=(1.02, 1),
            fontsize="small",
            frameon=False,
        )
    width, height = fig.get_size_inches()
    fig.set_size_inches(width * width_factor, height)
    fig.set_layout_engine("constrained")


def apply_visualization_override(
    long_id: str, petab_problem: Problem, sim_df: pd.DataFrame
) -> pd.DataFrame:
    """Use the newer visualization table and datasetIds, if available.

    Updates ``petab_problem`` in place and returns the updated simulation
    table.
    """
    override_dir = VIS_OVERRIDE_DIR / long_id
    if (vis_file := override_dir / "visualizations.tsv").exists():
        petab_problem.visualization_df = get_visualization_df(vis_file)
    if (dataset_id_file := override_dir / "dataset_ids.tsv").exists():
        dataset_ids = pd.read_csv(
            dataset_id_file,
            sep="\t",
            dtype={
                ptC.PREEQUILIBRATION_CONDITION_ID: "str",
                ptC.TIME: float,
            },
            keep_default_na=False,
        )
        petab_problem.measurement_df = _set_dataset_ids(
            petab_problem.measurement_df, dataset_ids
        )
        sim_df = _set_dataset_ids(sim_df, dataset_ids)

    # Empty plot names would show up as "nan" -- use the observables instead
    vis_df = petab_problem.visualization_df
    if vis_df is not None:
        vis_df[ptC.PLOT_NAME] = (
            vis_df[ptC.PLOT_NAME].astype("str")
            if ptC.PLOT_NAME in vis_df
            else pd.Series(pd.NA, index=vis_df.index, dtype="str")
        )
        if ptC.Y_VALUES in vis_df:
            y_values = vis_df.groupby(ptC.PLOT_ID)[ptC.Y_VALUES].transform(
                lambda y: _join_truncated(y.dropna().unique())
            )
            vis_df[ptC.PLOT_NAME] = vis_df[ptC.PLOT_NAME].fillna(y_values)
    return sim_df


def load_simulations(
    short_id: str, petab_problem: Problem, sim_dir: Path
) -> pd.DataFrame:
    """Load the simulation table and prepare it for plotting."""
    sim_df = get_simulation_df(sim_dir / f"{short_id}.tsv")

    # drop the pseudo-measurements resulting from priors
    sim_df = sim_df[
        sim_df[ptC.OBSERVABLE_ID].isin(
            petab_problem.measurement_df[ptC.OBSERVABLE_ID]
        )
    ]
    if len(sim_df) != len(petab_problem.measurement_df):
        raise AssertionError(
            f"{short_id}: {len(sim_df)} simulations, but "
            f"{len(petab_problem.measurement_df)} measurements."
        )
    return sim_df


def visualize_one(
    short_id: str,
    long_id: str,
    sim_dir: Path,
    fig_dir: Path,
    benchmark_dir: Path,
    best_x_entry: dict,
) -> Path:
    """Create the model fit figure for a single problem."""
    yaml_path = benchmark_dir / long_id / f"{long_id}.yaml"
    if not yaml_path.exists():
        yaml_path = yaml_path.with_name("problem.yaml")
    petab_problem = Problem.from_yaml(yaml_path)
    sim_df = load_simulations(short_id, petab_problem, sim_dir)
    sim_df = apply_visualization_override(long_id, petab_problem, sim_df)

    with plt.rc_context({"font.size": plt.rcParams["font.size"] * 1.5}):
        plotter.measurement_line_kwargs["linestyle"] = ""
        default_figsize = plotting.DEFAULT_FIGSIZE[:]
        if short_id in LARGE_FIGSIZE:
            plotting.DEFAULT_FIGSIZE[:] = LARGE_FIGSIZE[short_id]
        try:
            plot_problem(petab_problem, simulations_df=sim_df)
        finally:
            plotting.DEFAULT_FIGSIZE[:] = default_figsize

        fig = plt.gcf()
        tidy_figure(fig)
        fig.suptitle(
            f"{long_id}  |  fval={best_x_entry['fval']:.4g}"
            f"  |  {best_x_entry['optimizer']}"
            f" (run {best_x_entry['run_idx']})",
            fontsize="x-large",
            fontweight="bold",
        )

    out_path = fig_dir / f"{short_id}.pdf"
    plt.savefig(out_path, bbox_inches="tight")
    plt.close("all")
    return out_path


def main():
    parser = argparse.ArgumentParser(
        description="Plot model fits from pre-computed simulation tables."
    )
    parser.add_argument(
        "problem_ids",
        nargs="*",
        metavar="problem_id",
        help="Short problem ID(s) to process (default: all)",
    )
    parser.add_argument(
        "--best-x",
        type=Path,
        default=DEFAULT_BEST_X_PATH,
        help=f"Best parameters JSON file (default: {DEFAULT_BEST_X_PATH})",
    )
    parser.add_argument(
        "--sim-dir",
        type=Path,
        default=DEFAULT_SIM_DIR,
        help=f"Simulation table directory (default: {DEFAULT_SIM_DIR})",
    )
    parser.add_argument(
        "--fig-dir",
        type=Path,
        default=DEFAULT_FIG_DIR,
        help=f"Output directory (default: {DEFAULT_FIG_DIR})",
    )
    parser.add_argument(
        "--benchmark-dir",
        type=Path,
        default=BENCHMARK_PROBLEMS_DIR,
        help="`Benchmark-Models` directory of the PEtab benchmark "
        f"collection (default: {BENCHMARK_PROBLEMS_DIR})",
    )
    args = parser.parse_args()

    with open(args.best_x) as f:
        best_x_data = json.load(f)

    short_to_long = (
        pd.read_csv(PROBLEM_OVERVIEW_PATH).set_index("short")["id"].to_dict()
    )
    if unknown := set(args.problem_ids) - set(short_to_long):
        raise SystemExit(
            f"Unknown problem ID(s): {sorted(unknown)}\n"
            f"Available: {list(short_to_long)}"
        )
    problems_to_run = args.problem_ids or list(short_to_long)

    args.fig_dir.mkdir(parents=True, exist_ok=True)

    errors = []
    for short_id in problems_to_run:
        print(f"[{short_id}]")
        try:
            out_path = visualize_one(
                short_id,
                short_to_long[short_id],
                sim_dir=args.sim_dir,
                fig_dir=args.fig_dir,
                benchmark_dir=args.benchmark_dir,
                best_x_entry=best_x_data[short_id],
            )
            print(f"  Saved: {out_path}")
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR: {type(e).__name__}: {e}")
            errors.append(short_id)

    n_ok = len(problems_to_run) - len(errors)
    print(f"\nDone: {n_ok}/{len(problems_to_run)} succeeded.")
    if errors:
        raise SystemExit(f"Failed: {errors}")


if __name__ == "__main__":
    main()
