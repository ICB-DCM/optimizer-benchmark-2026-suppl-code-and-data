# Simulations with the best parameters

One PEtab simulation table per problem (`<short_problem_id>.tsv`),
simulated at the best parameters from `../best_x_within_walltime.json`
(see `../README.md`).
The columns and rows correspond to the measurement table of the respective
PEtab problem (benchmark collection v2024.11.11),
with `measurement` replaced by `simulation`.

The simulations were performed with the same software versions as the
Marvin pyPESTO optimizations
(see [`../../../optimizations/README.md`](../../../optimizations/README.md)).

## Parameter priors

For Isensee, Raimundez, and Schwen, parameter priors are part of the
objective function.
Priors on estimated parameters were converted to pseudo-measurements
(`petab.v1.priors.priors_to_measurements`),
resulting in additional rows with `observableId` `prior_<parameterId>`.
Drop them to compare against experimental data only.
