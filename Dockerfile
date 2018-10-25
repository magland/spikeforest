FROM python:3.6-stretch

RUN apt-get update && apt-get install -y build-essential

### Install spikeforest
RUN pip install spikeforest
