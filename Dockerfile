FROM ubuntu:latest

MAINTAINER georgewang1994@163.com

ENV HOME ammonia

WORKDIR $HOME

RUN apt-get update &&\
 apt-get install -y software-properties-common &&\
 add-apt-repository ppa:jonathonf/python-3.7

RUN apt-get update &&\
 apt-get install -y python3.7 libpython3.7 python3-pip

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1 &&\
 rm /usr/bin/python3 &&\
 ln -s python3.7 /usr/bin/python3

COPY requirements.txt requirements-op.txt /$HOME/

RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements-op.txt

ADD . /$HOME/

LABEL VERSION="1.0.0"
