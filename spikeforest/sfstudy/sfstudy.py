from mountainlab_pytools import mlproc as mlp
import spikeinterface as si

class SFStudy():
  def __init__(self):
    self._datasets=dict()

  def getDatasetIDs(self):
    return sorted(self._datasets.keys())

  def addDataset(self,*,dataset_id,dataset):
    self._datasets[dataset_id]=dataset

  def getDataset(self,dataset_id):
    return self._datasets[dataset_id]

  def loadDatasetsFromKBucket(self,*,kbucket_path,dataset_id_prefix=''):
    D=mlp.readDir(kbucket_path)
    for name in D['dirs']:
      DS=SFDataset(kbucket_path=kbucket_path+'/'+name)
      self.addDataset(dataset_id=dataset_id_prefix+name,dataset=DS)

class SFDataset():
  def __init__(self,kbucket_path):
    self._kbucket_path=kbucket_path
  
  def getRecording(self,download=True):
    ret=si.MdaRecordingExtractor(dataset_directory=self._kbucket_path,download=download)
    return ret

  def getSortingTrue(self):
    D2=mlp.readDir(self._kbucket_path)
    if 'firings_true.mda' in D2['files']:
      ret=si.MdaSortingExtractor(firings_file=self._kbucket_path+'/firings_true.mda')
    else:
      ret=None
    return ret
