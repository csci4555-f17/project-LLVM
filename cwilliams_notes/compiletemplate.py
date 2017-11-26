from __future__ import print_function

from ctypes import CFUNCTYPE, c_double, c_int

import llvmlite.binding as llvm
import sys

# All these initializations are required for code generation!
llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()  # yes, even this one
llvm.load_library_permanently("/opt/runtime/runtime.so")

'''
llvm_ir = """
   ; ModuleID = "examples/ir_fpadd.py"
   target triple = "unknown-unknown-unknown"
   target datalayout = ""

   declare void @"print_int_nl"(i32 %".1")

   define double @"fpadd"(double %".1", double %".2")
   {
   entry:
     %"res" = fadd double %".1", %".2"
     call void @"print_int_nl"(i32 34)
     ret double %"res"
   }
   """
'''

def create_execution_engine():
    """
    Create an ExecutionEngine suitable for JIT code generation on
    the host CPU.  The engine is reusable for an arbitrary number of
    modules.
    """
    # Create a target machine representing the host
    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    # And an execution engine with an empty backing module
    backing_mod = llvm.parse_assembly("")
    engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
    return engine


def compile_ir(engine, llvm_ir):
    """
    Compile the LLVM IR string with the given engine.
    The compiled module object is returned.
    """
    # Create a LLVM module object from the IR
    mod = llvm.parse_assembly(llvm_ir)
    mod.verify()
    # Now add the module and make sure it is ready for execution
    engine.add_module(mod)
    engine.finalize_object()
    return mod

def compile(llvm_ir):

    engine = create_execution_engine()
    mod = compile_ir(engine, llvm_ir)

    # Look up the function pointer (a Python int)
    # Run the function via ctypes
    func_ptr = engine.get_function_address("main")
    cfunc = CFUNCTYPE(c_int)(func_ptr)
    res = cfunc()
    sys.exit(res)
