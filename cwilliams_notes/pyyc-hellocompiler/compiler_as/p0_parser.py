#!/usr/bin/python
import ply.lex as lex

tokens = ['PRINT','INT','ASSIGN','NAME','PLUS','NEG','LPAREN','RPAREN','INPUT']

t_ignore    = ' \t'
t_ASSIGN    = '\='
t_PLUS      = '\+'
t_NEG       = '\-'
t_LPAREN    = '\('
t_RPAREN    = '\)'

def t_INT(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print "integer value too large", t.value
        t.value = 0
    return t

def t_INPUT(t):
    r'input'
    return t

def t_PRINT(t):
    r'print'
    return t

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_comment(t):
    r'\#.+'
    print "Comment: '%s'" %t.value[0]

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

lexer = lex.lex()
stmt = ''
lexer.input(stmt)


#while True:
#    tok = lexer.token()
#    if not tok:
#        break
#    print tok


from compiler.ast import Module,Stmt,Discard,CallFunc,Printnl,Add,UnarySub,Const,Assign,AssName,Name  
import ply.yacc as yacc

precedence = (
    ('left','PLUS', 'NEG'),
    )

def p_module(p):
    'module : statements'
    p[0] = Module(None, Stmt(p[1]))

def p_statements(p):
    '''statements : statement
                  | statements statement '''
    if ( len(p) == 2 ):
        p[0] = [p[1]]
    else:
        if isinstance(p[1], list):
            p[0] = p[1] + [p[2]] 
        else:
            p[0] = [p[1], p[2]]
           
#        p[0] = [p[1],p[2]]
        
#STATEMENT
def p_assign_statement(p):
    'statement : NAME ASSIGN expression'
    p[0] = Assign([AssName(p[1],'OP_ASSIGN')],p[3])

def p_print_statement(p):
    'statement : PRINT expression'
    p[0] = Printnl([p[2]], None)

def p_expression_statement(p):
    '''statement : expression '''
    p[0] = Discard(p[1])

#EXPRESSIONS

def p_plus_expression(p):
    'expression : expression PLUS expression'
    p[0] = Add((p[1], p[3]))

def p_neg_expression(p):
    'expression : NEG expression'
    p[0] = UnarySub(p[2])

def p_name_expression(p):
    'expression : NAME'
    p[0] = Name(p[1])

def p_int_expression(p):
    'expression : INT'
    p[0] = Const(p[1])

def p_input_expression(p):
    'expression : INPUT LPAREN RPAREN'
    p[0] = CallFunc(Name('input'), [], None, None)

def p_brace_expression(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_error(p):
    print "Syntax error at '%s'" % p.value

def parse_file(fn):
    f = open(fn, 'r')
    program = f.read()
    f.close()
    parser = yacc.yacc()
    return parser.parse(program)



#result = parser.parse(stmt)
#print result

#import compiler
#ast = compiler.parse(stmt)
#print ast 


