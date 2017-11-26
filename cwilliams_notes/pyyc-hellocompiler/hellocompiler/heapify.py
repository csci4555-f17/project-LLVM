from compiler.ast import *
from ast_types import Let, CompareExactly, CompareTag, GetTag, InjectFrom, ProjectTo, INT_TYPE, BOOL_TYPE, BIG_TYPE, Bool, CallUserFunc, LambdaHeapified
from uniquify import heapify_vars

def heapify(ast_):
    def local_assmts(ns):
        l = []
        for n in ns:
            if isinstance(n, Assign):
                for node in n.nodes:
                    if isinstance(node, AssName):
                        l.append(node.name)
        return l

    def rename_args(argnames, heap_vars):
        new_args = []
        renamed_args = []
        for arg in argnames:
            if arg in heap_vars:
                new_args.append(arg + "_new")
                renamed_args.append((arg, arg+"_new"))
            else:
                new_args.append(arg)
        return (new_args, renamed_args)

    def descend(n):
        if isinstance(n, Module):
            doc = n.doc
            node = n.node
            return Module(doc, descend(node))

        if isinstance(n, Stmt):
            nodes = n.nodes
            return Stmt([descend(node) for node in nodes])

        if isinstance(n, Name):
            name = n.name
            if name in heapify_vars:
                return Subscript(Name(name), 'OP_ASSIGN', [Const(0)])
            return Name(name)

        if isinstance(n, Const):
            return n

        if isinstance(n, Bool):
            return n

        if isinstance(n, Let):
            return Let(descend(n.var), descend(n.rhs), descend(n.body))

        if isinstance(n, InjectFrom):
            return InjectFrom(n.typ, descend(n.arg))

        if isinstance(n, CompareTag):
            return CompareTag(descend(n.var), n.tag_type)

        if isinstance(n, Add):
            return Add((descend(n.left), descend(n.right)))

        if isinstance(n, ProjectTo):
            return ProjectTo(n.typ, descend(n.arg))

        if isinstance(n, Printnl):
            nodes = n.nodes
            dest = n.dest
            return Printnl([descend(node) for node in nodes], dest) 

        if isinstance(n, Assign):
            nodes = n.nodes
            expr = n.expr
            return Assign([descend(node) for node in nodes], descend(expr))

        if isinstance(n, AssName):
            name = n.name
            if name in heapify_vars:
                return Subscript(Name(name), 'OP_ASSIGN', [Const(0)])
            flags = n.flags
            return AssName(name, flags)

        if isinstance(n, AssAttr):
            return n

        if isinstance(n, Discard):
            expr = n.expr
            return Discard(descend(expr))

        if isinstance(n, UnarySub):
            return UnarySub(descend(n.expr))

        if isinstance(n, CallFunc):
            node = n.node
            args = n.args
            return CallFunc(descend(node), [descend(arg) for arg in args], None, None)

        if isinstance(n, List):
            nodes = n.nodes
            return List([descend(node) for node in nodes])

        if isinstance(n, Dict):
            items = n.items
            return Dict([(descend(kv[0]), descend(kv[1])) for kv in items])

        if isinstance(n, Subscript):
            expr = n.expr
            flags = n.flags
            subs = n.subs
            return Subscript(descend(expr), flags, [descend(sub) for sub in subs])

        if isinstance(n, IfExp):
            test = n.test
            then = n.then
            else_ = n.else_
            return IfExp(descend(test), descend(then), descend(else_))

        if isinstance(n, Lambda):
            print heapify_vars
            local = set(local_assmts(n.code))
            local_to_inits = local.intersection(heapify_vars)
            params = set(n.argnames)
            params_to_heapify = params.intersection(heapify_vars)
            (new_args, renamed) = rename_args(n.argnames, heapify_vars)
            param_inits = []
            for a in renamed:
                param_inits.append(Assign([AssName(a[0], 'OP_ASSIGN')], List([Name(a[1])])))

            local_inits = []
            for l in list(local_to_inits):
                local_inits.append(Assign([AssName(l, 'OP_ASSIGN')], List([Const(0)])))

            return LambdaHeapified(new_args, n.argnames, param_inits, list(local_to_inits), local_inits, descend(n.code))

        if isinstance(n, Return):
            return Return(descend(n.value))

        if isinstance(n, CallUserFunc):
            node = n.node
            args = n.args
            return CallUserFunc(descend(node), [descend(arg) for arg in args])

        if isinstance(n, CompareExactly):
            return CompareExactly(descend(n.l), descend(n.r))

        if isinstance(n, Compare):
            return Compare(descend(n.expr), [(op[0], descend(op[1])) for op in n.ops])

        if isinstance(n, Class):
            return Class(n.name, n.bases, None, descend(n.code))

        if isinstance(n, str):
            return n

        raise Exception("Unsupported type in heapify %s" % n)

    new_statements = []
    local = set(local_assmts(ast_.node.nodes))
    local_to_init = list(local.intersection(heapify_vars))
    for var in local_to_init:
        new_statements.append( 
            Assign([AssName(var, 'OP_ASSIGN')], List([Const(0)])))
    new_ast = descend(ast_)
    stmts = new_ast.node.nodes
    new_ast.node.nodes = new_statements + stmts
    return new_ast

if __name__ == '__main__':
    p0 = '''
x = 2
def f(a, c):
    print x
    b = 5
    return lambda a: c

print f(2)
'''
    import compiler 
    import uniquify
    import explicate
    original_ast = compiler.parse(p0)
    unique = uniquify.unique(compiler.parse(p0))
    new_ast = explicate.explicate(unique)
    print heapify(new_ast)
