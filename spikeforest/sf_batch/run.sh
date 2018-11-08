#!/bin/bash

set -e

# Set number of cpu's to use for spike sorting
export NUM_WORKERS=2
export MKL_NUM_THREADS=$NUM_WORKERS
export NUMEXPR_NUM_THREADS=$NUM_WORKERS
export OMP_NUM_THREADS=$NUM_WORKERS

config=$1

python driver_sf_batch.py prepare $config
$parellel_prefix python driver_sf_batch.py run $config
#srun -c 2 -n 40 python driver_sf_batch.py run $config
python driver_sf_batch.py assemble $config
