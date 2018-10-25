FROM python:3.6-stretch


### Install spikeforest
RUN pip install jupyterlab

# force rebuild whenever the version in this file has changed
ADD setup.py /setup.py
RUN pip install spikeforest