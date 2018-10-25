FROM python:3.6-stretch


### Install spikeforest
RUN pip install jupyterlab
RUN mkdir /src

ADD setup.py # force rebuild whenever the version in this file has changed
RUN pip install spikeforest