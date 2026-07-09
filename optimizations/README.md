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

* pySaCeSS, see [pyscat-benchmark-docker/](pyscat-benchmark-docker/)

The driver scripts for the optimizations
are [optimize_with_fixed_pyscat_final.py](optimize_with_fixed_pyscat_final.py)
and [single_file_save_with_timelimits.py](single_file_save_with_timelimits.py).

The benchmark problems are available in the 
[PEtab benchmark problem collection](https://github.com/Benchmarking-Initiative/Benchmark-Models-PEtab);
version [v2024.11.11](https://doi.org/10.5281/zenodo.18356087) was used.

