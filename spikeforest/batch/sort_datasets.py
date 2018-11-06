import spikeforest as sf
from kbucket import client as kb
from pairio import client as pa
import random
import string
import json
from copy import deepcopy

default_run_code='0'

def sort_datasets(*,study_name,run_code=default_run_code):
    tasks=load_tasks(study_name=study_name)
    for task in tasks:
        task.execute()
        
def clear_sorting_results(*,study_name,in_process_only):
    tasks=load_tasks(study_name=study_name)
    for task in tasks:
        task.clearResults(in_process_only=in_process_only)
        
def assemble_sorting_results(study_name,run_code=default_run_code):
    tasks = load_tasks(study_name=study_name,run_code=run_code)

    results = []
    for (i, task) in enumerate(tasks):
        print('Loading result for task {} of {}: {} {}/{}'.format(
            i + 1, len(tasks),
            task.sorter()['name'],
            task.dataset()['study'], 
            task.dataset()['name']
        ))
        result = task.loadResult()
        if not result:
            raise Exception('Unable to load result for task.')
        results.append(result)

    key = dict(name='spikeforest_sorting_results',study=study_name)
    print('Saving results to... key={}'.format(json.dumps(key)))
    obj = dict()
    obj['sorting_results'] = results
    kb.saveObject(obj, key=key)
    
def try_sort_dataset(*,study_name,dataset_name,sorter_name,run_code=default_run_code):
    tasks=load_tasks(study_name=study_name,run_code=run_code)
    for task in tasks:
        ds=task.dataset()
        so=task.sorter()
        if ds['study']==study_name:
            if ds['name']==dataset_name:
                if so['name']==sorter_name:
                    result=task.run()
                    return result
    raise Exception('Not found')

def load_sorters():
    sorters=[]

    ms4_p1=dict(
        detect_sign=-1,
        adjacency_radius=-1,
        detect_threshold=3
    )
    ms4_p2=dict(
        detect_sign=-1,
        adjacency_radius=-1,
        detect_threshold=5
    )
    
    sorters.append(dict(
        name='MountainSort4-p1',
        processor=sf.MountainSort4,
        params=ms4_p1
    ))
    sorters.append(dict(
        name='MountainSort4-p2',
        processor=sf.MountainSort4,
        params=ms4_p2
    ))
    return sorters

def sort_dataset(sorter,dataset):
    ret=dict()
    ret['sorter']=dict(
        name=sorter['name'],
        processor_name=sorter['processor'].NAME,
        processor_version=sorter['processor'].VERSION,
        sorting_params=sorter['params']
    )
    ret['dataset']=deepcopy(dataset)
    result=sf.sortDataset(
        sorter = sorter,
        dataset = dataset
    )
    result['comparison_with_truth'] = sf.compareWithTruth(result)
    result['summary'] = sf.summarizeSorting(result)
    ret['result']=result
    return ret

class SortDatasetTask():
    def __init__(self,key,dataset,sorter):
        self._key=key
        self._dataset=dataset
        self._sorter=sorter
        self._code=''.join(random.choice(string.ascii_uppercase) for x in range(10))
    
    def dataset(self):
        return self._dataset

    def sorter(self):
        return self._sorter

    def clearResults(self,*,in_process_only):
        val=pa.get(self._key)
        if val:
            if (not in_process_only) or (val.startswith('in-process')) or (val.startswith('error')):
                print('Clearing results for: '+self._key['dataset_name'])
                pa.set(key=self._key,value=None)

    def execute(self):
        print(self._sorter['name']+' '+self._dataset['name'])
        val=pa.get(self._key)
        if val:
            if val.startswith('in-process'):
                print('In progress, skipping...')
            else:
                print('Completed, skipping...')
                return
        if not pa.set(self._key,'in-process-'+self._code,overwrite=False):
            print('Problem setting in-process value skipping...')
            return
        try:
            result=self.run()
        except:
            if pa.get(self._key)=='in-process-'+self._code:
                pa.set(self._key,'error')
            else:
                print('Unexpected: not setting error value because existing value does not match')
            raise
        if pa.get(self._key)=='in-process-'+self._code:
            print('Saving result object.')
            kb.saveObject(key=self._key,object=result)
        else:
            print('Unexpected: not setting result because existing value does not match.')

    def loadResult(self):
        val=pa.get(self._key)
        if val:
            if val.startswith('in-process'):
                print('Unable to load result... it is in process.')
                return None
            else:
                return kb.loadObject(key=self._key)
        else:
            return None

    def run(self):
        return sort_dataset(self._sorter, self._dataset)
    
def load_tasks(study_name,run_code=default_run_code):
    obj=kb.loadObject(
        key=dict(name='spikeforest_studies_processed'),
        share_ids=['spikeforest.spikeforest1']
    )
    
    datasets=obj['datasets']
    
    tasks=[]
    sorters=load_sorters()
    for ds in datasets:
        if ds['study']==study_name:
            for sorter in sorters:
                key=dict(
                    script='sort_datasets',
                    study_name=ds['study'],
                    dataset_name=ds['name'],
                    sorter_name=sorter['name'],
                    run_code=run_code
                )
                task=SortDatasetTask(dataset=ds,sorter=sorter,key=key)
                tasks.append(task)
    return tasks

