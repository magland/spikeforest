FROM python:3.6-stretch


### Install spikeforest
RUN pip install jupyterlab

ADD setup.py /tmp/setup.py # force rebuild whenever the version in this file has changed
RUN pip install spikeforest