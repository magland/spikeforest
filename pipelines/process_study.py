import spikeinterface as si
import spikewidgets as sw
import spiketoolkit as st
import spikeforest as sf

import os, shutil

from kbucket import client as kb
from pairio import client as pa

def process_study(*,study_dir,study_name,num_datasets=None):
    #Define the spike sorters
    sorters=[]
    ms4_params=dict(
        detect_sign=-1,
        adjacency_radius=-1,
        detect_threshold=3
    )
    sorters.append(dict(
        name='MountainSort4',
        processor=sf.MountainSort4,
        params=ms4_params
    ))
    
    # Define the datasets by reading the study directory
    datasets=[]
    dd=kb.readDir(study_dir)
    for dsname in dd['dirs']:
        dsdir='{}/{}'.format(study_dir,dsname)
        datasets.append(dict(
            name=dsname,
            dataset_dir=dsdir
        ))
    if num_datasets is not None:
        datasets=datasets[0:num_datasets]

    # Run the pipeline
    results=[]
    for dataset in datasets:
        for sorter in sorters:
            print ('SORTER: {}     DATASET: {}'.format(sorter['name'],dataset['name']))
            result=sf.sortDataset(
                sorter=sorter,
                dataset=dataset,
                _force_run=False
            )
            result['comparison_with_truth']=sf.compareWithTruth(result)
            result['summary']=sf.summarizeSorting(result)
            results.append(result)
        #break
    print ('Saving results object...')
    
    # Save the results
    kb.saveObject(results,key=dict(name='spikeforest_results',study_name=study_name))
    print ('Done.')