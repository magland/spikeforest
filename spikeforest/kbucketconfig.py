from kbucket import client as kb
from pairio import client as pa
import getpass

def kbucketConfigLocal(write=True):
  pa.setConfig(
      collections=[],
      user='',
      token='',
      read_local=True,write_local=False,read_remote=False,write_remote=False
  )
  kb.setConfig(
      share_ids=[],
      upload_share_id='',
      upload_token='',
      load_local=True,load_remote=False,save_remote=False
  )
  if write:
    pa.setConfig(
        write_local=True,
    )

def kbucketConfigRemote(*,user='spikeforest',share_id='spikeforest.spikeforest2',password=None,write=False):
  pa.setConfig(
      collections=[user],
      user='',
      token='',
      read_local=False,write_local=False,read_remote=True,write_remote=False
  )
  kb.setConfig(
      share_ids=[share_id],
      upload_share_id='',
      upload_token='',
      load_local=True,load_remote=True,save_remote=False
  )
  if write:
    if password is None:
      password=getpass.getpass('Enter the spikeforest password')
    pa.setConfig(
        user=user,
        token=pa.get(collection='spikeforest',key=dict(name='pairio_token',user=user,password=password)),
        write_remote=True
    )
    kb.setConfig(
        upload_share_id=share_id,
        upload_token=pa.get(collection='spikeforest',key=dict(name='kbucket_token',share_id=share_id,password=password)),
        save_remote=True
    )