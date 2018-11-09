#!/usr/bin/env python

import argparse
import spikeforest as sf
import os
import json

def read_json_file(fname):
    with open(fname) as f:
        return json.load(f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Sort the SpikeForest recordings')
    parser.add_argument('command',help='clear, prepare, run, assemble')
    parser.add_argument('config_file',help='Name of config .json file')
    args = parser.parse_args()

    spikeforest_password=os.environ.get('SPIKEFOREST_PASSWORD','')
    if not spikeforest_password:
      raise Exception('Environment variable not set: SPIKEFOREST_PASSWORD')

    command=args.command
    config_fname=args.config_file
    
    config=read_json_file(config_fname)
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