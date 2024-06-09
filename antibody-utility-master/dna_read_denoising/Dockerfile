FROM ubuntu:16.04

MAINTAINER Haoyang Zeng <haoyangz@mit.edu>

RUN apt-get update
RUN apt-get -q -y install python-pip
RUN apt-get -q -y install man parallel


RUN pip install numpy
RUN pip install python-Levenshtein h5py distance
RUN pip install pandas
RUN pip install scipy

RUN mkdir /scripts
ADD * /scripts/
WORKDIR /scripts

