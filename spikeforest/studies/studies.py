from spikeforest import SFStudy

def _synth_jfm_path():
  return 'kbucket://b5ecdf1474c5/spikeforest/gen_synth_datasets'

def synth_jfm_noise10_K10():
  study=SFStudy()
  study.loadDatasetsFromKBucket(
    kbucket_path=_synth_jfm_path()+'/datasets_noise10_K10',
    dataset_id_prefix=''
  )
  return study

def synth_jfm_noise10_K20():
  study=SFStudy()
  study.loadDatasetsFromKBucket(
    kbucket_path=_synth_jfm_path()+'/datasets_noise10_K20',
    dataset_id_prefix=''
  )
  return study

def synth_jfm_noise20_K10():
  study=SFStudy()
  study.loadDatasetsFromKBucket(
    kbucket_path=_synth_jfm_path()+'/datasets_noise20_K10',
    dataset_id_prefix=''
  )
  return study

def synth_jfm_noise20_K20():
  study=SFStudy()
  study.loadDatasetsFromKBucket(
    kbucket_path=_synth_jfm_path()+'/datasets_noise20_K20',
    dataset_id_prefix=''
  )
  return study