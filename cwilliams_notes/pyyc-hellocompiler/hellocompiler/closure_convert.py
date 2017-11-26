from compiler.ast import *
from ast_types import *
from uniquify import heapify_vars
import freevars
import values_variables as vv

lambda_count = 0
def closure_convert(ast_):

    def get_lambda_name():
        global lambda_count
        name = "__lambda_name_%s" % lambda_count
        lambda_count += 1
        return name

    def descend(n):
        if isinstance(n, Module):
            doc = n.doc
            node = n.node
            (code, funs) = descend(node)
            return (Module(doc, code), funs)

        if isinstance(n, Stmt):
            nodes = n.nodes
            codes = []
            funss = []
            for node in nodes:
                (code, funs) = descend(node)
                codes.append(code)
                funss += funs
            return (Stmt(codes), funss)

        if isinstance(n, Name):
            return (n, [])

        if isinstance(n, Const):
            return (n, [])

        if isinstance(n, Bool):
            return (n, [])

        if isinstance(n, Let):
            (codev, funv) = descend(n.var)
            (coder, funr) = descend(n.rhs)
            (codeb, funb) = descend(n.body)
            return (Let(codev, coder, codeb), funv + funr + funb)

        if isinstance(n, InjectFrom):
            (code, funs) = descend(n.arg)
            return (InjectFrom(n.typ, code), funs)

        if isinstance(n, CompareTag):
            (code, funs) = descend(n.var)
            return (CompareTag(code, n.tag_type), funs)

        if isinstance(n, Add):
            (codel, funl) = descend(n.left)
            (coder, funr) = descend(n.right)
            return (Add((codel, coder)), funl + funr)

        if isinstance(n, ProjectTo):
            (code, fun) = descend(n.arg)
            return (ProjectTo(n.typ, code), fun)

        if isinstance(n, Printnl):
            nodes = n.nodes
            dest = n.dest
            codes = []
            funs = []
            for node in nodes:
                (code, fun) = descend(node)
                codes.append(code)
                funs += fun
            return (Printnl(codes, dest), funs)

        if isinstance(n, Assign):
            nodes = n.nodes
            expr = n.expr
            codes = []
            funs = []
            for node in nodes:
                (code, fun) = descend(node)
                codes.append(code)
                funs += fun
            (ecode, efuns) = descend(expr)
            funs += efuns
            return (Assign(codes, ecode), efuns) 

        if isinstance(n, AssName):
            name = n.name
            flags = n.flags
            return (n, [])

        if isinstance(n, AssAttr):
            return (n, [])

        if isinstance(n, Discard):
            expr = n.expr
            (code, funs) = descend(expr)
            return (Discard(code), funs)

        if isinstance(n, UnarySub):
            (code, fun) = descend(n.expr)
            return (UnarySub(code), fun)

        if isinstance(n, CallFunc):
            node = n.node
            args = n.args
            (ncode, nfun) = descend(node)
            codes = []
            funs = nfun
            for arg in args:
                (code, fun) = descend(arg)
                codes.append(code)
                funs += fun
            return (CallFunc(ncode, codes, None, None), funs)

        if isinstance(n, CallUserFunc):
            node = n.node
            args = n.args
            (ncode, nfun) = descend(node)
            codes = []
            funs = nfun
            for arg in args:
                (code, fun) = descend(arg)
                codes.append(code)
                funs += fun
            return (CallUserFunc(ncode, codes), funs)

        if isinstance(n, List):
            codes = []
            funs = []
            for node in n.nodes:
                (code, fun) = descend(node)
                codes.append(code)
                funs += fun
            return (List(codes), funs)

        if isinstance(n, Dict):
            items = n.items
            codes = []
            funs = []
            for kv in items:
                (kcode, kfuns) = descend(kv[0])
                (vcode, vfuns) = descend(kv[1])
                codes.append((kcode, vcode))
                funs += kfuns + vfuns
            return (Dict(codes), funs)

        if isinstance(n, Subscript):
            expr = n.expr
            flags = n.flags
            subs = n.subs
            (ecode, efun) = descend(expr)
            codes = []
            funs = efun
            for sub in subs:
                (code, fun) = descend(sub)
                codes.append(code)
                funs += fun
            return (Subscript(ecode, flags, codes), funs)

        if isinstance(n, IfExp):
            test = n.test
            then = n.then
            else_ = n.else_
            (tcode, tfuns) = descend(test)
            (thcode, thfuns) = descend(then)
            (ecode, efuns) = descend(else_)
            return (IfExp(tcode, thcode, ecode), tfuns + thfuns + efuns)

        if isinstance(n, CompareExactly):
            (lcode, lfuns) = descend(n.l)
            (rcode, rfuns) = descend(n.r)
            return (CompareExactly(lcode, rcode), lfuns + rfuns)

        if isinstance(n, Compare):
            (ecode, efuns) = descend(n.expr) 

            opcodes = []
            opfuns = []
            for op in n.ops:
                (opcode, opfun) = descend(op[1])
                opfuns += opfun
                opcodes.append((op[0], opcode))
            
            return (Compare(ecode, opcodes), efuns + opfuns)

        if isinstance(n, LLVMRuntimeAdd):
            (lcode, lfuns) = descend(n.left)
            (rcode, rfuns) = descend(n.right)
            return (LLVMRuntimeAdd(lcode, rcode), lfuns + rfuns)

        if isinstance(n, LambdaHeapified):
            
            fvars = freevars.free_vars(n).intersection(heapify_vars)
            #fvars = freevars.free_vars(n.code).intersection(heapify_vars) - set(n.original_argnames) - set(n.localvars)
            print "argnames, fvars, paraminits, heapify_vars", n.argnames, fvars, n.paraminits, heapify_vars

            decorators = None
            fname = get_lambda_name()
            argnames = ['__free_vars'] + n.argnames
            defaults = []
            flags = 0
            doc = None
            (code, funs) = descend(n.code)

            free_var_assmt = []
            for i, fvar in enumerate(fvars):
                free_var_assmt.append(
                        Assign([AssName(fvar, 'OP_ASSIGN')], 
                               Subscript(Name('__free_vars'), 'OP_APPLY', [Const(i)])))

            new_code = Stmt(free_var_assmt + n.localinits + n.paraminits + code.nodes)
            f = Function(decorators, fname, argnames, defaults, flags, doc, new_code)
            funs = [f] + funs
            closure = CallFunc(Name('create_closure'), 
                               [vv.LabelValue(fname), List([Name(fvar) for fvar in fvars])])
            return (closure, funs)

        if isinstance(n, Return):
            (code, funs) = descend(n.value)
            return (Return(code), funs)

        if isinstance(n, Class):
            (code, funs) = descend(n.code)
            return (Class(n.name, n.bases, None, code), funs)

        if isinstance(n, str):
            return (n, [])

        raise Exception("Unsupported type in closure_convert %s" % n.__class__.__name__)

    return descend(ast_)

if __name__ == '__main__':
    p0 = '''
def test(x):
    a = lambda a: a + a + 4
    b = a(x)
    def test1(y):
        return y + 1
    b = test1(b)
    return b

a = test(2)
b = test(4)
print a
print b
'''
    import compiler 
    import uniquify
    import explicate
    import heapify
    import flattener
    import flattened_to_assembly
    f = flattener.Flattener()
    original_ast = compiler.parse(p0)
    unique = uniquify.unique(compiler.parse(p0))
    new_ast = explicate.explicate(unique)
    heapified = heapify.heapify(new_ast)
    converted = closure_convert(heapified)
    flts = f.flatten(converted[0])

    print converted[0]
    print "==========================="
    for fun in converted[1]:
        for l in f.flatten(fun):
            print l
    for flt in flts:
        print flt

