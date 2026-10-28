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

# Image used for the Marvin runs: the v0.3.0 recipe of this repository with
# the pyPESTO pin set to branch minimize_ms_single_file (commit a9093c2), as
# found in the image. The pin line is the only difference to v0.3.0.
RUN pip3 install --upgrade --force-reinstall git+https://github.com/stephanmg/pyPESTO.git@a9093c221d9a81c2b09784b6e21304fb81397dba

# for later releases pull either from pypesto after mimimize branch has been merged, or pull from benchmark branch after minimize_ms branch has been merged there
# RUN pip3 install --upgrade --force-reinstall git+https://github.com/stephanmg/pyPESTO.git@minimize

RUN pip3 freeze > requirements.txt
