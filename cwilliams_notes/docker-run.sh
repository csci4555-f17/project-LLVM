docker build -t llvm-docker .
docker run -it -v ${PWD}/runtime:/opt/runtime -v ${PWD}/pyyc-hellocompiler:/opt/pyyc-hellocompiler llvm-docker /bin/bash
