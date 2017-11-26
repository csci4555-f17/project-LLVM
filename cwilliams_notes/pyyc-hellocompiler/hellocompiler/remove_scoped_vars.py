from compiler.ast import *
from ast_types import Let, CompareExactly, CompareTag, GetTag, InjectFrom, ProjectTo, INT_TYPE, BOOL_TYPE, BIG_TYPE, Bool, ScopedName

def remove_scoped_vars(n):
    if isinstance(n, Module):
        return Module(n
    elif isinstance(n, Stmt):
        f = set([])
        for node in n.nodes:
            f = f | free_vars(node)
        return f
    elif isinstance(n, Assign):
        f_nodes = set([])
        for node in n.nodes:
            f_nodes = f_nodes | free_vars(node)
        return free_vars(n.expr) | f_nodes 
    elif isinstance(n, AssName):
        return free_vars(n.name)
    elif isinstance(n, Const):
        return set([])
    elif isinstance(n, Name):
        return free_vars(n.name)
    elif isinstance(n, ScopedName):
        if n.defined_scope != n.usage_scope:
            return set([n])
        else:
            return set([])
    elif isinstance(n, Add):
        return free_vars(n.left) | free_vars(n.right)
    elif isinstance(n, CallFunc):
        fv_args = [free_vars(e) for e in n.args]
        free_in_args = reduce(lambda a, b: a | b, fv_args, set([]))
        return free_vars(n.node) | free_in_args
    elif isinstance(n, Lambda):
        return free_vars(n.code)
    elif isinstance(n, Printnl):
        f = set([])
        for node in n.nodes:
            f = f | free_vars(node)
        return f
    elif isinstance(n, Let):
        return free_vars(n.rhs) | free_vars(n.body)
    elif isinstance(n, IfExp):
        return free_vars(n.test) | free_vars(n.then) | free_vars(n.else_)
    elif isinstance(n, InjectFrom):
        return free_vars(n.arg)
    elif isinstance(n, CompareTag):
        return free_vars(n.var)
    elif isinstance(n, ProjectTo):
        return free_vars(n.arg)
    elif isinstance(n, Return):
        return free_vars(n.value)
    elif isinstance(n, str):
        return set([])
    else:
        raise Exception("Unsupported node passed to free_vars: %s" % n.__class__.__name__)

