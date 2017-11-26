from compiler.ast import *
from ast_types import *
"""
def partitions_assignments(stmts):
    assignments = []
    rest = []
    for stmt in stmts:
        if isinstance(stmt, Assign):
            assignments.append(stmt)
        elif isinstance(stmt, :

"""

def collect_assignments(n):
    assignments = []
    if not isinstance(n, Stmt):
        raise Exception("collect_assignments expects to receive a Stmt node. Received a %s" % n.__class__.__name__)
    for stmt in n.nodes:
        if isinstance(stmt, Assign):
            node = stmt.nodes[0]
            if isinstance(node, AssName):
                assignments.append(node.name)
            else:
                raise Exception("collect_assignments doesn't support %s" % stmt.__class__.__name__)
    return assignments
def p_declassify(n, c_name, assmts=None):
    if assmts == None:
        assmts = collect_assignments(n)
    if isinstance(n, Class):
        return Class(n.name, n.bases, None, p_declassify(n.code, n.name))
    if isinstance(n, Stmt):
        return Stmt([p_declassify(node, c_name, assmts) for node in n.nodes])
    if isinstance(n, Name):
        if n.name in assmts:
            return EitherVar(
                        n.name,
                        IfExp(HasAttr(c_name, n.name), 
                              GetAttr(c_name, n.name), 
                              ParentScope(n)), 
                        GetAttr(c_name, n.name))
        else:
            return n
    if isinstance(n, Discard):
        return Discard(p_declassify(n.expr, c_name,  assmts))
    if isinstance(n, Printnl):
        return Printnl([p_declassify(node, c_name, assmts) for node in n.nodes], n.dest)
    if isinstance(n, Assign):
        node = n.nodes[0]
        if isinstance(node, AssName):
            return SetAttr(c_name, node.name, p_declassify(n.expr, c_name, assmts))
        else:
            raise Exception("Unsupported assign for type %s" % node.__class__.__name__)
    if isinstance(n, Const):
        return n

    if isinstance(n, Add):
        return Add( (p_declassify(n.left, c_name, assmts), 
                     p_declassify(n.right, c_name, assmts)) )

    if isinstance(n, If):
        tests = n.tests[0]
        return IfExp(p_declassify(tests[0], c_name, assmts), 
                     p_declassify(tests[1], c_name, assmts), 
                     p_declassify(n.else_, c_name, assmts))

    if isinstance(n, Function):
        name = n.name
        return SetAttr(c_name, name, Method(name, c_name, n.argnames, n.code))
    else:
        raise Exception("Unsupported type of %s in p_declassify" % n.__class__.__name__)

def declassify(n):
    if isinstance(n, Module):
        return Module(None, declassify(n.node))
    if isinstance(n, Stmt):
        return Stmt([declassify(node) for node in n.nodes])
    if isinstance(n, Class):
        return Class(n.name, n.bases, None,  p_declassify(n.code, n.name))
    if isinstance(n, If):
        tests = n.tests[0]
        return IfExp(tests[0], tests[1], n.else_)
    else:
        return n
"""
    if isinstance(n, Printnl):
        return n
    if isinstance(n, Assign):
        return n
    raise Exception("Unsupported type of %s in declassify" % n.__class__.__name__)
"""
