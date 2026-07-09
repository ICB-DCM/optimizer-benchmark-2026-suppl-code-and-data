"""
General settings / information / functions.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import scipy.stats

# Excluded benchmark collection problem IDs
EXCLUDED_PROBLEMS = {
    "Alkan_SciSignal2018",
    "Bachmann_MSB2011",
    "Froehlich_CellSystems2018",
    "Lang_PLOSComputBiol2024",
}

# Number of optimizers and problems used for the pre-pysacess part
N_OPTIMIZERS = 33
N_PROBLEMS = 30
N_RUNS = 10

# We only consider progress until this fraction of the SLURM budget
RELATIVE_WALLTIME_LIMIT = 0.8

# Misc paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROBLEM_OVERVIEW_PATH = BASE_DIR / "data" / "problem_overview_table.csv"
OPTIMIZER_OVERVIEW_PATH = BASE_DIR / "data" / "optimizer_overview_table.csv"
BENCHMARK_PROBLEMS_DIR = (
    BASE_DIR
    / "Benchmark-Models-PEtab-23c10f8b79b528bd96cee3a2ee47abd53580bad2"
    / "Benchmark-Models"
)
OUTPUT_DIR = BASE_DIR / "data_analysis" / "out"
OUTPUT_DIR.mkdir(exist_ok=True)


# Plotting settings
mpl_defaults = {
    "font.family": "sans-serif",
    # Arial is not available on Linux/CI; fall back to a substitute with
    # near-identical metrics, then matplotlib's bundled DejaVu Sans.
    "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
}
plt.rcParams.update(mpl_defaults)

# Options for subfigure titles .text()
SUBFIG_TITLE_KWARGS = {
    "fontsize": 10,
    "fontweight": "bold",
}


def get_threshold(percentile, df=1):
    """Get chi2 threshold for given percentile and degrees of freedom."""
    return scipy.stats.chi2.ppf(percentile, df) / 2
