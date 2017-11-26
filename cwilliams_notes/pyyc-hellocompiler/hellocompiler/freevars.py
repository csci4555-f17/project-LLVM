from compiler.ast import *
from ast_types import Let, CompareExactly, CompareTag, GetTag, InjectFrom, ProjectTo, INT_TYPE, BOOL_TYPE, BIG_TYPE, Bool, LambdaHeapified, CallUserFunc

def free_vars(n):
    if isinstance(n, Module):
        return free_vars(n.node)
    elif isinstance(n, Stmt):
        f = set([])
        for node in n.nodes:
            f = f | free_vars(node)
        return f
    elif isinstance(n, Assign):
        return free_vars(n.expr)
    elif isinstance(n, AssName):
        return set([n.name])
    elif isinstance(n, Return):
        return free_vars(n.value)
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
    elif isinstance(n, Discard):
        return free_vars(n.expr)
    elif isinstance(n, Dict):
        f = set([])
        for item in n.items:
            f = f | free_vars(item[0]) | free_vars(item[1])
        return f
    elif isinstance(n, Bool):
        return set([])
    elif isinstance(n, UnarySub):
        return free_vars(n.expr)
    elif isinstance(n, Printnl):
        f = set([])
        for node in n.nodes:
            f = f | free_vars(node)
        return f
    elif isinstance(n, Const):
        return set([])
    elif isinstance(n, Name):
        return set([n.name])
    elif isinstance(n, Add):
        return free_vars(n.left) | free_vars(n.right)
    elif isinstance(n, CallFunc):
        fv_args = [free_vars(e) for e in n.args]
        free_in_args = reduce(lambda a, b: a | b, fv_args, set([]))
        return free_vars(n.node) | free_in_args
    elif isinstance(n, LambdaHeapified):
        return free_vars(n.code) - set(n.original_argnames) - set(n.localvars)
    elif isinstance(n, Compare):
        f = set([])
        for op in n.ops:
            f = f| free_vars(op[1])
        return free_vars(n.expr) | f
    elif isinstance(n, Subscript):
        f = set([])
        for sub in n.subs:
            f = f | free_vars(sub)
        return free_vars(n.expr) | f
    elif isinstance(n, CallUserFunc):
        f = set([])
        for arg in n.args:
            f = f | free_vars(arg)
        return free_vars(n.node) | f
    elif isinstance(n, List):
        f = set([])
        for node in n.nodes:
            f = f | free_vars(node)
        return f
    elif isinstance(n, str):
        return set([])
    else:
        raise Exception("free_vars doesn't support type; %s" % n.__class__.__name__)


if __name__ == '__main__':
    p0 = '''
x = 1
z = 10
def f(a):
    q = 5
    return lambda x: x + z + k 
k = z + 1
print f(z)
'''
    import compiler 
    import uniquify
    import explicate
    original_ast = compiler.parse(p0)
    unique = uniquify.unique(compiler.parse(p0))
    new_ast = explicate.explicate(unique)
    freevs = free_vars(new_ast)
    print freevs
    print freevs.intersection(uniquify.heapify_vars)

