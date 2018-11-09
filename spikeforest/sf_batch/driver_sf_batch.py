#!/usr/bin/env python

import argparse
import spikeforest as sf
from kbucket import client as kb
import os
import json

def read_json_file(fname):
    with open(fname) as f:
        return json.load(f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Sort the SpikeForest recordings')
    parser.add_argument('command',help='clear, prepare, run, assemble')
    parser.add_argument('batch_name',help='Name of the batch')
    args = parser.parse_args()
    
    print('Loading batch configs...')
    sf.kbucketConfigRemote(share_id='spikeforest.spikeforest1',write=False)
    obj=kb.loadObject(key=dict(name='spikeforest_batches'))
    if not obj:
      raise Exception('Unable to find spikeforest_batches object.')
    batch_configs=obj['batches']
    print('Loaded {} configs...'.format(len(batch_configs)))
    
    config=None
    for bc in batch_configs:
      if bc['name']==args.batch_name:
        config=bc
    if not config:
      raise Exception('Unable to find batch config with name: '+args.batch_name)
    
    spikeforest_password=os.environ.get('SPIKEFOREST_PASSWORD','')
    if not spikeforest_password:
      raise Exception('Environment variable not set: SPIKEFOREST_PASSWORD')

    command=args.command
    if command=='clear':
      sf.sf_batch.sf_batch_prepare(config,clear_all=True)
    elif command=='prepare':
      sf.sf_batch.sf_batch_prepare(config)
    elif command=='run':
      sf.sf_batch.sf_batch_run(config)
    elif command=='assemble':
      sf.sf_batch.sf_batch_assemble(config)
    else:
      raise Exception('Unrecognized command: '+command)