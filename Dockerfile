FROM python:3.6-stretch


### Install spikeforest
RUN pip install jupyterlab
ADD . /src/spikeforest
WORKDIR ./src/spikeforest
RUN python setup.py develop

