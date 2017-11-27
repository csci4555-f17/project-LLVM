docker build -t llvm-docker .
docker run -it -v ${PWD}/pyyc-hellocompiler/runtime:/opt/runtime -v ${PWD}/pyyc-hellocompiler:/opt/pyyc-hellocompiler llvm-docker /bin/bash
