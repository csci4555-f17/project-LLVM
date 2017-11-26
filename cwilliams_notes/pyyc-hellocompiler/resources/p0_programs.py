# coding: utf-8
import compiler

def p_cmd(cmd):
    print "raw command:\t", cmd
    
def p_ast(cmd):
    print "ast of command:\t", compiler.parse(cmd)
    
def p_both(cmd):
    p_cmd(cmd)
    p_ast(cmd)
    print ""

def p_invalid_both(cmd, reason):
    print "INVALID STATEMENT --", reason
    p_both(cmd)


p_both("1")
p_both("print - input() + input()")
p_both("x = 1 + 1")
p_both("x = 1 + 2 + 3")
p_both("1 + 1")
p_both("x = 1 - 1")
p_both("my_var = input(4)")
p_both("x = -1")
p_both("x = 5; y = x + 9 - 1")
p_both("""
x = 8
y = 9
z = x + y""")
p_both("print input(3)")
p_both("print input(3+3)")
p_both('"""My documentation"""; x = 5')
p_invalid_both("x, y = 4, 5", "Multiple variable assignments not supported")
p_invalid_both("x = y = 4", "Multiple variable assignments not supported")
p_invalid_both("x = True", "Booleans not supported")
p_invalid_both("(x, y, z) = 1, 2, 3", "Multiple variable assignments not supported")
p_invalid_both("print x+y, 1+3", "multi-arity print() calls not supported")
p_invalid_both("input(3.3)","input cannot take a float as an argument")
p_invalid_both("my_var = 3.3", "the only const value allowed is an integer") 
p_invalid_both("1.2+2.3", "P0 only supports integer arithematic")
p_invalid_both("1.2+2","P0 only supports integer arithematic")
p_invalid_both("my_var = 1.2+2","P0 only supports integer arithematic")
