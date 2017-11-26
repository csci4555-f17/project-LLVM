'''
JIT compiles the program
`
x = 1
print x
`
'''
import compiletemplate as ct
from llvmlite import ir

# Create some useful types
double = ir.DoubleType()
integer = ir.IntType(32)
zero = ir.Constant(integer, 0)
void = ir.VoidType()

fnty_main = ir.FunctionType(integer, ())
fnty_print = ir.FunctionType(void, (integer,))
fnty_inject_int = ir.FunctionType(integer, (integer,))
# Create an empty module...
module = ir.Module(name=__file__)

# Create prototypes for runtime functions
func_print = ir.Function(module, fnty_print, name="print_any")
func_inject_int = ir.Function(module, fnty_inject_int, name="inject_int")

# main function
func = ir.Function(module, fnty_main, name="main")

block = func.append_basic_block(name="entry")
builder = ir.IRBuilder(block)
v = ir.Constant(ir.IntType(32), 1)
res = builder.call(func_inject_int, [v])
res2 = builder.call(func_print, [res])
builder.ret(zero)

ct.compile(str(module))
