# pypesto-benchmark-docker

## Build
`docker build -t pypesto_benchmark_docker .`

## Export for apptainer

`docker save -o pypesto_benchmark_docker.tar pypesto_benchmark_docker`

## Convert to apptainer

`apptainer build pypesto_benchmark_docker.sif docker-archive:://pypesto_benchmark_docker.tar`

## Image versions

The image used for the Marvin runs is based on Ubuntu 24.04 with
Python 3.12 and Ipopt 3.11.9 from the Ubuntu package.
The [`Dockerfile`](Dockerfile) in this directory is the `v0.3.0` recipe of
this repository with the pyPESTO pin set to the commit found in the image
(`a9093c2`, branch `minimize_ms_single_file`).
All package versions pinned in that recipe match the image, and the
`pip3 freeze` step of the recipe produced the `/requirements.txt` found in
the image.
Its installed packages are listed in [`requirements.txt`](requirements.txt)
(`pip freeze` output; the `pypesto` line was added based on the
installation metadata of the package in the image).
[`ipopt/Dockerfile`](ipopt/Dockerfile) is the recipe of the later image that
was used for the repeated runs (see [`../README.md`](../README.md)).

See [`../README.md`](../README.md) for a table of the relevant package
versions and for the modified pyPESTO versions.
