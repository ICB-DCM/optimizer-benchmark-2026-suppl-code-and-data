[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21296723.svg)](https://doi.org/10.5281/zenodo.21296723)

# README

This is the supplementary code and data for the paper *Large-scale analysis of
optimisation methods for parameter estimation problems in the life sciences* by
Stephan Grein, David R. Penas, Daniel Weindl, Polina Lakrisenko, Julio R.
Banga, and Jan Hasenauer.

## Data generation

Information about the optimization runs is provided in the
[`optimizations/` directory](optimizations/).

## Data

Due to the large size of the raw data, we only provide summarized data that is
sufficient to generate the individual components of the figures in the paper.
These data are available in the [`data/` directory](data/).

## Data analysis scripts

Scripts for generating the figures in the paper are available in the [
`data_analysis/` directory](data_analysis/).

### Requirements and tested platforms

Python ≥ 3.13, installed automatically by `uv`. Tested on Linux and Windows
via CI ([`data-analysis.yml`](.github/workflows/data-analysis.yml); on
Windows, use Git Bash or WSL, not `cmd.exe`/PowerShell); not tested on
macOS, but no platform-specific dependencies are used. Please open an issue
with any installation/execution problems you run into.

### Reproducing the figures without HPC

No HPC cluster, MPI, containers, or AMICI/model compilation is needed to
reproduce the figures - those are only required to regenerate the raw optimizer
trajectories in [`optimizations/`](optimizations/). The summarized data in
[`data/`](data/) is enough to generate the individual components of the
figures included in the manuscript and supplemental information with
`./run_all.sh` on a standard computer; assembling these into the final
composite figures required additional manual work, and some panels may show
rendering artifacts (e.g. overplotting) not present in the published
versions.

### Reproducing the analysis

The analysis environment is managed with [uv](https://docs.astral.sh/uv/).
To reproduce all figures and tables, run:

```sh
cd data_analysis
./run_all.sh
```

This installs the pinned Python environment (`uv sync --frozen`) and then
runs every notebook and script in the directory, in dependency order,
writing the generated figures and tables to `data_analysis/out/`.

## License

Code is licensed under the BSD 3-Clause License (see LICENSE), and data is
licensed under CC-BY-4.0 (see LICENSE-DATA).
