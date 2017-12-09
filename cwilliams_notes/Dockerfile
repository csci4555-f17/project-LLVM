FROM ubuntu:latest

RUN apt-get -y update && \
 	apt-get -y install git make gcc libc6-dev-i386 python-pip vim wget software-properties-common python-software-properties clang

# Weird steps to get around some key authentication erros while trying to add the 
# llvm apt repo in the following step
RUN add-apt-repository ppa:nilarimogard/webupd8 && \
    apt-get update && \
    apt-get install launchpad-getkeys && \
    launchpad-getkeys && \
    apt-get update
    
# Get llvm-5.0. This is needed to build llvmlite
RUN apt-add-repository "deb http://apt.llvm.org/xenial/ llvm-toolchain-xenial-5.0 main" && \
    apt-get -y update && \
    apt-get -y --allow-unauthenticated install llvm-5.0-dev

# Needed to build llvmlite
ENV LLVM_CONFIG=/usr/bin/llvm-config-5.0

RUN pip install --upgrade pip && \
	pip install ply ipython pytest

RUN git clone https://github.com/numba/llvmlite.git && \
    cd llvmlite && \
    git checkout tags/v0.21.0 && \
    python setup.py install

COPY simplefunction.py /root
COPY generate-exec.sh /root
COPY simplecompile.py /root

WORKDIR /root
