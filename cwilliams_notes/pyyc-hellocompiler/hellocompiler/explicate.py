from compiler.ast import *
from ast_types import *

let_scope = 0
def explicate(ast_):

    def is_pure(e):
        return isinstance(e, Name) or isinstance(e, Const) or isinstance(e, Bool)

    def get_let_var():
        global let_scope
        let_scope += 1
        return Name("__let_var_%s" % let_scope)

    def letify(expr, k):
#        if is_pure(expr):
#            return k(expr)
#
        v = get_let_var()
        return Let(v, expr, k(v))

    def function_polymorphism(n):
        print "!!!!!!!!!!!!!!"
        print n

        def get_receiver(f):
            #return CallFunc(Name('get_receiver'), [f])
            return InjectFrom('big', CallFunc(Name('get_receiver'), [f]))
        def get_init_attr(f):
            return CallFunc(Name('get_attr'), [f, '__init__'])
        def get_function(f):
            return InjectFrom('big', CallFunc(Name('get_function'), [f]))
            #return CallFunc(Name('get_function'), [f])
        def create_object(f):
            return InjectFrom('big', CallFunc(Name('create_object'), [f]))
        def ini_func(f):
            return InjectFrom('big', CallFunc(Name('get_function'), [get_init_attr(f)]))

        def call_ini_return(ini, o):
            return letify(CallUserFunc(ini, [o] + n.args), lambda x: o)

        def if_is_class(f, o):
            return IfExp(InjectFrom('bool', CallFunc(Name('has_attr'), [f, '__init__'])),
                         letify(ini_func(f), lambda ini: call_ini_return(ini, o)),
                         o)
                         
        def result(f):
            return IfExp(InjectFrom('bool', CallFunc(Name('is_class'), [f])), 
                         letify(create_object(f), lambda o: if_is_class(f, o)),
                         IfExp(InjectFrom('bool', CallFunc(Name('is_bound_method'), [f])),
                               letify(get_function(f), lambda func: letify(get_receiver(f), lambda receiver : CallUserFunc(func, [receiver] + n.args))),
                               IfExp(InjectFrom('bool', CallFunc(Name('is_unbound_method'), [f])),
                                     letify(get_function(f) , lambda func: CallUserFunc(func, n.args)),
                                     CallUserFunc(f, [descend(arg) for arg in n.args]))))
        return letify(descend(n.node), lambda f: result(f))

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
            if name == 'True':
                return Bool(True)
            if name == 'False':
                return Bool(False)
            return Name(name)

        if isinstance(n, Const):
            return n

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
            flags = n.flags
            return AssName(name, flags)

        if isinstance(n, Discard):
            expr = n.expr
            return Discard(descend(expr))

        if isinstance(n, UnarySub):
            return LLVMRuntimeNeg(descend(n.expr))

        if isinstance(n, AssAttr):
            return n

        if isinstance(n, SetAttr):
            return CallFunc(Name('set_attr'), [Name(n.obj), n.attr, descend(n.expr)])

        if isinstance(n, HasAttr):
            return InjectFrom('bool', CallFunc(Name('has_attr'), [Name(n.obj), n.attr]))

        if isinstance(n, GetAttr):
            print n
            return CallFunc(Name('get_attr'), [Name(n.obj), n.attr])

        if isinstance(n, Getattr):
            print n
            return CallFunc(Name('get_attr'), [descend(n.expr), n.attrname])
        
        if isinstance(n, CallFunc):
            #TODO: Can we ssay this? Is the only non user function 
            # called going to be input?
            try:
                if n.node.name == 'input':
                    node = n.node
                    args = n.args
                    return CallFunc(descend(node), [descend(arg) for arg in args], None, None)
            except Exception:
                pass
            return function_polymorphism(n)

        if isinstance(n, Compare):
            exp_left = descend(n.expr)
            (op, exp_right) = (n.ops[0][0], descend(n.ops[0][1]))
            
            #Much simpler if we do an EXACT comparison
            if op == 'is':
                return InjectFrom('bool', CompareExactly(exp_left, exp_right))      

            def result(l, r):
                return IfExp(InjectFrom('bool', CompareTag(l, INT_TYPE)),
                             InjectFrom('bool', Compare(ProjectTo('bool', l), [(op, ProjectTo('bool', r))])),
                             IfExp(InjectFrom('bool', CompareTag(l, BOOL_TYPE)),
                                   InjectFrom('bool', Compare(ProjectTo('bool', l), [(op, ProjectTo('bool', r))])),
                                   InjectFrom('bool', CallFunc(Name('equal'), 
                                       [ProjectTo('big', l), ProjectTo('big', r)]))))
                                         
            if op == "==":
                return LLVMRuntimeCmpEq(exp_left, exp_right)
            elif op == "!=":
                return LLVMRuntimeCmpNEq(exp_left, exp_right)
            else:
                raise Exception("unsupported op", op)

        if isinstance(n, Add):
            left = descend(n.left)
            right = descend(n.right)
            return LLVMRuntimeAdd(left, right)

        if isinstance(n, Or):
            left = descend(n.nodes[0])
            right = descend(n.nodes[1])

            def ifex(l):
                return IfExp(InjectFrom('bool', CallFunc(Name('is_true'), [l], None, None)),
                             l,
                             right)

            return letify(left, lambda l: ifex(l))

        if isinstance(n, And):
            left = descend(n.nodes[0])
            right = descend(n.nodes[1])

            def ifex(l):
                return IfExp(InjectFrom('bool', CallFunc(Name('is_true'), [l], None, None)),
                             right,
                             l)

            return letify(left, lambda l: ifex(l))

        if isinstance(n, Not):
            expr = n.expr
            return IfExp(descend(expr), descend(Name('False')), descend(Name('True')))
        
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

        if isinstance(n, Function):
            return Assign([AssName(n.name, 'OP_ASSIGN')], InjectFrom('big', Lambda(n.argnames, n.defaults, n.flags, descend(n.code))))
        if isinstance(n, Lambda):
            return InjectFrom('big', Lambda(n.argnames, n.defaults, n.flags, Stmt([Return(descend(n.code))])))

        if isinstance(n, Return):
            return Return(descend(n.value))

        if isinstance(n, Class):
            return Class(n.name, n.bases, None, descend(n.code))

        if isinstance(n, str):
            return n

        raise Exception("Unsupported type %s" % n.__class__.__name__)

    return descend(ast_)
if __name__ == "__main__":
    p0 = '''
class C:
    0
'''
    import compiler 
    import uniquify
    import declassify
    original_ast = compiler.parse(p0)
    unique = uniquify.unique(compiler.parse(p0))
    declassified = declassify.declassify(unique)
    
    print declassified
