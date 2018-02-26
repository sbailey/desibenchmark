# desibenchmark

DESI benchmark code for evaluating performance on a supercomputer

Stephen Bailey & Rollin Thomas
Lawrence Berkeley National Lab
January 2018

## Overview

blah blah

## Installation

To create an environment to run these scripts at NERSC:
```
#- Create basic python environment
curl -o miniconda3.sh \
    https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash miniconda3.sh -b -f -p env
rm -rf miniconda3.sh
source env/bin/activate
conda update --yes conda
conda install --yes --file=packages.txt

#- Add DESI-specific code
pip install speclite==0.7
pip install git+https://github.com/desihub/desiutil.git@1.9.9#egg=desiutil
pip install git+https://github.com/desihub/specter.git@0.8.2#egg=specter
pip install git+https://github.com/desihub/desispec.git@0.18.0#egg=desispec
pip install git+https://github.com/desihub/desimodel.git@0.9.1#egg=desimodel

#- Build mpi4py using Cray compiler wrappers
wget https://bitbucket.org/mpi4py/mpi4py/downloads/mpi4py-2.0.0.tar.gz
tar zxvf mpi4py-2.0.0.tar.gz
(cd mpi4py-2.0.0                                &&  \
    python setup.py build --mpicc=$(which cc)   &&  \
    python setup.py install)                    &&  \
rm -rf mpi4py-2.0.0 mpi4py-2.0.0.tar.gz

#- This is a hack to get $DESIMODEL data somewhere; can we do better?
export DESIMODEL=$CONDA_PREFIX/desimodel
mkdir $DESIMODEL
python -c "import desimodel.install; desimodel.install.install('$DESIMODEL')"
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
mkdir -p $CONDA_PREFIX/etc/conda/deactivate.d
echo "export DESIMODEL=$DESIMODEL" > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo "unset DESIMODEL" > $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
```

To do:
  * docker-ize

### Test installation

Initial command to test if the environment worked:
```
salloc -N 1 -t 1:00:00 -C haswell -q interactive

datadir=/global/cscratch1/sd/sjbailey/desi/benchmark/inputs/
time srun -n 20 --cpu_bind=cores \
     desi_extract_spectra --mpi \
        -i $datadir/pix/20191001/pix-r1-00003580.fits \
        -f $datadir/pix/20191001/fibermap-00003580.fits \
        -p $datadir/psf/20191001/psfnight-r1.fits \
        -o $SCRATCH/frame-r1-00003580.fits
```
Should take 5-6 minutes and create $SCRATCH/frame-r1-00003580.fits.

## Running the benchmark

Haswell on 5 nodes (32x2 cores) <BR/>
~12.5 frames per node-hour
```
salloc -N 5 -t 2:00:00 -C haswell -q interactive
let n=32*$SLURM_JOB_NUM_NODES
srun -n $n -c 2 --cpu_bind=cores ./desi-extract -i $SCRATCH/desi/benchmark/inputs/ -o $SCRATCH/temp
```

KNL on 5 nodes (68x4 cores) <BR/>
~x.y frames per node-hour
```
salloc -N 5 -t 2:00:00 -C knl -q interactive
let n=68*$SLURM_JOB_NUM_NODES
srun -n $n -c 4 --cpu_bind=cores ./desi-extract -i $SCRATCH/desi/benchmark/inputs/ -o $SCRATCH/temp
```

Optional, to reduce the logging verbosity for large scale runs, change
the logging level before running `desi-extract`:
```
export DESI_LOGLEVEL=error
```

