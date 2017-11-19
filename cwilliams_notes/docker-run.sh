docker build -t llvm-docker .
docker run -it -v ${PWD}/runtime:/opt/runtime llvm-docker /bin/bash
