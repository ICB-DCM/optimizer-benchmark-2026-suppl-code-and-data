# Best parameter vectors

The best parameter vector found for each of the 30 benchmark problems,
over all optimizers and runs on Marvin,
within 80% of the walltime budget (`walltime_s` in
`../problem_overview_table.csv`), as in the rest of the analysis.
Only parameter vectors within the parameter bounds were considered.
For all problems, this coincides with the best objective value (`../best_fx_marvin.csv`).

Forward simulations for these parameters are in [`simulations/`](simulations/).

## `best_x_within_walltime.csv`

One row per (problem, parameter).

| Column                                   | Description                                                       |
|------------------------------------------|-------------------------------------------------------------------|
| `problem`, `problem_id`                  | Short and full problem ID                                         |
| `parameterId`                            | PEtab parameter ID                                                |
| `parameterScale`                         | PEtab parameter scale (`log10` or `lin`)                          |
| `value_scaled`, `value_linear`           | Parameter value on `parameterScale` and on linear scale           |
| `lowerBound_scaled`, `upperBound_scaled` | Parameter bounds on `parameterScale`                              |
| `lowerBound_linear`, `upperBound_linear` | Parameter bounds on linear scale                                  |
| `optimizer`, `run_idx`                   | Optimizer ID and run index that found this parameter vector       |
| `fval`                                   | Objective function value (see `best_x_within_walltime.json`)      |
| `x_flagged`                              | See [Beer](#beer)                                                 |

## `best_x_within_walltime.json`

Same content as the CSV, keyed by short problem name.

| Field              | Description                                                                                     |
|--------------------|-------------------------------------------------------------------------------------------------|
| `fval`             | Best objective function value (negative log-likelihood/posterior) within the walltime limit     |
| `x`                | Parameter vector on PEtab parameter scale, in the order of `petab.v1.Problem.x_free_ids`        |
| `time`             | Wall time (s) within the run at which `x` was recorded                                          |
| `walltime_limit_s` | Walltime limit applied (s)                                                                      |
| `optimizer`        | Optimizer ID (see `../optimizer_overview_table.csv`, `output_dir`)                              |
| `run_idx`          | Run index (1-10)                                                                                |
| `x_flagged`        | Whether `x` was recorded later than `fval`, see [Beer](#beer)                                   |

## Beer

parPE-saCeSS only stored the final parameter vector of each run, not the
intermediate ones.
For Beer, the best result was found by `sacess_dhc`, so `x` is the final
parameter vector of that run (`time` = 32400 s, after the walltime limit),
whereas `fval` is the best value within the walltime limit.
Therefore, `fval` (-61862.93) and the objective function value at `x`
(-61864.67) differ slightly.
This is the only problem with `x_flagged = true`.
