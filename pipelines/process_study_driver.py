#!/usr/bin/env python

import os

from kbucket import client as kb
from pairio import client as pa
from process_study import process_study

def main():
    # Select the study
    study_dir='kbucket://b5ecdf1474c5/spikeforest/gen_synth_datasets/datasets_noise10_K20'
    study_name='synth_jfm_noise10_K20'
    num_datasets=None

    # Specify whether we want to read/write remotely
    read_local=False
    write_local=True
    read_remote=True
    write_remote=True
    load_local=True
    load_remote=True
    save_remote=True

    # The following can be set for saving results
    PAIRIO_USER='spikeforest'
    KBUCKET_SHARE_ID='magland.spikeforest'
    
    pa.setConfig(read_local=read_local,write_local=write_local,read_remote=read_remote,write_remote=write_remote)
    pa.setConfig(collections=[PAIRIO_USER])
    
    kb.setConfig(load_local=load_local,load_remote=load_remote,save_remote=save_remote)
    kb.setConfig(share_ids=[KBUCKET_SHARE_ID])
    
    if write_remote:
        PAIRIO_TOKEN=os.getenv('SPIKEFOREST_PAIRIO_TOKEN')
        pa.setConfig(user=PAIRIO_USER,token=PAIRIO_TOKEN)
        
    if save_remote:
        KBUCKET_UPLOAD_TOKEN=os.getenv('SPIKEFOREST_KBUCKET_TOKEN')
        kb.setConfig(upload_share_id=KBUCKET_SHARE_ID,upload_token=KBUCKET_UPLOAD_TOKEN)
        kb.testSaveRemote()

    process_study(study_dir=study_dir,study_name=study_name,num_datasets=num_datasets)

if __name__== "__main__":
  main()