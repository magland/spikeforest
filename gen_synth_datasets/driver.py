import spikeinterface as si
import os, sys
import numpy as np

from mountainlab_pytools import mlproc as mlp
from mountainlab_pytools import mdaio

from gen_synth_datasets import gen_synth_datasets

import h5py
import json

def gen_datasets(duration,noise_level,num_units,label):
    K=20
    datasets=[]
    ds0=dict(
        duration=duration,
        noise_level=noise_level,
        K=num_units
    )
    num_datasets=10

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

    gen_synth_datasets(datasets,outdir=label)

def main():
    gen_datasets(600,10,10,'datasets_noise10_K10')
    gen_datasets(600,10,20,'datasets_noise10_K20')
    gen_datasets(600,20,10,'datasets_noise20_K10')
    gen_datasets(600,20,20,'datasets_noise20_K20')
    
if __name__ == "__main__":
    main()
