#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import spikeinterface as si
import spikewidgets as sw
import spiketoolkit as st
import spikeforest as sf

import os, shutil

from kbucket import client as kb
from pairio import client as pa


# In[ ]:


# Select the study
study_dir='kbucket://b5ecdf1474c5/spikeforest/gen_synth_datasets/datasets_noise10_K20'
study_name='synth_jfm_noise10_K20'
num_datasets=None

# Specify whether we want to do this offline
offline=False

# The following can be set for saving results
PAIRIO_USER='spikeforest'
PAIRIO_TOKEN=os.getenv('SPIKEFOREST_PAIRIO_TOKEN')
KBUCKET_SHARE_ID='magland.spikeforest'
KBUCKET_UPLOAD_TOKEN=os.getenv('SPIKEFOREST_KBUCKET_TOKEN')


# In[ ]:


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


# In[ ]:


# Configure pairio and kbucket

if not offline:
    # writing to pairio
    if PAIRIO_USER:
        pa.setConfig(user=PAIRIO_USER,token=PAIRIO_TOKEN)
                     
    # writing to kbucket              
    if KBUCKET_UPLOAD_TOKEN:
        print('Setting upload server to {}'.format(KBUCKET_SHARE_ID))
        kb.setConfig(upload_share_id=KBUCKET_SHARE_ID,upload_token=KBUCKET_UPLOAD_TOKEN)
        kb.testUpload()
        
    # reading from pairio and kbucket
    pa.setConfig(collections=[PAIRIO_USER])
    kb.setConfig(share_ids=[KBUCKET_UPLOAD_TOKEN])


# In[ ]:


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


# In[ ]:


results=[]
for dataset in datasets:
    for sorter in sorters:
        print('SORTER: {}     DATASET: {}'.format(sorter['name'],dataset['name']))
        result=sf.sortDataset(
            sorter=sorter,
            dataset=dataset,
            _force_run=False
        )
        result['comparison_with_truth']=sf.compareWithTruth(result)
        result['summary']=sf.summarizeSorting(result)
        results.append(result)
    #break
print('Saving results object...')
kb.saveObject(results,key=dict(name='spikeforest_results',study_name=study_name))
print('Done.')


# In[ ]:


results=kb.loadObject(key=dict(name='spikeforest_results',study_name=study_name))


# In[ ]:


kb.findFile(key=dict(name='spikeforest_results',study_name=study_name),remote_only=True)


# In[ ]:


results[0]


# In[ ]:


from IPython.display import Image
Image(kb.realizeFile(results[0]['summary']['plots']['unit_waveforms']),format='jpeg')


# In[ ]:


import json
def _read_text_file(path):
  with open(path) as f:
    return json.load(f)
html=_read_text_file(kb.realizeFile(results[0]['comparison_with_truth']['html']))
from IPython.display import HTML
display(HTML(html))


# In[ ]:




