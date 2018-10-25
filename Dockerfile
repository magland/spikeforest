FROM magland/jp_proxy_widget:20180831

RUN apt-get update && apt-get install -y build-essential

### Install spikeforest
RUN pip install spikeforest
