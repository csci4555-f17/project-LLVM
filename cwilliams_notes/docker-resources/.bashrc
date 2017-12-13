alias compileHello='pushd /root/llvm-build-dir && cmake --build . && popd'
alias runHelloPass='pushd /root/llvm-build-dir && ./bin/opt -load lib/LLVMHello.so -hello -f /opt/pyyc-hellocompiler/test01.ll > /dev/null && popd'
alias editHelloCpp='vim ~/llvm/lib/Transforms/Hello/Hello.cpp'
