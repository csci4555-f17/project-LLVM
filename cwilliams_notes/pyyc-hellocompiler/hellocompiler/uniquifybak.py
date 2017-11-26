from compiler.ast import *

class NullScope():
    pass

def rename_var(name, scope):
    return "%s_%s" % (name, scope)

class Scope():
    def __init__(self, scope, parent_scope):
        self.scope = scope
        self.assmts = {} 
        self.parent_scope = parent_scope

    def add_assmt(self, assmt):
        self.assmts[assmt] = self.rename_var(assmt)
        
    def rename_var(self, name):
        return "__uniquify_var_%s_%s" % (name, self.scope)

    def __repr__(self):
        return "\nscope: %s\n%s" % (self.scope, self.assmts)

null = NullScope() 
scopes = {-1: null,
          0: Scope(0, null)}
heapify_vars = set([])

def get_current_scope(current, parent):
    global scopes
    try:
        return scopes[current]
    except KeyError:
        s = Scope(current, scopes[parent])
        scopes[current] = s
        return s

scope_count = 0
def get_next_scope():
    global scope_count
    scope_count += 1
    return scope_count

def reset_scope_count():
    global scope_count
    scope_count = 0

def get_new_name(var, callee_scope, current_scope=None):
    if current_scope == None:
        current_scope = callee_scope

    s = scopes[current_scope]
    try:
        name = s.assmts[var]
        if callee_scope != current_scope:
            heapify_vars.add(name)
        return name
    except KeyError:
        return get_new_name(var, callee_scope, s.parent_scope.scope)
        
def gather_assignments(n, this_scope, parent_scope):
    if isinstance(n, Module):
        doc = n.doc
        node = n.node
        gather_assignments(node, this_scope, parent_scope)

    elif isinstance(n, Stmt):
        nodes = n.nodes
        _ = [gather_assignments(node, this_scope, parent_scope) for node in nodes]

    elif isinstance(n, Assign):
        nodes = n.nodes
        e = n.expr
        _ = [gather_assignments(n, this_scope, parent_scope) for n in nodes]
        gather_assignments(e, this_scope, parent_scope)

    elif isinstance(n, AssName):
        s = get_current_scope(this_scope, parent_scope)
        s.add_assmt(n.name)

    elif isinstance(n, Discard):
        gather_assignments(n.expr, this_scope, parent_scope)

    elif isinstance(n, Const):
        pass

    elif isinstance(n, Name):
        pass

    elif isinstance(n, Function):
        s = get_current_scope(this_scope, parent_scope)
        s.add_assmt(n.name)
        parent_scope, this_scope = this_scope, get_next_scope()
        s = get_current_scope(this_scope, parent_scope)
        for arg in n.argnames:
            s.add_assmt(arg)

        gather_assignments(n.code, this_scope, parent_scope)

    elif isinstance(n, Return):
        Return(gather_assignments(n.value, this_scope, parent_scope))

    elif isinstance(n, Lambda):
        parent_scope, this_scope = this_scope, get_next_scope()
        s = get_current_scope(this_scope, parent_scope)
        for arg in n.argnames:
            s.add_assmt(arg)

        gather_assignments(n.code, this_scope, parent_scope)

    elif isinstance(n, Add):
        left = n.left
        right = n.right
        gather_assignments(n.left, this_scope, parent_scope)
        gather_assignments(n.right, this_scope, parent_scope)
    
    elif isinstance(n, UnarySub):
        gather_assignments(n.expr, this_scope, parent_scope)

    elif isinstance(n, Printnl):
        _ = [gather_assignments(node, this_scope, parent_scope) for node in n.nodes]

    elif isinstance(n, CallFunc):
        gather_assignments(n.node, this_scope, parent_scope)
        _ = [gather_assignments(arg, this_scope, parent_scope) for arg in n.args]

    elif isinstance(n, List):
        _ = [gather_assignments(node, this_scope, parent_scope) for node in n.nodes]

    elif isinstance(n, Subscript):
        gather_assignments(n.expr, this_scope, parent_scope)
        _ = [gather_assignments(sub, this_scope, parent_scope) for sub in n.subs]

    elif isinstance(n, IfExp):
        gather_assignments(n.test, this_scope, parent_scope)
        gather_assignments(n.then, this_scope, parent_scope)
        gather_assignments(n.else_, this_scope, parent_scope)

    elif isinstance(n, Compare):
        gather_assignments(n.expr, parent_scope)
        _ = [gather_assignments(op[1], this_scope, parent_scope) for op in n.ops]

    elif isinstance(n, Dict):
        for item in n.items:
            gather_assignments(item[0], this_scope, parent_scope)
            gather_assignments(item[1], this_scope, parent_scope)

    elif isinstance(n, Not):
        gather_assignments(n.expr, this_scope, parent_scope)

    elif isinstance(n, And):
        _ = [gather_assignments(node, this_scope, parent_scope) for node in n.nodes]

    elif isinstance(n, Or):
        _ = [gather_assignments(node, this_scope, parent_scope) for node in n.nodes]
    else:
        raise Exception("Gather assignments doesn't support node of type %s" % n.__class__.__name__)

def uniquify(n, this_scope, parent_scope):
    if isinstance(n, Module):
        doc = n.doc
        node = n.node
        return Module(doc, uniquify(node, this_scope, parent_scope))

    elif isinstance(n, Stmt):
        nodes = n.nodes
        return Stmt([uniquify(node, this_scope, parent_scope) for node in nodes])

    elif isinstance(n, Discard):
        return Discard(uniquify(n.expr, this_scope, parent_scope))

    elif isinstance(n, Assign):
        nodes = n.nodes
        e = n.expr
        return Assign([uniquify(n, this_scope, parent_scope) for n in nodes],
                       uniquify(e, this_scope, parent_scope))

    elif isinstance(n, AssName):
        return AssName(get_new_name(n.name, this_scope), n.flags)

    elif isinstance(n, Const):
        return n

    elif isinstance(n, Name):
        if n.name in ('input', 'True', 'False'):
            return n
        return Name(get_new_name(n.name, this_scope))

    elif isinstance(n, Function):
        fname = get_new_name(n.name, this_scope)
        parent_scope, this_scope = this_scope, get_next_scope()
        return Function(n.decorators,
                        fname,
                        [get_new_name(arg, this_scope) for arg in n.argnames],
                        n.defaults,
                        n.flags,
                        n.doc,
                        uniquify(n.code, this_scope, parent_scope))

    elif isinstance(n, Return):
        return Return(uniquify(n.value, this_scope, parent_scope))

    elif isinstance(n, Lambda):
        parent_scope, this_scope = this_scope, get_next_scope()
        return Lambda([get_new_name(arg, this_scope) for arg in n.argnames],
                      n.defaults,
                      n.flags,
                      uniquify(n.code, this_scope, parent_scope))

    elif isinstance(n, Add):
        return Add((uniquify(n.left, this_scope, parent_scope), uniquify(n.right, this_scope, parent_scope)))
    
    elif isinstance(n, UnarySub):
        return UnarySub(uniquify(n.expr, this_scope, parent_scope))

    elif isinstance(n, Printnl):
        return Printnl([uniquify(node, this_scope, parent_scope) for node in n.nodes], n.dest)

    elif isinstance(n, List):
        return List([uniquify(node, this_scope, parent_scope) for node in n.nodes])

    elif isinstance(n, Subscript):
        return Subscript(uniquify(n.expr, this_scope, parent_scope), n.flags, [uniquify(sub,this_scope,  parent_scope) for sub in n.subs])

    elif isinstance(n, CallFunc):
        return CallFunc(uniquify(n.node, this_scope, parent_scope), [uniquify(arg, this_scope, parent_scope) for arg in n.args])
    elif isinstance(n, IfExp):
        return IfExp(uniquify(n.test, this_scope, parent_scope),
                     uniquify(n.then, this_scope, parent_scope),
                     uniquify(n.else_, this_scope, parent_scope))

    elif isinstance(n, Compare):
        return Compare(uniquify(n.expr, this_scope, parent_scope),
                       [(op[0], uniquify(op[1], this_scope, parent_scope)) for op in n.ops])

    elif isinstance(n, Dict):
        items = []
        for item in n.items:
            items.append((uniquify(item[0], this_scope, parent_scope), uniquify(item[1], this_scope, parent_scope)))
        return Dict(items)

    elif isinstance(n, Not):
        return Not(uniquify(n.expr, this_scope, parent_scope))

    elif isinstance(n, And):
        return And([uniquify(node, this_scope, parent_scope) for node in n.nodes])

    elif isinstance(n, Or):
        return Or([uniquify(node, this_scope, parent_scope) for node in n.nodes])

    else:
        print n
        raise Exception("uniquify doesn't support node of type %s" % n.__class__.__name__)

def unique(ast):
    gather_assignments(ast, 0, None)
    print scopes
    reset_scope_count()
    return uniquify(ast, 0, None)

if __name__ == '__main__':
    p = '''
a = input()
b = input()
c = input()


def d(e,f,g):
    h = a + b + c
    r = lambda x : h + x
    return r(1)

o = lambda p : p + p

i = d(o(1),b,c)
print i

s = lambda y : d(a,b,c) + y
print s(1)
'''

    import compiler
    ast = compiler.parse(p)
    gather_assignments(ast)
    new_ast = uniquify(ast)
    print new_ast
    print "heapify_vars", heapify_vars
