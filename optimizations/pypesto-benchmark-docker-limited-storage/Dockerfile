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

RUN  pip3 install python-libsbml>=5.17.0  \
    && pip3 install mpi4py amici==0.30.1  \
    && python3 -m amici

RUN pip3 install pypesto==0.5.4 fides==0.7.8 pyswarm==0.6 nlopt==2.8.0 scipy==1.14.1 cma==4.0.0 petab==0.5.0

# for v0.1.0 (fixed versions and ipopt) and v0.2.0 (amici 0.30.1) - corresponds to pypesto 0.5.4 release with additional functionality for the benchmark (benchmark branch)
# RUN pip3 install --upgrade --force-reinstall git+https://github.com/stephanmg/pyPESTO.git@4999790468e983e56f275b23fb675e63809163ac

# for v0.3.0 (respecting walltime limit cma) - corresponds to pypesto 0.5.4 release with additional functionality for the benchmark and fixes (benchmark_fix branch)
#RUN pip3 install --upgrade --force-reinstall git+https://github.com/stephanmg/pyPESTO.git@benchmark_fix

# for later releases pull either from pypesto after benchmark_fix branch has been merged, or pull from benchmark branch after benchmark_fix branch has been merged there
# RUN pip3 install --upgrade --force-reinstall git+https://github.com/stephanmg/pyPESTO.git@benchmark

# for v0.4.0 (setting time limits, adding end time stamp to the .h5 file)
RUN pip3 install --upgrade --force-reinstall git+https://github.com/stephanmg/pyPESTO.git@benchmark_fix_new_time_limits_and_time_stamp

RUN pip3 freeze > requirements.txt
