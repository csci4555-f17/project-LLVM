# Lexer
tokens = (
    'PRINT','INT','PLUS', 'INPUT', 'LPAREN',
    'RPAREN', 'MINUS', 'NAME', 'EQUALS'
    )

t_PLUS = r'\+'
t_MINUS = r'-'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_EQUALS = r'='

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_INT(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print "integer value too large", t.value
        t.value = 0
    return t

def t_PRINT(t):
    r'print'
    return t

def t_INPUT(t):
    r'input'
    return t

t_ignore = ' \t' 

def t_comment(t):
    r'\#.*[\n]*'

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

import ply.lex as lex
#lex.lex(debug=1)
lexer = lex.lex()


if __name__ == "__main__":
    cmd = '''
print input()'''
    lexer.input(cmd)
    while True:
        tok = lexer.token()
        ln = lexer.lineno
        if not tok:
            break
        print tok, ln
