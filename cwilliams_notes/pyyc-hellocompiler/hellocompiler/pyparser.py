from lex import *
# Parser
from compiler.ast import Printnl, Add, Const, CallFunc, Name, Module, Stmt, UnarySub, Assign, AssName, Discard

precedence = (
    ('left','PLUS', 'MINUS'),
    )

def p_module(p):
    '''module : statements'''
    p[0] = Module(None, Stmt(p[1]))

def p_statements(p):
    '''statements : statement
                  | statements statement'''
    if len(p) == 2 :
        p[0] = [p[1]]
    else:
        if isinstance(p[1], list):
            p[0] = p[1] + [p[2]] 
        else:
            p[0] = [p[1], p[2]]

def p_statement(p):
    '''statement : discard
                 | assignment
                 | print '''
    p[0] = p[1]

def p_print_expression(p):
    '''print : PRINT expression'''
    p[0] = Printnl([p[2]], None)


def p_input_expression(p):
    'expression : INPUT LPAREN RPAREN'
    p[0] = CallFunc(Name('input'), [], None, None)

def p_plus_expression(p):
    'expression : expression PLUS expression'
    p[0] = Add((p[1], p[3]))

def p_int_expression(p):
    'expression : INT'
    p[0] = Const(p[1])

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_var_expression(p):
    '''expression : NAME'''
    p[0] = Name(p[1])

def p_neg_expression(p):
    'expression : MINUS expression'
    p[0] = UnarySub(p[2])

def p_discard(p):
    '''discard : expression'''
    p[0] = Discard(p[1])

def p_assignment(p):
    '''assignment : NAME EQUALS expression '''
    p[0] = Assign([AssName(p[1], 'OP_ASSIGN')], p[3])

def p_error(p):
    if p is not None:
        print "Line %s, illegal token %s" % (p.lineno, p.value)
    else:
        print "Unexpected end of input"

import ply.yacc as yacc
#parser = yacc.yacc(debug=1)
parser = yacc.yacc(debug=0)

def parse_file(fn):
    f = open(fn, 'r')
    program = f.read()
    f.close()
    return parser.parse(program)

if __name__ == "__main__":
    import compiler
    from difflib import Differ
    cmd = '''
start = input()
end = - input()
print start + end - input()
'''
    myparse = str(parser.parse(cmd))
    officialparse = str(compiler.parse(cmd))
    print myparse
    print
    print officialparse
