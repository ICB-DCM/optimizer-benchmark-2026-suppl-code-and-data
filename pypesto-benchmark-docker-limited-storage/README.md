# pypesto-benchmark-docker-limited-storage
[![Build and Push Docker Image](https://github.com/stephanmg/pypesto-benchmark-docker-limited-storage/actions/workflows/push_docker.yaml/badge.svg)](https://github.com/stephanmg/pypesto-benchmark-docker-limited-storage/actions/workflows/push_docker.yaml)

## Build
`docker build -t pypesto_benchmark_docker_limited_storage .`

## Export for apptainer

`docker save -o pypesto_benchmark_docker_limited_storage.tar pypesto_benchmark_docker_limited_storage`

## Convert to apptainer

`apptainer build pypesto_benchmark_docker_limited_storage.sif docker-archive:://pypesto_benchmark_docker_limited_storage.tar`


## Copy requirements
Use `docker ps` to find container ID, then call:
`docker cp CONTAINER_ID:/requirements.txt .`

The requirements file `requirements.txt` is automatically generated from the latest tagged release (currently v0.3.0).

## Releases

`latest` corresponds currently to `v0.4.0` and considered latest stable/tested version.

- v0.4.0 (setting time limits, adding end time stamp to the .h5 file)
- v0.3.0: 7547ba1d0893caa85dc4b0ef332a3a37de77bcf7 (respect walltime limit by cma solver)
- v0.2.0: 4fbe1b50ef6972437155082885d60d93f142334c (amici 0.30.1)
- v0.1.0: 711970a52794a268cdf4769041d6cb0f95b9fd73 (fixed versions)
