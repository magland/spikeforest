import spikeinterface as si
import os, sys
import numpy as np

from mountainlab_pytools import mlproc as mlp
from mountainlab_pytools import mdaio
from gen_synth_datasets import gen_synth_datasets

import h5py
import json

def gen_datasets(*,duration=600,noise_level,num_units,label,num_channels=4,num_datasets=10):
    datasets=[]
    ds0=dict(
        duration=duration,
        noise_level=noise_level,
        K=num_units
    )

    for j in range(1,num_datasets+1):
        ds=dict(        
            name='{}_synth'.format('{0:03d}'.format(j)),
            seed=j
        )
        for key in ds0:
            ds[key]=ds0[key]
        datasets.append(ds)

    print('DATASETS:')
    print([ds['name'] for ds in datasets])

    gen_synth_datasets(datasets,outdir=label,num_channels=num_channels)

def main():
    #gen_datasets(noise_level=10, num_units=10, label='datasets_noise10_K10_C4', num_channels=4, num_datasets=1)
    
    gen_datasets(noise_level=10, num_units=10, label='datasets_noise10_K10_C4', num_channels=4)
    gen_datasets(noise_level=10, num_units=20, label='datasets_noise10_K20_C4', num_channels=4)
    gen_datasets(noise_level=20, num_units=10, label='datasets_noise20_K10_C4', num_channels=4)
    gen_datasets(noise_level=20, num_units=20, label='datasets_noise20_K20_C4', num_channels=4)

    gen_datasets(noise_level=10, num_units=10, label='datasets_noise10_K10_C8', num_channels=8)
    gen_datasets(noise_level=10, num_units=20, label='datasets_noise10_K20_C8', num_channels=8)
    gen_datasets(noise_level=20, num_units=10, label='datasets_noise20_K10_C8', num_channels=8)
    gen_datasets(noise_level=20, num_units=20, label='datasets_noise20_K20_C8', num_channels=8)
    
    
if __name__ == "__main__":
    main()
