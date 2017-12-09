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

python /opt/pyyc-hellocompiler/hellocompiler/compile.py /tmp/stupidcode.py
opt-5.0 -S -o /tmp/lessstupidir.ll -adce /tmp/stupidcode.ll 2> /tmp/lessstupidir.ll
python /root/simplecompile.py /tmp/lessstupidir.ll
