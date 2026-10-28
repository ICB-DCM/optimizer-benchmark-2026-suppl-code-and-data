# pypesto-benchmark-docker-limited-storage

## Build
`docker build -t pypesto_benchmark_docker_limited_storage .`

## Export for apptainer

`docker save -o pypesto_benchmark_docker_limited_storage.tar pypesto_benchmark_docker_limited_storage`

## Convert to apptainer

`apptainer build pypesto_benchmark_docker_limited_storage.sif docker-archive:://pypesto_benchmark_docker_limited_storage.tar`

## Installed package versions

The [`Dockerfile`](Dockerfile) in this directory is the recipe of the image
tagged `v0.3.0` that was used on FinisTerrae III;
[`requirements.txt`](requirements.txt) is its `pip freeze` output
(Ubuntu 24.04, Python 3.12, Ipopt 3.11.9 from the Ubuntu package).
The image tagged `v0.2.0` has identical versions of all
relevant packages and differs only in the pyPESTO fork commit
(`4999790` instead of `0faf8d2`, see [`../README.md`](../README.md)).
See the table in [`../README.md`](../README.md) for the package versions
relevant for the benchmark.
