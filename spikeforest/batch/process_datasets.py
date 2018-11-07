#!/usr/bin/env python

from kbucket import client as kb
from pairio import client as pa
import spikeforest as sf
import spikeinterface as si
import spikewidgets as sw
import spiketoolkit as st
from copy import deepcopy
import json
import mlprocessors as mlpr
from matplotlib import pyplot as plt
from PIL import Image
import os
import random
import string

default_run_code='0'

def clear_dataset_results(in_process_only,run_code=default_run_code):
  print('Loading tasks...')
  tasks=load_tasks(run_code=run_code)

  print('Checking tasks...')
  for i,task in enumerate(tasks):
    task.clearResults(in_process_only=in_process_only)
  
  print('Done.')

def download_datasets(run_code=default_run_code):
  tasks=load_tasks(run_code=run_code)

  for i,task in enumerate(tasks):
    ds=task.dataset()
    print('Download task {} of {}: {}'.format(i+1,len(tasks),ds['name']))
    dsdir=ds['directory']
    kb.realizeFile(dsdir+'/raw.mda')

def process_datasets(run_code=default_run_code):
  tasks=load_tasks(run_code=run_code)

  for i,task in enumerate(tasks):
    ds=task.dataset()
    print('Processing task {} of {}: {}'.format(i+1,len(tasks),ds['name']))
    task.execute()
    
def try_process_dataset(study_name,dataset_name,run_code=default_run_code):
  tasks=load_tasks(run_code=run_code)
  for task in tasks:
    ds=task.dataset()
    if ds['study']==study_name:
      if ds['name']==dataset_name:
        result=task.run()
        return result
  raise Exception('Not found')

def assemble_dataset_results(run_code=default_run_code):
  tasks=load_tasks(run_code=run_code)

  results=[]
  for i,task in enumerate(tasks):
    print('Loading result for task {} of {}: {}/{}'.format(i+1,len(tasks),task.dataset()['study'],task.dataset()['name']))
    result=task.loadResult()
    if not result:
      raise Exception('Unable to load result for task.')
    results.append(result)

  key1=dict(name='spikeforest_studies')
  key2=dict(name='spikeforest_studies_processed')
  print('Saving results to... key={}'.format(json.dumps(key2)))
  obj=kb.loadObject(
    key=key1,
    share_ids=['spikeforest.spikeforest1']
  )
  obj['datasets']=results;
  datasets=obj['datasets']
  for ds in datasets:
      print(ds['study'],ds['name'])
  kb.saveObject(obj,key=key2)


def load_tasks(run_code):
  obj=kb.loadObject(
    key=dict(name='spikeforest_studies'),
    share_ids=['spikeforest.spikeforest1']
  )
  
  datasets=obj['datasets']
  tasks=[]
  for i,ds in enumerate(datasets):
    key=dict(
            script='process_datasets',
            study_name=ds['study'],
            dataset_name=ds['name'],
            run_code=run_code
        )
    tasks.append(
        ProcessDatasetTask(key,ds)
    )
  return tasks

class ProcessDatasetTask():
  def __init__(self,key,dataset):
    self._key=key
    self._dataset=dataset
    self._code=''.join(random.choice(string.ascii_uppercase) for x in range(10))
    
  def dataset(self):
    return self._dataset
    
  def clearResults(self,*,in_process_only):
    val=pa.get(self._key)
    if val:
      if (not in_process_only) or (val.startswith('in-process')) or (val.startswith('error')):
        print('Clearing results for: '+self._key['dataset_name'])
        pa.set(key=self._key,value=None)

  def execute(self):
    print('Dataset: '+self._dataset['name'])
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
        print('Inable to load result... it is in process.')
        return None
      else:
        return kb.loadObject(key=self._key)
    else:
      return None
  
  def run(self):
    return process_dataset(self._dataset)

def read_json_file(fname):
  with open(fname) as f:
    return json.load(f)
  
def write_json_file(fname,obj):
  with open(fname, 'w') as f:
    json.dump(obj, f)
    
def save_plot(fname,quality=40):
    plt.savefig(fname+'.png')
    plt.close()
    im=Image.open(fname+'.png').convert('RGB')
    os.remove(fname+'.png')
    im.save(fname,quality=quality)

# A MountainLab processor for generating the summary info for a dataset
class ComputeDatasetInfo(mlpr.Processor):
  NAME='ComputeDatasetInfo'
  VERSION='0.1.0'
  recording_dir=mlpr.Input(directory=True,description='Recording directory')
  json_out=mlpr.Output('Info in .json file')
    
  def run(self):
    ret={}
    recording=si.MdaRecordingExtractor(dataset_directory=self.recording_dir,download=False)
    ret['samplerate']=recording.getSamplingFrequency()
    ret['num_channels']=len(recording.getChannelIds())
    ret['duration_sec']=recording.getNumFrames()/ret['samplerate']
    write_json_file(self.json_out,ret)
  
def compute_dataset_info(dataset):
  out=ComputeDatasetInfo.execute(recording_dir=dataset['directory'],json_out={'ext':'.json'}).outputs['json_out']
  kb.saveFile(out)
  return read_json_file(kb.realizeFile(out))

# A MountainLab processor for generating a plot of a portion of the timeseries
class CreateTimeseriesPlot(mlpr.Processor):
  NAME='CreateTimeseriesPlot'
  VERSION='0.1.6'
  recording_dir=mlpr.Input(directory=True,description='Recording directory')
  jpg_out=mlpr.Output('The plot as a .jpg file')
  
  def run(self):
    R0=si.MdaRecordingExtractor(dataset_directory=self.recording_dir,download=False)
    R=st.filters.bandpass_filter(recording=R0,freq_min=300,freq_max=6000)
    N=R.getNumFrames()
    N2=int(N/2)
    channels=R.getChannelIds()
    if len(channels)>20: channels=channels[0:20]
    sw.TimeseriesWidget(recording=R,trange=[N2-4000,N2+0],channels=channels,width=12,height=5).plot()
    save_plot(self.jpg_out)
    
def create_timeseries_plot(dataset):
  out=CreateTimeseriesPlot.execute(recording_dir=dataset['directory'],jpg_out={'ext':'.jpg'}).outputs['jpg_out']
  kb.saveFile(out)
  return 'sha1://'+kb.computeFileSha1(out)+'/timeseries.jpg'

# A MountainLab processor for generating a plot of a portion of the timeseries
class CreateWaveformsPlot(mlpr.Processor):
  NAME='CreateWaveformsPlot'
  VERSION='0.1.0'
  recording_dir=mlpr.Input(directory=True,description='Recording directory')
  firings=mlpr.Input(description='Firings file')
  jpg_out=mlpr.Output('The plot as a .jpg file')
  
  def run(self):
    R0=si.MdaRecordingExtractor(dataset_directory=self.recording_dir,download=True)
    R=st.filters.bandpass_filter(recording=R0,freq_min=300,freq_max=6000)
    S=si.MdaSortingExtractor(firings_file=self.firings)
    channels=R.getChannelIds()
    if len(channels)>20:
      channels=channels[0:20]
    units=S.getUnitIds()
    if len(units)>20:
      units=units[::int(len(units)/20)]
    sw.UnitWaveformsWidget(recording=R,sorting=S,channels=channels,unit_ids=units).plot()
    save_plot(self.jpg_out)
    
def create_waveforms_plot(dataset,firings):
  out=CreateWaveformsPlot.execute(recording_dir=dataset['directory'],firings=firings,jpg_out={'ext':'.jpg'}).outputs['jpg_out']
  kb.saveFile(out)
  return 'sha1://'+kb.computeFileSha1(out)+'/waveforms.jpg'

def process_dataset(dataset):
  ret=deepcopy(dataset)
  ret['computed_info']=compute_dataset_info(dataset)  
  firings_true_path=dataset['directory']+'/firings_true.mda'
  if kb.findFile(firings_true_path):
    ret['ground_truth']=firings_true_path
  ret['plots']=dict(
    timeseries=create_timeseries_plot(dataset)
  )
  if ret['ground_truth']:
    ret['plots']['waveforms_true']=create_waveforms_plot(dataset,ret['ground_truth'])
  return ret

    