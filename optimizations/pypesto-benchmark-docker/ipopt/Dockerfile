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
    python3.12-venv \
    swig \
    libopenmpi-dev \
    && ln -sf /usr/bin/swig4.0 /usr/bin/swig

ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get install curl pkg-config -y
RUN apt-get install coinor-libipopt-dev -y
RUN apt-get install libmumps-seq-dev -y
RUN mkdir /opt/src/ && cd /opt/src/ && git clone https://github.com/coin-or/Ipopt.git
RUN cd /opt/src/Ipopt && git checkout stable/3.14 
ENV IPOPT_DIR=/opt/ipopt/
ENV LD_LIBRARY_PATH=/opt/ipopt/lib:$LD_LIBRARY_PATH
ENV PKG_CONFIG_PATH=/opt/ipopt/lib/pkgconfig:$PKG_CONFIG_PATH
RUN mkdir /opt/src/Ipopt/build && cd /opt/src/Ipopt/build &&  ../configure --with-mumps-cflags=-I/usr/include/mumps_seq  --prefix=/opt/ipopt/ --with-mumps --enable-shared --with-mumps-lflags="-ldmumps_seq" && make -j4 && make install
RUN pkg-config --modversion ipopt
RUN pip3 install --no-binary=cyipopt cyipopt --force


ENV AMICI_CXXFLAGS -fopenmp
ENV AMICI_LDFLAGS -fopenmp
#
RUN pip3 install python-libsbml mpi4py amici==0.30.1 && python3 -m amici

RUN pip3 install pypesto==0.5.4 fides==0.7.8 pyswarm==0.6 nlopt==2.8.0 scipy==1.14.1 cma==4.0.0 petab==0.5.0 pandas==2.2.3

RUN pip3 install --upgrade --force-reinstall git+https://github.com/stephanmg/pyPESTO.git@minimize_ms_single_file_additions_unified_time_interface

RUN pip3 install fides==0.7.8 pyswarm==0.6 nlopt==2.8.0 scipy==1.14.1 cma==4.0.0 petab==0.5.0 pandas==2.2.3 mpi4py==4.0.3
