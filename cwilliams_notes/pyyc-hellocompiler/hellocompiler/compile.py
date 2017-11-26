import flattener as flt
import x86_ir as ir
import liveness_analysis as liveness
import interference_graph as ig
import register_allocation as ra
import flattened_to_assembly as gen
import heapify
import closure_convert
import uniquify
import declassify
import llvm_builder as builder
import compiletemplate as ct


import stack_assembly_generator as ag
import explicate as exp
import compiler
import sys



def flatten(fn):
    assembly_fn = fn.split(".")[0] + ".s"

    with open(fn, 'r') as fh:
        ast = exp.explicate(compiler.parseFile(fn))

    try:
        flattener = f.Flattener()
        flattener.flatten(ast)
        with open(assembly_fn, 'w') as fh:
            fh.write("\n".join([str(i) for i in s.generate()]))
    except SyntaxError as se:
        print "SyntaxError:", se


if __name__ == "__main__":
    #print sys.argv
    for fn in sys.argv[1:]:
        flat = flt.Flattener()
        parsed = compiler.parseFile(fn)
        declassified = declassify.declassify(parsed)
        uniqued = uniquify.unique(declassified)
        explicated = exp.explicate(uniqued)
        heaped = heapify.heapify(explicated)
        (code, funs) = closure_convert.closure_convert(heaped)
        flat_code = flat.flatten(code)
        #print flat_code

        b = builder.Builder(flat_code)
        b.build()
        #print b.module
        ct.compile(str(b.module))
