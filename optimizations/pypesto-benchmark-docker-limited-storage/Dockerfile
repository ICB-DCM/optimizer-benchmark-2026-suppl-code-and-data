FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin

RUN apt-get update \
    && apt-get install -y \
    cmake \
    wget \
    g++ \
    git \
    libatlas-base-dev \
    libhdf5-serial-dev \
    python-is-python3 \
    python3 \
    python3-dev \
    python3-pip \
    swig \
    libopenmpi-dev \
    python3.12-venv \
    && ln -sf /usr/bin/swig4.0 /usr/bin/swig

ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get install curl pkg-config -y
RUN apt install coinor-libipopt-dev -y
RUN apt install coinor-libipopt1v5 -y

RUN pip3 install cyipopt==1.5.0

ENV AMICI_CXXFLAGS -fopenmp
ENV AMICI_LDFLAGS -fopenmp

RUN  pip3 install python-libsbml>=5.17.0  \
    && pip3 install mpi4py amici==0.30.1  \
    && python3 -m amici

RUN pip3 install pypesto==0.5.4 fides==0.7.8 pyswarm==0.6 nlopt==2.8.0 scipy==1.14.1 cma==4.0.0 petab==0.5.0

# for v0.1.0 (fixed versions and ipopt) and v0.2.0 (amici 0.30.1) - corresponds to pypesto 0.5.4 release with additional functionality for the benchmark (benchmark branch)
# RUN pip3 install --upgrade --force-reinstall git+https://github.com/stephanmg/pyPESTO.git@4999790468e983e56f275b23fb675e63809163ac

# for v0.3.0 (respecting walltime limit cma) - corresponds to pypesto 0.5.4 release with additional functionality for the benchmark and fixes (benchmark_fix branch)
RUN pip3 install --upgrade --force-reinstall git+https://github.com/stephanmg/pyPESTO.git@benchmark_fix

# for later releases pull either from pypesto after benchmark_fix branch has been merged, or pull from benchmark branch after benchmark_fix branch has been merged there
# RUN pip3 install --upgrade --force-reinstall git+https://github.com/stephanmg/pyPESTO.git@benchmark

RUN pip3 freeze > requirements.txt
