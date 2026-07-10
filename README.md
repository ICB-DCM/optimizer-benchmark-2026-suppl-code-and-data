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
sufficient to reproduce the figures in the paper. These data are available in
the [`data/` directory](data/).

## Data analysis scripts

Scripts for generating the figures in the paper are available in the [
`data_analysis/` directory](data_analysis/).

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
