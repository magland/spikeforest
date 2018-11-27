from mountainlab_pytools import mlproc as mlp
from mountainlab_pytools import mdaio
import spikeextractors as si
import os, sys
import numpy as np
import json
from synthesize_timeseries import synthesize_timeseries
from synthesize_random_firings import synthesize_random_firings
from synthesize_random_waveforms import synthesize_random_waveforms
import h5py

def gen_synth_datasets(datasets,*,outdir):
    samplerate=32000
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    num_channels=4
    upsamplefac=13
    samplerate=30000
    for ds in datasets:
        ds_name=ds['name']
        print(ds_name)
        K=ds['K']
        duration=ds['duration']
        noise_level=ds['noise_level']
        waveforms,geom=synthesize_random_waveforms(K=K,M=num_channels,average_peak_amplitude=-100,upsamplefac=upsamplefac)
        times,labels=synthesize_random_firings(K=K,duration=duration,samplerate=samplerate)
        labels=labels.astype(np.int64)
        OX=si.NumpyOutputExtractor()
        OX.setTimesLabels(times,labels)
        X=synthesize_timeseries(
            output_extractor=OX,
            waveforms=waveforms,
            noise_level=noise_level,
            samplerate=samplerate,
            duration=duration,
            waveform_upsamplefac=upsamplefac
        )
        IX=si.NumpyInputExtractor(timeseries=X,samplerate=samplerate,geom=geom)
        si.MdaInputExtractor.writeDataset(IX,outdir+'/{}'.format(ds_name))
        si.MdaOutputExtractor.writeFirings(OX,outdir+'/{}/firings_true.mda'.format(ds_name))
    print('Done.')