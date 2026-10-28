# Optimizations

Optimizations were performed on two HPC clusters: *Marvin* at University of
Bonn and *FinisTerrae III* at CSIC.

Due to the large-scale nature of the benchmark, the default storage format
of pyPESTO had to be adapted on both clusters to avoid exceeding the available
storage space. In particular on FinisTerrae III, a substantially reduced
storage format was used, which only stored monotonic per-run trajectories
instead of individual local optimization trajectories.

Optimizations were performed using the following container images:

* pyPESTO optimizers (scipy, nlopt, ...):
  for Marvin, see [pypesto-benchmark-docker/](pypesto-benchmark-docker/);
  for FinisTerrae III see
  [pypesto-benchmark-docker-limited-storage/](pypesto-benchmark-docker-limited-storage/)

* for parPE-saCeSS, see https://github.com/davidrpenas/sacess_parpe
  [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21294078.svg)](https://doi.org/10.5281/zenodo.21294078)

* pySaCeSS, see [pyscat-benchmark-docker/](pyscat-benchmark-docker/)

The `Dockerfile`s in these directories are the recipes of the images.
Note that the versions pinned in the `pip install` lines are partially
superseded by the subsequent `--force-reinstall` steps. The versions of the
relevant packages that were actually installed in the images that were used
(`pip list`) are:

| Package | Marvin | FinisTerrae III | pySaCeSS |
|---------|--------|-----------------|----------|
| amici   | 0.30.1 | 0.30.1 | 0.31.2 |
| cma     | 4.0.0  | 4.0.0  | 4.0.0  |
| cyipopt | 1.5.0  | 1.5.0  | 1.5.0  |
| fides   | 0.7.8  | 0.7.8  | 0.8.0  |
| Ipopt   | 3.11.9 | 3.11.9 | 3.14.17 |
| nlopt   | 2.8.0  | 2.8.0  | 2.8.0  |
| petab   | 0.5.0  | 0.5.0  | 0.8.1  |
| pypesto | 0.5.3 (modified, [a9093c2][fork-marvin]) | 0.5.3 (modified, [0faf8d2][fork-ft3]) | 0.5.8 |
| pyscat  | -      | -      | 0.0.1.post2.dev24+g03f949dee |
| pyswarm | 0.6    | 0.6    | 0.6    |
| Python  | 3.12   | 3.12   | 3.13   |
| scipy   | 1.15.2 | 1.15.2 | 1.17.0 |

Ipopt is the Ubuntu package of the respective base image (24.04: 3.11.9;
25.04: 3.14.17).
"Modified" pyPESTO refers to benchmark-specific commits of the
[stephanmg/pyPESTO](https://github.com/stephanmg/pyPESTO) fork
(based on the pyPESTO development state of 2024-10-23, shortly before the
0.5.4 release, reporting version 0.5.3):
[a9093c2][fork-marvin] in the Marvin image (see
[pypesto-benchmark-docker/](pypesto-benchmark-docker/)) and
[0faf8d2][fork-ft3] in the FinisTerrae III image (built from tag `v0.3.0` of
[pypesto-benchmark-docker-limited-storage/](pypesto-benchmark-docker-limited-storage/);
the image tagged `v0.2.0` contains the preceding commit, which differs only in
a wall-time limit for CMA-ES within `SacessOptimizer`, not used on
FinisTerrae III).
The changes of these commits relative to the pyPESTO 0.5.4 release
([GitHub](https://github.com/ICB-DCM/pyPESTO/releases/tag/v0.5.4),
[Zenodo: 10.5281/zenodo.14016957](https://doi.org/10.5281/zenodo.14016957))
are archived as patches in [pypesto-fork-patches/](pypesto-fork-patches/):
`git apply <patch>` on the source tree of pyPESTO 0.5.4 reproduces the
respective fork commit.
The fork branched off shortly before the release; the patches therefore also
revert the three release-only changes (version string, changelog entry, and a
deprecated alias in the PEtab importer).

[fork-marvin]: https://github.com/stephanmg/pyPESTO/commit/a9093c221d9a81c2b09784b6e21304fb81397dba
[fork-ft3]: https://github.com/stephanmg/pyPESTO/commit/0faf8d241d72989107917f177a7836d7bca8dbbf

The driver scripts for the optimizations
are [optimize_with_fixed_pyscat_final.py](optimize_with_fixed_pyscat_final.py)
(pySaCeSS) and [single_file_save.py](single_file_save.py) (pyPESTO-based
methods on Marvin); the corresponding script for FinisTerrae III is only
available in the later version used for the repeated runs (see below).

Runs whose jobs had been terminated before most of the compute budget was
recorded were repeated with updated images in which the wall-time
limit is passed to the optimizers:
on Marvin, the image built from
[pypesto-benchmark-docker/ipopt/Dockerfile](pypesto-benchmark-docker/ipopt/Dockerfile)
(Ipopt 3.14.20,
cyipopt 1.6.1, SciPy 1.14.1, pyPESTO fork commit [0d10b94][fork-marvin-reruns])
with [pypesto-benchmark-docker/benchmark.py](pypesto-benchmark-docker/benchmark.py);
on FinisTerrae III, the image tagged `v0.7.0` (Ipopt 3.14.20, cyipopt 1.6.1,
SciPy 1.17.1, fork commit [4ab0002][fork-ft3-reruns]) with
[pypesto-benchmark-docker-limited-storage/benchmark.py](pypesto-benchmark-docker-limited-storage/benchmark.py).
The patch of `4ab0002` is archived in
[pypesto-fork-patches/](pypesto-fork-patches/);
[single_file_save_with_timelimits.py](single_file_save_with_timelimits.py) is
an intermediate version of the Marvin driver script.

[fork-marvin-reruns]: https://github.com/stephanmg/pyPESTO/commit/0d10b9459e1b91eed97134ca5dbe9e3704245b2e
[fork-ft3-reruns]: https://github.com/stephanmg/pyPESTO/commit/4ab000212cce2c4d7c23afc55440e1ec506ca719

The benchmark problems are available in the
[PEtab benchmark problem collection](https://github.com/Benchmarking-Initiative/Benchmark-Models-PEtab);
version [v2024.11.11](https://doi.org/10.5281/zenodo.18356087) was used.
