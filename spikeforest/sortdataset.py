from kbucket import client as kb
import spikeinterface as si
import spikeforest as sf
import tempfile
import random
import mlprocessors as mlpr
import os

class MountainSort4(mlpr.Processor):
    NAME='MountainSort4'
    VERSION='4.0.1'
    
    dataset_dir=mlpr.Input('Directory of dataset',directory=True)
    firings_out=mlpr.Output('Output firings file')
    
    detect_sign=mlpr.IntegerParameter('Use -1, 0, or 1, depending on the sign of the spikes in the recording')
    adjacency_radius=mlpr.FloatParameter('Use -1 to include all channels in every neighborhood')
    freq_min=mlpr.FloatParameter(optional=True,default=300,description='Use 0 for no bandpass filtering')
    freq_max=mlpr.FloatParameter(optional=True,default=6000,description='Use 0 for no bandpass filtering')
    whiten=mlpr.BoolParameter(optional=True,default=True,description='Whether to do channel whitening as part of preprocessing')
    clip_size=mlpr.IntegerParameter(optional=True,default=50,description='')
    detect_threshold=mlpr.FloatParameter(optional=True,default=3,description='')
    detect_interval=mlpr.IntegerParameter(optional=True,default=10,description='Minimum number of timepoints between events detected on the same channel')
    noise_overlap_threshold=mlpr.FloatParameter(optional=True,default=0.15,description='Use None for no automated curation')
    
    def run(self):
        recording=si.MdaRecordingExtractor(self.dataset_dir)
        num_workers=int(os.environ.get('NUM_WORKERS',-1))
        if num_workers<=0: num_workers=None
        sorting=sf.sorters.mountainsort4(
            recording=recording,
            detect_sign=self.detect_sign,
            adjacency_radius=self.adjacency_radius,
            freq_min=self.freq_min,
            freq_max=self.freq_max,
            whiten=self.whiten,
            clip_size=self.clip_size,
            detect_threshold=self.detect_threshold,
            detect_interval=self.detect_interval,
            noise_overlap_threshold=self.noise_overlap_threshold,
            num_workers=num_workers
        )
        si.MdaSortingExtractor.writeSorting(sorting=sorting,save_path=self.firings_out)

def sortDataset(
    *,
    sorter,
    dataset,
    _force_run=False
):
    dsdir=dataset['directory']
    sorting_params=sorter['params']
    sorting_processor=sorter['processor']
    outputs=sorting_processor.execute(dataset_dir=dsdir,firings_out=dict(ext='.mda'),**sorting_params,_force_run=_force_run).outputs
    result=dict(
        dataset_name=dataset['name'],
        dataset_dir=dsdir,
        firings_true=dsdir+'/firings_true.mda',
        sorting_params=sorting_params,
        sorting_processor_name=sorting_processor.NAME,
        sorting_processor_version=sorting_processor.VERSION,
        firings=outputs['firings_out']
    )
    kb.saveFile(outputs['firings_out'])
    return result

def _create_temporary_fname(ext):
    return tempfile.gettempdir()+'/tmp_'+''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))+ext
