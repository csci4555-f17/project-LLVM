import assembly_types as t
import x86_ir as ir
import values_variables as vv
import registers as r

def translate(a_type):

    if isinstance(a_type, t.Assign):
        var = a_type.var
        expr = a_type.simple
        if isinstance(expr, t.Add):
            left = expr.left
            right = expr.right
            return [ir.Mov(right, var),
                    ir.Add(left, var)]

        if isinstance(expr, t.Sub):
            left = expr.left
            right = expr.right
            return [ir.Mov(right, var),
                    ir.Sub(left, var)]
        
        if isinstance(expr, t.Neg):
            val = expr.val
            return [ir.Mov(val, var),
                    ir.Neg(var)]

        if isinstance(expr, vv.Atom):
            return [ir.Mov(expr.v, var)]

        if isinstance(expr, t.Input):
            return [ir.Input(),
                    ir.Mov(r.EAX(), var)]

    elif isinstance(a_type, t.Print):
        var = a_type.val
        return [ir.Push(var),
                ir.Print(),
                ir.Add(vv.Value(4), r.ESP())]

    elif isinstance(a_type, Discard):
        expr = a_type.simple
        if isinstance(expr, t.Input):
            return [ir.Input()]
        else:
            return []

def generate(l, num_vars):
    instructions = []
    for l_i in l:
        instructions = instructions + translate(l_i)
    p = ir.Program(instructions, num_vars)
    return str(p)

