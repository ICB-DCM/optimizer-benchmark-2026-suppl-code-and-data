# Data

Summarized benchmark results, sufficient to reproduce the figures in the
paper (see [`../data_analysis/`](../data_analysis/)).

## `problem_overview_table.csv`

One row per benchmark problem (from the PEtab Benchmark collection).

| Column                   | Description                                                                                                    |
|--------------------------|----------------------------------------------------------------------------------------------------------------|
| `id`                     | Full benchmark collection problem ID                                                                           |
| `short`                  | Short problem name used elsewhere in this dataset                                                              |
| `n_conditions`           | Number of experimental conditions (based on the PEtab implementation)                                          |
| `n_est_parameters`       | Number of estimated parameters                                                                                 |
| `n_observables`          | Number of observables (based on the PEtab implementation)                                                      |
| `n_measurements`         | Number of data points                                                                                          |
| `error_model_type`       | Noise model type (e.g. constant, parameter-dependent)                                                          |
| `initial_condition_type` | How initial conditions are specified (e.g. given, analytical)                                                  |
| `sensitivity_method`     | Sensitivity method used for gradient computation (`FSA`, `ASA`), unless Hessian is required, then always `FSA` |
| `amici_nx_solver`        | Number of ODE state variables in the AMICI-imported model                                                      |
| `difficulty`             | Assigned difficulty category (easy/hard, corresponding to subset I/II, respectively                            |
| `walltime_s`             | Wall time budget allotted for optimization (s)                                                                 |
| `n_cores`                | Number of CPU cores used                                                                                       |
| `cputime_s`              | CPU time budget (`walltime_s * n_cores`)                                                                       |
| `problem_color`          | Hex color used for this problem in plots                                                                       |

## `optimizer_overview_table.csv`

One row per optimizer/method configuration used in the benchmark.

| Column               | Description                                                          |
|----------------------|----------------------------------------------------------------------|
| `slurm_name`         | Job name used on the cluster                                         |
| `output_dir`         | Output directory / optimizer ID used to join with results files      |
| `optimizer_label`    | Display label used in plots                                          |
| `package`            | Software package providing the optimizer                             |
| `objective_impl`     | Objective function implementation used                               |
| `is_pysacess`        | Whether this is a pySACESS (pyscat) run                              |
| `excluded`           | Whether this optimizer is excluded from the benchmarking             |
| `description`        | Free-text notes                                                      |
| `original_id`        | Original identifier, if renamed                                      |
| `supports_gradients` | Whether the optimizer uses gradients                                 |
| `supports_hessian`   | Whether the optimizer uses the Hessian                               |
| `supports_bounds`    | Whether the optimizer supports bound constraints                     |
| `gradient_based`     | Whether the optimizer is gradient-based                              |
| `hessian_based`      | Whether the optimizer is Hessian-based                               |
| `is_global`          | Whether the optimizer is a global method                             |
| `is_local`           | Whether the optimizer is a local method                              |
| `output_dir_ft3`     | Output directory used on the ft3 site (may differ from `output_dir`) |
| `always_fsa`         | Whether this optimizer was always run with forward sensitivities     |
| `optimizer_color`    | Hex color used for this optimizer in plots                           |

## `best_fx_marvin.csv` / `best_fx_ft3.csv`

One row per (problem, optimizer, run), giving the best objective value found
by that multi-start run on the given compute site (30 problems, 10 runs each; `marvin`/`ft3` respectively per file).

| Column      | Description                                                     |
|-------------|-----------------------------------------------------------------|
| `problem`   | Short problem name (see `problem_overview_table.csv`)           |
| `optimizer` | Optimizer ID (see `optimizer_overview_table.csv`, `output_dir`) |
| `run_idx`   | Run index (1-10)                                                |
| `fx_best`   | Best objective function value found in this run                 |
| `site`      | Compute site (`marvin` or `ft3`)                                |

## `fval_at_timepoints.csv`

Best-so-far objective value at fixed fractions of the walltime budget, per
(problem, optimizer, run); used for convergence/efficiency analysis.

| Column               | Description                                                          |
|----------------------|----------------------------------------------------------------------|
| `problem`            | Short problem name                                                   |
| `optimizer`          | Optimizer ID                                                         |
| `run_idx`            | Run index (1-10)                                                     |
| `timepoint_fraction` | Fraction of the walltime budget elapsed (0.001, 0.01, 0.1, 0.5, 1.0) |
| `fval`               | Best objective value found by this timepoint                         |

## `individual_starts_for_fig_6b.csv`

Per-start (not just per-run-best) optimality gaps for one problem, used for
Figure 6B.

| Column           | Description                                              |
|------------------|----------------------------------------------------------|
| `problem`        | Short problem name                                       |
| `optimizer`      | Optimizer ID                                             |
| `run_idx`        | Run index (1-10)                                         |
| `optimality_gap` | Optimality gap of an individual multi-start for this run |

## `successful_starts.json`

List of records (one per problem/optimizer/run) with the number of
individual optimizer starts that reached a given significance threshold.

| Field            | Description                                                                           |
|------------------|---------------------------------------------------------------------------------------|
| `problem`        | Short problem name                                                                    |
| `optimizer`      | Optimizer ID                                                                          |
| `run_idx`        | Run index                                                                             |
| `fval_threshold` | Objective value threshold defining "success" (from the chi2-based significance level) |
| `significance`   | Significance level used to derive `fval_threshold`                                    |
| `n_success`      | Number of starts within this run that reached the threshold                           |
| `overall_time_s` | Total wall-clock time of the run (s)                                                  |

## `first_hitting_times_marvin.json`

List of records (one per problem/optimizer, marvin site only) with the time
at which the best-so-far objective first crossed each of several
significance thresholds across all 10 runs.

| Field                 | Description                                                       |
|-----------------------|-------------------------------------------------------------------|
| `problem`             | Short problem name                                                |
| `optimizer`           | Optimizer ID                                                      |
| `significance_levels` | Significance levels for which thresholds were computed            |
| `thresholds`          | Objective value thresholds corresponding to `significance_levels` |
| `best_fval`           | Best objective value found overall for this problem/optimizer     |
| `times`               | First-hitting time (s) for each threshold in `thresholds`         |

## `simulation_times/<problem_id>.json`

One file per benchmark problem; all files share the same schema. Each file
is a list of records, one per randomly sampled parameter vector, with
per-condition AMICI simulation timing/status. Used to characterize the raw
computational cost of evaluating each problem's objective function (with
and without sensitivities).

| Field                     | Description                                                        |
|---------------------------|--------------------------------------------------------------------|
| `problem_id`              | Full benchmark collection problem ID                               |
| `sample_idx`              | Index of the sampled parameter vector                              |
| `sensitivity_method`      | Sensitivity method used (`none`, `fsa`, `asa`)                     |
| `time_obj_s`              | Total wall time for the objective (and sensitivity) evaluation (s) |
| `fval`                    | Objective function value at the sampled parameters                 |
| `condition_ids`           | Experimental condition IDs simulated                               |
| `amici_status`            | AMICI simulation status per condition                              |
| `amici_cpu_times_total_s` | AMICI simulation CPU time per condition (s)                        |
| `amici_messages`          | AMICI messages/warnings per condition                              |
