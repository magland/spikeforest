import spikeinterface as si
import os, sys
import numpy as np

from mountainlab_pytools import mlproc as mlp
from mountainlab_pytools import mdaio

from gen_synth_datasets import gen_synth_datasets

import h5py
import json

def main():
    K=15
    datasets=[]
    ds0=dict(
        duration=600,
        noise_level=10,
        K=K
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

    gen_synth_datasets(datasets,outdir='datasets')
    
if __name__ == "__main__":
    main()