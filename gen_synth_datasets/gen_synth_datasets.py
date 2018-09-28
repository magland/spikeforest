from mountainlab_pytools import mlproc as mlp
from mountainlab_pytools import mdaio
import spikeinterface as si
import os, sys
import numpy as np
import json

def gen_synth_datasets(datasets,*,tmpdir,outdir):
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    for ds in datasets:
        ds_name=ds['name']
        print(ds_name)
        spiketrains_fname=tmpdir+'/spiketrains_{}.npy'.format(ds_name)
        recording_fname=tmpdir+'/recording_{}.h5'.format(ds_name)
        gen_spiketrains(
            spiketrains_fname,
            dict(
                duration=ds['duration'],
                n_exc=ds['n_exc'],
                n_inh=ds['n_inh'],
                f_exc=ds['f_exc'],
                f_inh=ds['f_inh'],
                min_rate=ds['min_rate'],
                st_exc=ds['st_exc'],
                st_inh=ds['st_inh'],
            )
        )
        gen_recording(
            ds['templates'],
            spiketrains_fname,
            recording_fname,
            dict(
                noise_level=ds['noise_level'],
                min_dist=ds['min_dist'],
                seed=ds['seed']
            )
        )
        mlp.runPipeline()
        IX=si.MEArecInputExtractor(recording_file=recording_fname)
        OX=si.MEArecOutputExtractor(recording_file=recording_fname)
        if ds['channel_ids'] is not None:
            IX=si.SubInputExtractor(IX,channel_ids=ds['channel_ids'])
        print('Writing in mda format...')
        si.MdaInputExtractor.writeDataset(IX,outdir+'/{}'.format(ds_name))
        si.MdaOutputExtractor.writeFirings(OX,outdir+'/{}/firings_true.mda'.format(ds_name))
    print('Done.')
        
# Wrappers to MEArec processors
def gen_spiketrains(spiketrains_out,params):
    mlp.addProcess(
        'mearec.gen_spiketrains',
        inputs=dict(
        ),
        outputs=dict(
            spiketrains_out=spiketrains_out
        ),
        parameters=params,
        opts={}
    )
    
def gen_recording(templates,spiketrains,recording_out,params):
    #ml_mearec.gen_recording()(templates=templates,spiketrains=spiketrains,recording_out=recording_out,**params)
    mlp.addProcess(
        'mearec.gen_recording',
        inputs=dict(
            templates=templates,
            spiketrains=spiketrains
        ),
        outputs=dict(
            recording_out=recording_out
        ),
        parameters=params,
        opts={}
    )