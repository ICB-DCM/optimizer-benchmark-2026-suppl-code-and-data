# pypesto-benchmark-docker
[![Build and Push Docker Image](https://github.com/stephanmg/pypesto-benchmark-docker/actions/workflows/push_docker.yaml/badge.svg)](https://github.com/stephanmg/pypesto-benchmark-docker/actions/workflows/push_docker.yaml)

## Build
`docker build -t pypesto_benchmark_docker .`

## Export for apptainer

`docker save -o pypesto_benchmark_docker.tar pypesto_benchmark_docker`

## Convert to apptainer

`apptainer build pypesto_benchmark_docker.sif docker-archive:://pypesto_benchmark_docker.tar`

## Copy requirements
Use `docker ps` to find container ID, then call:
`docker cp CONTAINER_ID:/requirements.txt .`

The requirements file `requirements.txt` is automatically generated from the latest tagged release (currently v0.3.0).

## Releases
`latest` corresponds currently to `v0.2.0` and considered latest stable/tested version.

- v0.4.12: Latest cyipopt package version
- v0.4.12: Fix mpi4py version
- v0.4.11: Small corrections, safeguard to write problem definition only once to h5 file
- v0.4.10: Correct walltime for optimizers without support
- v0.4.3: c3f61935ec5bdeab4d18e8e4aa9b09aa3769f81e (install pyscat)
- v0.4.2: a986fc9894deabda46a072b672731ce07113487c (fix SWIG and install AMICI==0.30.1)
- v0.4.1: 88e99179fe94c1b81c49c039161fe4d9178a0f7c (downgrade cyipopt to 1.5.0, install AMICI > 0.30.1)
- v0.4.0: 490bbc348d57b7b03a91e09163ee8fec3fc84b9b (upgrade cyipopt to 1.6.1 to support ipopt max wall time)
- v0.3.0: cd04411dbce97e2b49be693e34524f0e38415ed9 (respect walltime limit by cma solver)
- v0.2.0: 408814c9ee711a7be12c2eee1fafd7b63cb32f5a (amici 0.30.1)
- v0.1.0: 8a781a4d6b8d6138b7158acc3af395db7c9514a8 (fixed versions)
