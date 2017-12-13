docker build -t llvm-docker .
docker run -it -v ${PWD}/pyyc-hellocompiler/runtime:/opt/runtime -v ${PWD}/pyyc-hellocompiler:/opt/pyyc-hellocompiler -v ${PWD}/docker-resources/Hello.cpp:/root/llvm/lib/Transforms/Hello/Hello.cpp llvm-docker /bin/bash
