FROM ubuntu:18.04

ARG FILE_PATH
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ENV LANG C.UTF-8

RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y python3-numpy python3-six curl unzip\
       libfftw3-3 libyaml-0-2 libtag1v5 libsamplerate0 python3-yaml \
       libavcodec57 libavformat57 libavutil55 libavresample3 \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
    && apt-get install -y build-essential python3-dev git python3-pip \
    libfftw3-dev libavcodec-dev libavformat-dev libavresample-dev \
    libsamplerate0-dev libtag1-dev libyaml-dev \
    && mkdir /essentia && cd /essentia && git clone https://github.com/MTG/essentia.git \
    && cd /essentia/essentia && git checkout v2.1_beta5 && python3 waf configure --with-python --with-examples --with-vamp \
    && python3 waf && python3 waf install && ldconfig \
    &&  apt-get remove -y build-essential libyaml-dev libfftw3-dev libavcodec-dev \
        libavformat-dev libavutil-dev libavresample-dev python-dev libsamplerate0-dev \
        libtag1-dev python-numpy-dev \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* \
    && cd / && rm -rf /essentia/essentia


ENV PYTHONPATH /usr/local/lib/python3/dist-packages

RUN python3 -m pip install -U matplotlib
RUN python3 -m pip install pandas
# RUN pip freeze


WORKDIR /essentia



COPY requirements.txt .

RUN pip3 install -r requirements.txt

# TODO: make setup.py script, which copies to the audio folder
COPY app.py .
COPY music_data.py .
COPY map_maker.py .
EXPOSE 5000
RUN export FLASK_APP=app.py






