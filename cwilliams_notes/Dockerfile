FROM ubuntu:latest

RUN apt-get -y update && \
 	apt-get -y install make gcc libc6-dev-i386 python-pip vim clang

RUN pip install --upgrade pip && \
	pip install ply ipython pytest

WORKDIR /opt
