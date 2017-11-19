FROM continuumio/miniconda
FROM ubuntu:latest

RUN apt-get -y update && \
 	apt-get -y install make gcc libc6-dev-i386 python-pip vim wget clang 

RUN pip install --upgrade pip && \
	pip install ply ipython pytest

RUN wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh && \
    /bin/bash Miniconda2-latest-Linux-x86_64.sh -b -p /opt/conda

ENV PATH /opt/conda/bin:$PATH

RUN conda install -y llvmlite

COPY simplefunction.py /root
COPY generate-exec.sh /root

WORKDIR /root
