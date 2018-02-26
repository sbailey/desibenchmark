FROM ubuntu:16.04
MAINTAINER Rollin Thomas <rcthomas@lbl.gov>
WORKDIR /tmp

# Ubuntu packages

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

RUN \
    apt-get update          &&  \
    apt-get upgrade --yes   &&  \
    apt-get install --yes       \
        --no-install-recommends \
        build-essential         \
        bzip2                   \
        ca-certificates         \
        curl                    \
        gfortran                \
        git                     \
        subversion

# MPICH

RUN \
    curl --location --remote-name   \
        http://www.mpich.org/static/downloads/3.2/mpich-3.2.tar.gz  &&  \
    tar zxvf mpich-3.2.tar.gz   &&  \
    (cd mpich-3.2               &&  \
        ./configure             &&  \
        make -j 4               &&  \
        make install            &&  \
        make clean)             &&  \
    /sbin/ldconfig              &&  \
    rm -rf                          \
        mpich-3.2.tar.gz            \
        mpich-3.2

# Miniconda Python 3
# NOTE: How to source/conda activate in Dockerfile?

ENV CONDA_PREFIX /opt/anaconda3

ADD packages.txt /tmp/.
RUN \
    curl --location --output miniconda3.sh  \
        https://repo.continuum.io/miniconda/Miniconda3-4.4.10-Linux-x86_64.sh   &&  \
    /bin/bash miniconda3.sh -b -f -p $CONDA_PREFIX              &&  \
    $CONDA_PREFIX/bin/conda update --yes conda                  &&  \
    $CONDA_PREFIX/bin/conda install --yes --file=packages.txt   &&  \
    $CONDA_PREFIX/bin/conda clean --yes --all                   &&  \
    rm -rf packages.txt miniconda3.sh

ENV PATH $CONDA_PREFIX/bin:$PATH

# Define astropy cache and config in container

ENV XDG_CACHE_HOME=/srv/cache
RUN mkdir -p $XDG_CACHE_HOME/astropy

ENV XDG_CONFIG_HOME=/srv/config
RUN mkdir -p $XDG_CONFIG_HOME/astropy

RUN python -c "import astropy"

# mpi4py

RUN \
    curl --location --remote-name   \
        https://bitbucket.org/mpi4py/mpi4py/downloads/mpi4py-2.0.0.tar.gz   &&  \
    tar zxvf mpi4py-2.0.0.tar.gz    &&  \
    (cd mpi4py-2.0.0                &&  \
        python setup.py build       &&  \
        python setup.py install)    &&  \
    rm -rf                              \
        mpi4py-2.0.0.tar.gz             \
        mpi4py-2.0.0

# DESI packages

RUN \
    pip install speclite==0.7                                                       &&  \
    pip install git+https://github.com/desihub/desiutil.git@1.9.9#egg=desiutil      &&  \
    pip install git+https://github.com/desihub/specter.git@0.8.2#egg=specter        &&  \
    pip install git+https://github.com/desihub/desispec.git@0.18.0#egg=desispec     &&  \
    pip install git+https://github.com/desihub/desimodel.git@0.9.1#egg=desimodel

# Hack to get $DESIMODEL data somewhere; can we do better?
# (Probably create a desi Conda channel...)

ENV DESIMODEL $CONDA_PREFIX/desimodel

RUN \
    mkdir $DESIMODEL    &&  \
    python -c "import desimodel.install; desimodel.install.install('$DESIMODEL')"   &&  \
    mkdir -p $CONDA_PREFIX/etc/conda/activate.d     &&  \
    mkdir -p $CONDA_PREFIX/etc/conda/deactivate.d   &&  \
    echo "export DESIMODEL=$DESIMODEL" > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh &&  \
    echo "unset DESIMODEL" > $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh

WORKDIR /srv

# Add the code

ADD desi-extract /srv/desi-extract
