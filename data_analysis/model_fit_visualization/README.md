# Visualization tables for model fit plots

Visualization tables for `../visualize_model_fit.py`,
taken from a newer version of the
[PEtab benchmark collection](https://github.com/PEtab-dev/petab-benchmark-problems)
(commit `dbd3e3d82b2fe093ff39639cc2d3850568e7fdbb`, `problems/<problem_id>/v1/`)
than the one used in the study (v2024.11.11).
The study version lacks visualization tables for some problems
or has less informative ones.

Per problem directory:

* `visualizations.tsv`: the newer visualization table, used instead of the
  original one
* `dataset_ids.tsv`: if the newer visualization table refers to `datasetId`s
  that differ from or are missing in the study version's measurement table:
  the newer `datasetId` for each
  (`observableId`, `preequilibrationConditionId`, `simulationConditionId`,
  `time`)

Only tables that differ from the study version
and are compatible with the study version's measurement table are included
(validated with `petab.v1.visualize.lint.validate_visualization_df`).
Generated with:

```sh
uv run --script import_visualization_tables.py \
    <v2024.11.11 Benchmark-Models dir> <newer collection problems dir>
```
