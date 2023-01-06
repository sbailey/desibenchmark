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

git clone https://github.com/sbailey/desibenchmark
cd desibenchmark
```

Or to use the latest pre-installed DESI code:
```
source /project/projectdirs/desi/software/desi_environment.sh master

git clone https://github.com/sbailey/desibenchmark
cd desibenchmark
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

Haswell on 19 nodes (32x2 cores) to process a single exposure of 30 frames:<BR/>
```
salloc -N 19 -t 1:00:00 -C haswell -q interactive
srun -n 600 -c 2 --cpu_bind=cores \
    ./desi-extract --night 20191001 --expid 3580 $SCRATCH/desi/benchmark/inputs/ $SCRATCH/temp $(date +%s)
```
Just r camera (10 frames; faster per-frame but packed less efficiently):
```
srun -N 7 -n 200 -c 2 --cpu_bind=cores \
    ./desi-extract --night 20191001 --expid 3580 --camera r $SCRATCH/desi/benchmark/inputs/ $SCRATCH/temp $(date +%s)
```

Haswell on 5 nodes (32x2 cores) <BR/>
~12.5 frames per node-hour
```
salloc -N 5 -t 2:00:00 -C haswell -q interactive
let n=32*$SLURM_JOB_NUM_NODES
srun -n $n -c 2 --cpu_bind=cores \
    ./desi-extract $SCRATCH/desi/benchmark/inputs/ $SCRATCH/temp $(date +%s)
```

KNL on 5 nodes (68x4 cores) <BR/>
~x.y frames per node-hour
```
salloc -N 5 -t 2:00:00 -C knl -q interactive
let n=68*$SLURM_JOB_NUM_NODES
srun -n $n -c 4 --cpu_bind=cores \
    ./desi-extract $SCRATCH/desi/benchmark/inputs/ $SCRATCH/temp $(date +%s)
```

Optional, to reduce the logging verbosity for large scale runs, change
the logging level before running `desi-extract`:
```
export DESI_LOGLEVEL=error
```

## Duplicating the dataset

For large runs, it is necessary to duplicate the provided 2019 dataset. You can use the
script `duplicate-pix-data.py` provided in this repo. 

### Examples

Creating dataset with default script values (years 2020-2023 and days 01-09).
The user however must always specify their workingdir.

```
python duplicate-pix-data.py --workingdir="/pscratch/sd/s/stephey/desi/benchmark-z-backup/pixtest"
```

Creating only one year

```
python duplicate-pix-data.py --workingdir="/pscratch/sd/s/stephey/desi/benchmark-z-backup/pixtest" --create-years 2020
```

Creating specific years and dates

```
python duplicate-pix-data.py --workingdir="/pscratch/sd/s/stephey/desi/benchmark-z-backup/pixtest" --create-years 2020 2021 --create-days 1 2
```


