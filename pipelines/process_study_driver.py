#!/usr/bin/env python

import os
import sys
import argparse

from kbucket import client as kb
from pairio import client as pa
from process_study import Study

def main(*,command,mode='local'):
    # Select the study
    study_dir='kbucket://b5ecdf1474c5/spikeforest/gen_synth_datasets/datasets_noise10_K20'
    study_name='synth_jfm_noise10_K20'
    
    # The following are relevant when mode='remote'
    PAIRIO_USER='spikeforest'
    KBUCKET_SHARE_ID='magland.spikeforest'

    # Specify whether we want to read/write remotely
    if mode=='local':
        read_local=True; write_local=True; read_remote=False ;write_remote=False
        load_local=True; load_remote=True; save_remote=False
    elif mode=='remote':
        read_local=False; write_local=False; read_remote=True; write_remote=True
        load_local=False; load_remote=True; save_remote=True
        if write_remote:
            PAIRIO_TOKEN=os.getenv('SPIKEFOREST_PAIRIO_TOKEN')
            pa.setConfig(user=PAIRIO_USER,token=PAIRIO_TOKEN)
        if save_remote:
            KBUCKET_UPLOAD_TOKEN=os.getenv('SPIKEFOREST_KBUCKET_TOKEN')
            kb.setConfig(upload_share_id=KBUCKET_SHARE_ID,upload_token=KBUCKET_UPLOAD_TOKEN)
            kb.testSaveRemote()
    else:
        raise Exception('Missing or invalid mode:',mode)
    
    pa.setConfig(read_local=read_local,write_local=write_local,read_remote=read_remote,write_remote=write_remote)
    pa.setConfig(collections=[PAIRIO_USER])
    
    kb.setConfig(load_local=load_local,load_remote=load_remote,save_remote=save_remote)
    kb.setConfig(share_ids=[KBUCKET_SHARE_ID])
    
    study=Study(study_dir=study_dir,study_name=study_name)
    
    if command=='process':
        study.process()
    elif command=='clear':
        study.clearResults()
    elif command=='save':
        results=study.getResults()
        print ('Saving {} results...'.format(len(results)))
        key=dict(
            name='spikeforest_results',
            study_name=study_name
        )
        kb.saveObject(key=key,object=results)
        print ('Saved under key:')
        print (key)
    else:
        raise Exception('Unrecognized command: '+command)

def print_usage():
    print ('Usage:')
    print ('./process_study_driver.py process')
    print ('./process_study_driver.py save')
    print ('./process_study_driver.py clear')
        
if __name__== "__main__":
    parser = argparse.ArgumentParser(description = 'Process a spikeforest study')
    parser.add_argument('command', help='process, save, or clear')
    parser.add_argument('--mode', help='local or remote')
  
    args = parser.parse_args()
    
    main(
        command=args.command,
        mode=args.mode
    )
