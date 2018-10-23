from kbucket import client as kb
import spikeinterface as si

def mountainsort4b_params(
    detect_sign, # Use -1, 0, or 1, depending on the sign of the spikes in the recording
    adjacency_radius, # Use -1 to include all channels in every neighborhood
    freq_min=300, # Use None for no bandpass filtering
    freq_max=6000,
    whiten=True, # Whether to do channel whitening as part of preprocessing
    clip_size=50,
    detect_threshold=3,
    detect_interval=10, # Minimum number of timepoints between events detected on the same channel
    noise_overlap_threshold=0.15 # Use None for no automated curation
):
    return locals()

def spikeforest_sort(
        recording_dirname, # The recording extractor
        sorter,
        sorting_params,
        _force_run=False,
        _force_save=False
    ):
    
    recording_signature=kb.computeDirHash(recording_dirname)
    signature_obj=dict(
        sorter_name=sorter.name,
        sorter_version=sorter.version,
        recording=recording_signature,
        sorting_params=sorting_params
    )
    if not _force_run:
        print('Looking up in cache...')
        firings=kb.realizeFile(key=signature_obj)
        if firings:
            print('Found')
            if _force_save:
                print('Saving')
                kb.saveFile(fname=firings,key=signature_obj)
            return si.MdaSortingExtractor(firings_file=firings)
    
    recording=si.MdaRecordingExtractor(recording_dirname)
    sorting=sorter(recording=recording,**sorting_params)
    
    si.MdaSortingExtractor.writeSorting(sorting=sorting,save_path='tmp_firings.mda')
    kb.saveFile(fname='tmp_firings.mda',key=signature_obj)

    return sorting