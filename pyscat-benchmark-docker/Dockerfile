FROM ubuntu:25.04

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
    python3.13-venv \
    swig \
    libopenmpi-dev 

ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get install curl pkg-config -y
RUN apt install coinor-libipopt-dev -y
RUN apt install coinor-libipopt3 -y
   
RUN pip3 install cyipopt==1.5.0

ENV AMICI_CXXFLAGS -fopenmp
ENV AMICI_LDFLAGS -fopenmp

RUN pip3 install python-libsbml mpi4py amici==0.31.2 && python3 -m amici

RUN pip3 install pypesto==0.5.4 fides==0.7.8 pyswarm==0.6 nlopt==2.8.0 scipy cma==4.0.0 petab==0.5.0 pandas==2.3.0 pyscat

RUN pip3 install --upgrade --force-reinstall "git+https://github.com/stephanmg/pyPESTO.git@minimize_ms_single_file_additions_unified_time_interface#egg=pypesto"
RUN pip3 install --upgrade --force-reinstall "git+https://github.com/ICB-DCM/pyscat.git@03f949dee646f3a54db3a5813c02053e06044c6b#egg=pyscat"
RUN pip3 install --upgrade --force-reinstall "git+https://github.com/Benchmarking-Initiative/Benchmark-Models-PEtab.git@master#subdirectory=src/python"

RUN pip3 freeze > requirements.txt
