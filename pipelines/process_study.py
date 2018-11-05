import spikeinterface as si
import spikewidgets as sw
import spiketoolkit as st
import spikeforest as sf

import os, shutil

from kbucket import client as kb
from pairio import client as pa

class Study():
    def __init__(self,study_dir,study_name):
        #Define the spike sorters
        self._sorters=[]
        ms4_params=dict(
            detect_sign=-1,
            adjacency_radius=-1,
            detect_threshold=3
        )
        self._sorters.append(dict(
            processor=sf.MountainSort4,
            params=ms4_params
        ))

        # Define the datasets by reading the study directory
        self._datasets=[]
        dd=kb.readDir(study_dir)
        for dsname in dd['dirs']:
            dsdir='{}/{}'.format(study_dir,dsname)
            self._datasets.append(dict(
                name=dsname,
                dataset_dir=dsdir
            ))
            
    def clearResults(self):
        for dataset in self._datasets:
            for sorter in self._sorters:
                lock_obj=self._get_lock_object(sorter,dataset)
                pa.set(key=lock_obj,value=None)
                
    def getResults(self):
        results=[]
        for dataset in self._datasets:
            for sorter in self._sorters:
                lock_obj=self._get_lock_object(sorter,dataset)
                result=pa.get(key=lock_obj)
                results.append(result)
        return results
    
    def process(self):
        for dataset in self._datasets:
            for sorter in self._sorters:
                print ('SORTER: {}     DATASET: {}'.format(sorter['processor'].NAME,dataset['name']))
                lock_obj=self._get_lock_object(sorter,dataset)

                if pa.set(key=lock_obj,value='running',overwrite=False):
                    try:
                        print ('Running...')
                        result=sf.sortDataset(
                            sorter = sorter,
                            dataset = dataset
                        )
                        result['comparison_with_truth'] = sf.compareWithTruth(result)
                        result['summary'] = sf.summarizeSorting(result)
                        kb.saveObject(key=lock_obj,object=result)
                    except:
                        pa.set(key=lock_obj,value='error',overwrite=True)
                        raise
                else:
                    val0=pa.get(key=lock_obj)
                    if val0 == 'running':
                        print ('Skipping (result is running)...')
                    else:
                        print ('Skipping (result is locked)...')
    
    def _get_lock_object(self,sorter,dataset):
        return dict(
            dataset=dataset,
            sorter=dict(
                name=sorter['processor'].NAME,
                version=sorter['processor'].VERSION,
                params=sorter['params']
            )
        )

    