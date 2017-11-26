docker pull ubuntu
docker build -t pyyc-env .
docker run -it -v ${PWD}:/opt pyyc-env /bin/bash
