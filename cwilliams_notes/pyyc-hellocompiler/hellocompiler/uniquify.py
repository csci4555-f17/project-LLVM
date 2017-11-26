from compiler.ast import *
from ast_types import *

class NullScope():
    pass

def rename_var(name, scope):
    return "%s_%s" % (name, scope)

class Scope():
    def __init__(self, scope):
        self.scope = scope
        self.assmts = {} 

    def add_assmt(self, assmt):
        self.assmts[assmt] = self.rename_var(assmt)
        
    def rename_var(self, name):
        return "__uniquify_var_%s_%s" % (name, self.scope)

    def __repr__(self):
        return "\nscope: %s\n%s" % (self.scope, self.assmts)

null = NullScope() 
scopes = {}
heapify_vars = set([])

def get_current_scope(scope_list):
    scope_key = "_".join(scope_list)
    global scopes
    try:
        return scopes[scope_key]
    except KeyError:
        s = Scope(scope_key)
        scopes[scope_key] = s
        return s

def get_new_name(var, this_scope, first_call=True):
    assert len(this_scope) != 0
    current_scope = "_".join(this_scope)
    try:
        s = scopes[current_scope]
        name = s.assmts[var]
        if not first_call:
            heapify_vars.add(name)
        return name
    except KeyError:
        return get_new_name(var, this_scope[:-1], False)

def contained_in_scopes(var, this_scope):
    if len(this_scope) == 0:
        return None

    scope_key = "_".join(this_scope)
    try:
        s = scopes[scope_key]
        n = s.assmts[var]
        return s
    except KeyError:
        return contained_in_scopes(var, this_scope[:-1])
        
lambda_count = 0
def new_lambda_count():
    global lambda_count
    lambda_count += 1
    return lambda_count

def reset_lambda_count():
    global lambda_count
    lambda_count = 0

def gather_assignments(n, this_scope):
    if isinstance(n, Module):
        doc = n.doc
        node = n.node
        gather_assignments(node, this_scope)

    elif isinstance(n, Stmt):
        nodes = n.nodes
        _ = [gather_assignments(node, this_scope) for node in nodes]

    elif isinstance(n, Class):
        s = get_current_scope(this_scope)
        s.add_assmt(n.name)
        this_scope = this_scope + [n.name]
        gather_assignments(n.code, this_scope)

    elif isinstance(n, Assign):
        nodes = n.nodes
        e = n.expr
        _ = [gather_assignments(n, this_scope) for n in nodes]
        gather_assignments(e, this_scope)

    elif isinstance(n, AssName):
        s = get_current_scope(this_scope)
        s.add_assmt(n.name)

    elif isinstance(n, Discard):
        gather_assignments(n.expr, this_scope)

    elif isinstance(n, AssAttr):
        gather_assignments(n.expr, this_scope)

    elif isinstance(n, Const):
        pass

    elif isinstance(n, Name):
        pass

    elif isinstance(n, Function):
        s = get_current_scope(this_scope)
        s.add_assmt(n.name)
        s = get_current_scope(this_scope + [n.name])
        for arg in n.argnames:
            s.add_assmt(arg)

        gather_assignments(n.code, this_scope + [n.name])

    elif isinstance(n, Return):
        Return(gather_assignments(n.value, this_scope))

    elif isinstance(n, Lambda):
        this_scope = this_scope + ["lambda_%s" % new_lambda_count()]
        s = get_current_scope(this_scope)
        for arg in n.argnames:
            s.add_assmt(arg)

        gather_assignments(n.code, this_scope)

    elif isinstance(n, Add):
        left = n.left
        right = n.right
        gather_assignments(n.left, this_scope)
        gather_assignments(n.right, this_scope)
    
    elif isinstance(n, UnarySub):
        gather_assignments(n.expr, this_scope)

    elif isinstance(n, Printnl):
        _ = [gather_assignments(node, this_scope) for node in n.nodes]

    elif isinstance(n, CallFunc):
        gather_assignments(n.node, this_scope)
        _ = [gather_assignments(arg, this_scope) for arg in n.args]

    elif isinstance(n, List):
        _ = [gather_assignments(node, this_scope) for node in n.nodes]

    elif isinstance(n, Subscript):
        gather_assignments(n.expr, this_scope)
        _ = [gather_assignments(sub, this_scope) for sub in n.subs]

    elif isinstance(n, IfExp):
        gather_assignments(n.test, this_scope)
        gather_assignments(n.then, this_scope)
        gather_assignments(n.else_, this_scope)

    elif isinstance(n, Compare):
        gather_assignments(n.expr, this_scope)
        _ = [gather_assignments(op[1], this_scope) for op in n.ops]

    elif isinstance(n, Dict):
        for item in n.items:
            gather_assignments(item[0], this_scope)
            gather_assignments(item[1], this_scope)

    elif isinstance(n, Not):
        gather_assignments(n.expr, this_scope)

    elif isinstance(n, And):
        _ = [gather_assignments(node, this_scope) for node in n.nodes]

    elif isinstance(n, SetAttr):
        s = get_current_scope(this_scope)
        s.add_assmt(n.attr)
        gather_assignments(n.expr, this_scope)

    elif isinstance(n, Method):
        s = get_current_scope(this_scope + [n.name])
        for arg in n.argnames:
            s.add_assmt(arg)
        gather_assignments(n.code, this_scope + [n.name])

    elif isinstance(n, EitherVar):
        gather_assignments(n.this, this_scope)
        gather_assignments(n.that, this_scope)

    elif isinstance(n, ParentScope):
        gather_assignments(n.n, this_scope)

    elif isinstance(n, Getattr):
        gather_assignments(n.expr, this_scope)
      
    elif isinstance(n, HasAttr):
        pass

    elif isinstance(n, GetAttr):
        pass

    elif isinstance(n, Or):
        _ = [gather_assignments(node, this_scope) for node in n.nodes]
    else:
        raise Exception("Gather assignments doesn't support node of type %s" % n.__class__.__name__)

def uniquify(n, this_scope):
    if isinstance(n, Module):
        doc = n.doc
        node = n.node
        return Module(doc, uniquify(node, this_scope))

    elif isinstance(n, Stmt):
        nodes = n.nodes
        return Stmt([uniquify(node, this_scope) for node in nodes])

    elif isinstance(n, Discard):
        return Discard(uniquify(n.expr, this_scope))

    elif isinstance(n, Assign):
        nodes = n.nodes
        e = n.expr
        return Assign([uniquify(n, this_scope) for n in nodes],
                       uniquify(e, this_scope))

    elif isinstance(n, AssName):
        return AssName(get_new_name(n.name, this_scope), n.flags)

    elif isinstance(n, Const):
        return n

    elif isinstance(n, ParentScope):
        return uniquify(n.n, this_scope[:-1])

    elif isinstance(n, EitherVar):
        if contained_in_scopes(n.var, this_scope[:-1]):
            return uniquify(n.this, this_scope)
        else:
            return uniquify(n.that, this_scope)

    elif isinstance(n, Name):
        if n.name in ('input', 'True', 'False'):
            return n
        return Name(get_new_name(n.name, this_scope))

    elif isinstance(n, Class):
        cname = get_new_name(n.name, this_scope)
        new_bases = [uniquify(base, this_scope) for base in n.bases]
        this_scope = this_scope + [n.name]
        return Class(cname, new_bases, None, uniquify(n.code, this_scope))

    elif isinstance(n, SetAttr):
        #scoping for classes is string
        cname = get_new_name(n.obj, this_scope[:-1])
        return SetAttr(cname, n.attr, uniquify(n.expr, this_scope))

    elif isinstance(n, HasAttr):
        cname = get_new_name(n.obj, this_scope[:-1])
        return HasAttr(cname, n.attr)

    elif isinstance(n, GetAttr):
        cname = get_new_name(n.obj, this_scope[:-1])
        return GetAttr(cname, n.attr)

    elif isinstance(n, Function):
        fname = get_new_name(n.name, this_scope)
        this_scope = this_scope + [n.name]
        return Function(n.decorators,
                        fname,
                        [get_new_name(arg, this_scope) for arg in n.argnames],
                        n.defaults,
                        n.flags,
                        n.doc,
                        uniquify(n.code, this_scope))

    elif isinstance(n, Method):
        this_scope = this_scope + [n.name]
        return Function(None,
                        n.name,
                        [get_new_name(arg, this_scope) for arg in n.argnames],
                        (),
                        0,
                        None,
                        uniquify(n.code, this_scope))

    elif isinstance(n, Return):
        return Return(uniquify(n.value, this_scope))

    elif isinstance(n, Lambda):
        this_scope = this_scope + ["lambda_%s" % new_lambda_count()]
        return Lambda([get_new_name(arg, this_scope) for arg in n.argnames],
                      n.defaults,
                      n.flags,
                      uniquify(n.code, this_scope))

    elif isinstance(n, Add):
        return Add((uniquify(n.left, this_scope), uniquify(n.right, this_scope)))
    
    elif isinstance(n, UnarySub):
        return UnarySub(uniquify(n.expr, this_scope))

    elif isinstance(n, Printnl):
        return Printnl([uniquify(node, this_scope) for node in n.nodes], n.dest)

    elif isinstance(n, List):
        return List([uniquify(node, this_scope) for node in n.nodes])

    elif isinstance(n, Subscript):
        return Subscript(uniquify(n.expr, this_scope), n.flags, [uniquify(sub, this_scope) for sub in n.subs])

    elif isinstance(n, CallFunc):
        return CallFunc(uniquify(n.node, this_scope), [uniquify(arg, this_scope) for arg in n.args])
    elif isinstance(n, IfExp):
        return IfExp(uniquify(n.test, this_scope),
                     uniquify(n.then, this_scope),
                     uniquify(n.else_, this_scope))

    elif isinstance(n, Compare):
        return Compare(uniquify(n.expr, this_scope),
                       [(op[0], uniquify(op[1], this_scope)) for op in n.ops])

    elif isinstance(n, Dict):
        items = []
        for item in n.items:
            items.append((uniquify(item[0], this_scope), uniquify(item[1], this_scope)))
        return Dict(items)

    elif isinstance(n, Not):
        return Not(uniquify(n.expr, this_scope))

    elif isinstance(n, And):
        return And([uniquify(node, this_scope) for node in n.nodes])

    elif isinstance(n, Or):
        return Or([uniquify(node, this_scope) for node in n.nodes])

    elif isinstance(n, Getattr):
        return Getattr(uniquify(n.expr, this_scope), n.attrname)

    elif isinstance(n, AssAttr):
        return AssAttr(uniquify(n.expr, this_scope), n.attrname, n.flags)
    else:
        print n
        raise Exception("uniquify doesn't support node of type %s" % n.__class__.__name__)

def unique(ast):
    gather_assignments(ast, ['main'])
    reset_lambda_count()
    return uniquify(ast, ['main'])

if __name__ == '__main__':
    p = '''
class C:
    1
'''

    import compiler
    ast = compiler.parse(p)
    print unique(ast)
