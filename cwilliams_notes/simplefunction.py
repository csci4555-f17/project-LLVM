"""
This file demonstrates a trivial function "fpadd" returning the sum of
two floating-point numbers.

EXTRA:
This function also declares an empty function body for 'print_int_nl' and 
call this funcion inside of the 'fpadd' function body. The 'print_int_nl' is 
an exsiting C function which will be linked just before compilation. See
simplecompile.py for more details
"""

from llvmlite import ir

# Create some useful types
double = ir.DoubleType()
integer = ir.IntType(32)
two = ir.Constant(integer, 2)
void = ir.VoidType()
fnty = ir.FunctionType(double, (double, double))

fnty2 = ir.FunctionType(void, (integer,))

# Create an empty module...
module = ir.Module(name=__file__)
# and declare a function named "fpadd" inside it
func_print = ir.Function(module, fnty2, name="print_int_nl")
func = ir.Function(module, fnty, name="fpadd")

# Now implement the function
block = func.append_basic_block(name="entry")
builder = ir.IRBuilder(block)
a, b = func.args
result = builder.fadd(a, b, name="res")
result2 = builder.call(func_print, [ir.Constant(ir.IntType(32), 34)])
builder.ret(result)

# Print the module IR
print(module)
