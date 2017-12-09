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
opt-5.0 -S -o /tmp/lessstupidir.ll -adce /tmp/stupidcode.ll

# Run the new ir
python /root/simplecompile.py /tmp/lessstupidir.ll
