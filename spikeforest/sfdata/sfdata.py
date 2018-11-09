from kbucket import client as kb
from PIL import Image
import json
import pandas as pd
import spikeinterface as si

def kb_read_text_file(fname):
    fname=kb.realizeFile(fname)
    with open(fname,'r') as f:
        return f.read()
    
def kb_read_json_file(fname):
    fname=kb.realizeFile(fname)
    with open(fname,'r') as f:
        return json.load(f)

class SFSortingResult():
    def __init__(self,obj,recording):
        self._obj=obj
        self._recording=recording
    def getObject(self):
        return self._obj
    def recording(self):
        return self._recording
    def sorterName(self):
        return self._obj['sorter_name']
    def plotNames(self):
        plots=self._obj['summary'].get('plots',dict())
        return list(plots.keys())
    def sorting(self):
        return si.MdaSortingExtractor(firings_file=self._obj['firings'])
    def plot(self,name,format='image'):
        plots=self._obj['summary'].get('plots',dict())
        url=plots[name]
        if format=='url':
            return url
        else:
            path=kb.realizeFile(url)
            if format=='image':
                return Image.open(path)
            elif format=='path':
                return path
            else:
                raise Exception('Invalid format: '+format)
    def comparisonWithTruth(self,*,format='dataframe'):
        A=self._obj['comparison_with_truth']
        if format=='html':
            return kb_read_text_file(A['html'])
        else:
            B=kb_read_json_file(A['json'])
            if format=='json':
                return B
            elif format=='dataframe':
                return pd.DataFrame(B).transpose()
            else:
                raise Exception('Invalid format: '+format)

class SFRecording():
    def __init__(self,obj,study):
        self._obj=obj
        self._sorting_result_names=[]
        self._sorting_results_by_name=dict()
        self._study=study
    def getObject(self):
        return self._obj
    def study(self):
        return self._study
    def name(self):
        return self._obj['name']
    def description(self):
        return self._obj['description']
    def directory(self):
        return self._obj['directory']
    def recording(self,download=False):
        return si.MdaRecordingExtractor(dataset_directory=self.directory(),download=download)
    def sortingTrue(self):
        return si.MdaSortingExtractor(firings_file=self.directory()+'/firings_true.mda')
    def plotNames(self):
        plots=self._obj.get('plots',dict())
        return list(plots.keys())
    def plot(self,name,format='image'):
        plots=self._obj.get('plots',dict())
        url=plots[name]
        if format=='url':
            return url
        else:
            path=kb.realizeFile(url)
            if format=='image':
                return Image.open(path)
            elif format=='path':
                return path
            else:
                raise Exception('Invalid format: '+format)
    def addSortingResult(self,obj):
        sorter_name=obj['sorter_name']
        if sorter_name in self._sorting_results_by_name:
            print('Sorting result already in recording: {}'.format(sorter_name))
        else:
            R=SFSortingResult(obj,self)
            self._sorting_result_names.append(sorter_name)
            self._sorting_results_by_name[sorter_name]=R
    def sortingResultNames(self):
        return self._sorting_result_names
    def sortingResult(self,name):
        return self._sorting_results_by_name[name]

class SFStudy():
    def __init__(self,obj):
        self._obj=obj
        self._recordings_by_name=dict()
        self._recording_names=[]
    def getObject(self):
        return self._obj
    def name(self):
        return self._obj['name']
    def description(self):
        return self._obj['description']
    def addRecording(self,obj):
        name=obj['name']
        if name in self._recordings_by_name:
            print('Recording already in study: '+name)
        else:
            self._recording_names.append(name)
            D=SFRecording(obj,self)
            self._recordings_by_name[name]=D
    def recordingNames(self):
        return self._recording_names
    def recording(self,name):
        return self._recordings_by_name[name]
        

class SFData():
    def __init__(self):
        self._studies_by_name=dict()
        self._study_names=[]
    def loadStudies(self,*,key=None):
        if key is None:
            key=dict(name='spikeforest_studies_processed')
        obj=kb.loadObject(key=key)
        studies=obj['studies']
        for study in studies:
            name=study['name']
            if name in self._studies_by_name:
                print('Study already loaded: '+name)
            else:
                self._study_names.append(study['name'])
                S=SFStudy(study)
                self._studies_by_name[name]=S
        recordings=obj['recordings']
        for ds in recordings:
            study=ds['study']
            self._studies_by_name[study].addRecording(ds)
    def loadSortingResults(self,*,key):
        obj=kb.loadObject(key=key)
        results=obj['sorting_results']
        for result in results:
            study_name=result['study_name']
            recording_name=result['recording_name']
            sorter_name=result['sorter_name']
            S=self.study(study_name)
            D=S.recording(recording_name)
            D.addSortingResult(result)
        print('Loaded {} results'.format(len(results)))
    def studyNames(self):
        return self._study_names
    def study(self,name):
        return self._studies_by_name[name]