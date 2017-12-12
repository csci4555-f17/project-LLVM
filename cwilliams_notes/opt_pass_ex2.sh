# Generate some dumb pyhton code
cat >/tmp/stupidcode.py <<EOL
a = 1+2
a = 1+2
a = 1+2
a = 1+2
a = 1+2
a = 1+2
a = 1+2
a = 1+2
a = 1+2
a = 1+2
a = 1+2
a = 1+2
a = 1+2
print a
EOL

# Compile python into llvm ir
python /opt/pyyc-hellocompiler/hellocompiler/compile.py /tmp/stupidcode.py
# Run an optimization pass on the IR and generate some hopefully better IR
# -S prints output as IR
# -o print output to specified file
# -adce stands for 'aggresive dead code elimination'
#create .s file and specify target machine 
llc-5.0 -mtriple=x86_64-unknown-linux-gnu /tmp/stupidcode.ll
#link runtime lib with.s and create object file
gcc /tmp/stupidcode.s /opt/runtime/runtime.so -o stupidNonOpt -lm

# Run the non-optimized ir
START=$(date +%s)
#sleep 1
./stupidNonOpt
END=$(date +%s)
DIFF=$(( $END - $START ))
echo "Time taken non-optimized: $DIFF seconds"

#apply constmerge, instcombine and time-passes passes and write the result to stupidOptmized.ll
opt-5.0 -stats -constmerge -instcombine -time-passes < /tmp/stupidcode.ll > /dev/null -o /tmp/stupidOptimized.ll
#create .s file and specify target machine 
llc-5.0 -mtriple=x86_64-unknown-linux-gnu /tmp/stupidOptimized.ll 
#link runtime lib with.s and create object file
gcc /tmp/stupidOptimized.s /opt/runtime/runtime.so -o stupidOpt -lm

# Run the new optimized ir
START=$(date +%s)
#sleep 1
./stupidOpt
END=$(date +%s)
DIFF=$(( $END - $START ))
echo "Time taken optimized: $DIFF seconds"

