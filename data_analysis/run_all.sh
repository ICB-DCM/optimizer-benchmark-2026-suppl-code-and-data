#!/usr/bin/env bash
# Reproduce all data analysis results: runs every notebook and script in
# this directory, in dependency order, and (re)creates data_analysis/out/.
#
# Usage: ./run_all.sh
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export MPLBACKEND=Agg

uv sync --frozen

NOTEBOOKS=(
    figure1.ipynb
    figure_s1.ipynb
    analysis_0_simulation_times.ipynb
    analysis_3_4_reproducibility_and_optimality_gap.ipynb
    analysis_5_first_hitting_times.ipynb
    analysis_6_overall_efficiency.ipynb
    analysis_7_pyscat_sacess.ipynb
)

for notebook in "${NOTEBOOKS[@]}"; do
    echo "=== Running ${notebook} ==="
    uv run --frozen jupyter nbconvert --to notebook --execute --inplace "${notebook}"
done

echo "=== Running figure2.py ==="
uv run --frozen python figure2.py

echo "All done. See out/ for generated figures and tables."
