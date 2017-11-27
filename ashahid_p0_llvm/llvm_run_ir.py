from __future__ import print_function

from ctypes import CFUNCTYPE, c_double, c_int, c_void_p

import llvmlite.binding as llvm

from p0_llvm import *


class py_to_llvm_ir():

    def __init__(self):
        self.instr = dict()
        self.prog_ord = []

        # All these initializations are required for code generation!
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()  # yes, even this one
        llvm.load_library_permanently("/home/ashahid/Documents/CS-5555/hw_project/llvmlite/runtime/runtime.so")
        #self.llvm_ir = +str(llvm_ir)
        self.llvm_ir = """
        ; ModuleID = "p0_llvm.py"
        target triple = "unknown-unknown-unknown"
        target datalayout = ""

        define void @"main"() 
        {
        entry:
        %"res" = add i32 1, 1
        call void @"print_int_nl"(i32 %"res")
        ret void
        }

        declare void @"print_int_nl"(i32 %".1") 
        """

    def create_execution_engine(self):
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

    def compile_ir(self, engine):
        """
        Compile the LLVM IR string with the given engine.
        The compiled module object is returned.
        """
        # Create a LLVM module object from the IR
        mod = llvm.parse_assembly(self.llvm_ir)
        mod.verify()
        # Now add the module and make sure it is ready for execution
        engine.add_module(mod)
        engine.finalize_object()
        return mod



def py_llvm_trans():

    py_to_llvm_ir_inst = py_to_llvm_ir()
    
#    print py_to_llvm_ir_inst.llvm_ir

    engine = py_to_llvm_ir_inst.create_execution_engine()
    mod = py_to_llvm_ir_inst.compile_ir(engine)

    # Look up the function pointer (a Python int)
    # Run the function via ctypes
    func_ptr = engine.get_function_address("main")
    cfunc = CFUNCTYPE(c_void_p)(func_ptr)
    res = cfunc()
    print("fpadd(...) =", res)


if __name__ == "__main__":
    print module
    py_llvm_trans()


