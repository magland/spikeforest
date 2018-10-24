from matplotlib import pyplot as plt
from PIL import Image
import mlprocessors as mlpr
from kbucket import client as kb
import spikeinterface as si
import spikewidgets as sw
import os

def summarizeSorting(result):
    ret={'plots':{}}
    unit_waveforms=PlotUnitWaveforms.execute(recording_dir=result['dataset_dir'],firings=result['firings'],plot_out={'ext':'.jpg'}).outputs['plot_out']
    unit_waveforms=kb.saveFile(unit_waveforms,basename='unit_waveforms.jpg')
    ret['plots']['unit_waveforms']=unit_waveforms
    return ret

class PlotUnitWaveforms(mlpr.Processor):
    recording_dir=mlpr.Input(directory=True,description='Recording directory')
    firings=mlpr.Input('Firings file (sorting)')
    plot_out=mlpr.Output('Plot as .jpg image file')
    
    def run(self):
        recording=si.MdaRecordingExtractor(dataset_directory=self.recording_dir)
        sorting=si.MdaSortingExtractor(firings_file=self.firings)
        sw.UnitWaveformsWidget(recording=recording,sorting=sorting).plot()
        fname=save_plot(self.plot_out)

def save_plot(fname,quality=20):
    plt.savefig(fname+'.png')
    plt.close()
    im=Image.open(fname+'.png').convert('RGB')
    os.remove(fname+'.png')
    im.save(fname,quality=quality)