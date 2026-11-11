# Data analysis

Scripts and notebooks for generating the figures in the paper. See
[`run_all.sh`](run_all.sh) to reproduce everything, and
[`../data/README.md`](../data/README.md) for the input data.

## Figures

| Figure | Script                                                  |
|--------|---------------------------------------------------------|
| 1      | `figure1.ipynb`                                         |
| 2      | `figure2.py`                                            |
| 3      | `analysis_3_4_reproducibility_and_optimality_gap.ipynb` |
| 4      | `analysis_3_4_reproducibility_and_optimality_gap.ipynb` |
| 5      | `analysis_5_first_hitting_times.ipynb`                  |
| 6      | `analysis_6_overall_efficiency.ipynb`                   |
| 7      | `analysis_7_pyscat_sacess.ipynb`                        |
| S1     | `figure_s1.ipynb`                                       |
| S2     | `analysis_0_simulation_times.ipynb`                     |
| S3     | `analysis_0_simulation_times.ipynb`                     |
| S4     | `analysis_3_4_reproducibility_and_optimality_gap.ipynb` |
| S5     | `analysis_3_4_reproducibility_and_optimality_gap.ipynb` |
| S6     | `analysis_3_4_reproducibility_and_optimality_gap.ipynb` |
| S7     | `analysis_7_pyscat_sacess.ipynb`                        |
| S8     | `analysis_3_4_reproducibility_and_optimality_gap.ipynb` |

## Model fits

`visualize_model_fit.py` plots the model fits for the best parameters in
[`../data/best_parameters/`](../data/best_parameters/) to `out/model_fits/`.
It requires the PEtab benchmark collection (v2024.11.11, see
[`../optimizations/README.md`](../optimizations/README.md)) and runs in its
own environment (see the inline script metadata and
`visualize_model_fit.py.lock`).
For many problems, it uses newer visualization tables from
[`model_fit_visualization/`](model_fit_visualization/):

```sh
uv run --script visualize_model_fit.py --benchmark-dir <path/to/Benchmark-Models>
```
