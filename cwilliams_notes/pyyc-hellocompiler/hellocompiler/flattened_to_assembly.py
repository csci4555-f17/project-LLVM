import x86_ir as ir
import assembly_types as t
import values_variables as vv
import registers as r
import explicate as exp
import flattener as flt
import compiler

scope = 0
def next_scope():
    global scope
    ret = scope
    scope += 1
    return ret

def generate(flattened_instructions):
    instructions = []

    for i in flattened_instructions:
        if isinstance(i, t.Assign):
            assmt = i.assmt
            expr = i.simple

            if isinstance(expr, vv.Value):
                instructions.append(ir.Mov(expr, assmt))

            elif isinstance(expr, vv.Variable):
                instructions.append(ir.Mov(expr, assmt))

            elif isinstance(expr, vv.BoolValue):
                instructions.append(ir.Mov(expr, assmt))

            elif isinstance(expr, t.InjectInt):
                instructions.append(ir.Mov(expr.val, assmt))
                instructions.append(ir.ShiftLeft(2, assmt))

            elif isinstance(expr, t.InjectBig):
                instructions.append(ir.Mov(expr.val, assmt))
                instructions.append(ir.Add(vv.Value(3), assmt))

            elif isinstance(expr, t.InjectBool):
                instructions.append(ir.Mov(expr.val, assmt))
                instructions.append(ir.ShiftLeft(2, assmt))
                instructions.append(ir.Add(vv.Value(1), assmt))

            elif isinstance(expr, t.CallFunc):
                c = 0
                for arg in reversed(expr.args):
                    c += 1
                    instructions.append(ir.Push(arg))

                instructions.append(ir.CallFunc(expr.func_name))
                
                if c > 0:
                    instructions.append(ir.Add(vv.Value(4*c), r.ESP()))

                instructions.append(ir.Mov(r.EAX(), assmt))

            elif isinstance(expr, t.ProjectInt):
                instructions.append(ir.Mov(expr.val, assmt))
                instructions.append(ir.ShiftRight(2, assmt))
            
            elif isinstance(expr, t.ProjectBool):
                instructions.append(ir.Mov(expr.val, assmt))
                instructions.append(ir.ShiftRight(2, assmt))

            elif isinstance(expr, t.ProjectBig):
                instructions.append(ir.Mov(expr.val, assmt))
                instructions.append(ir.ShiftRight(2, assmt))
                instructions.append(ir.ShiftLeft(2, assmt))

            elif isinstance(expr, t.Add):
                instructions.append(ir.Mov(expr.right, assmt))
                instructions.append(ir.Add(expr.left, assmt))

            elif isinstance(expr, t.Input):
                instructions.append(ir.Input())
                instructions.append(ir.Mov(r.EAX(), assmt))

            elif isinstance(expr, t.Neg):
                instructions.append(ir.Mov(expr.val, assmt))
                instructions.append(ir.Neg(assmt))

            elif isinstance(expr, t.List):
                instructions.append(ir.Push(expr.length))
                instructions.append(ir.CallFunc('create_list'))
                instructions.append(ir.Add(vv.Value(4), r.ESP()))
                instructions.append(ir.Mov(r.EAX(), assmt))

            elif isinstance(expr, t.GetSubscript):
                var = expr.pyobj_var
                key = expr.key

                instructions += [ir.Push(key),
                                 ir.Push(var),
                                 ir.CallFunc('get_subscript'),
                                 ir.Add(vv.Value(8), r.ESP()),
                                 ir.Mov(r.EAX(), assmt)]

            elif isinstance(expr, t.Dict):
                instructions.append(ir.CallFunc('create_dict'))
                instructions.append(ir.Mov(r.EAX(), assmt))

            elif isinstance(expr, t.CmpEq):
                instructions.append(ir.Cmp(expr.left, expr.right))
                instructions.append(ir.SetE(r.AL()))
                instructions.append(ir.MovZB(r.AL(), assmt))

            elif isinstance(expr, t.CmpNEq):
                instructions.append(ir.Cmp(expr.left, expr.right))
                instructions.append(ir.SetNE(r.AL()))
                instructions.append(ir.MovZB(r.AL(), assmt))

            elif isinstance(expr, t.CallStar):
                c = 0
                for arg in reversed(expr.args):
                    c += 1
                    instructions.append(ir.Push(arg))

                instructions.append(ir.CallStar(expr.func_name))
                
                if c > 0:
                    instructions.append(ir.Add(vv.Value(4*c), r.ESP()))

                instructions.append(ir.Mov(r.EAX(), assmt))

            elif isinstance(expr, r.OffsetEBP):
                instructions.append(ir.Mov(expr, assmt))

            elif expr == None:
                pass
            else:
                raise Exception("Unsuported inner instance of %s, class: %s" % (expr, expr.__class__.__name__))

        elif isinstance(i, t.IfExp):
            test = i.test_var
            then = generate(i.then)
            else_ = generate(i.else_)
            instructions.append(ir.IfExp(test, then, else_, str(next_scope())))
        
        elif isinstance(i, t.Print):
            instructions += [ir.Push(i.val),
                             ir.Print(),
                             ir.Add(vv.Value(4), r.ESP())]

        elif isinstance(i, t.SubscriptAssign):
            var = i.pyobj_var
            idx = i.key
            expr = i.assmt_var

            instructions += [ir.Push(expr),
                             ir.Push(idx),
                             ir.Push(var),
                             ir.CallFunc('set_subscript'),
                             ir.Add(vv.Value(12), r.ESP())]

        elif isinstance(i, t.Function):
            instructions += generate(i.body)

        elif isinstance(i, t.Return):
            val = i.value
            if i.value == None:
                val = vv.Value(0)
            instructions += [ir.Mov(val, r.EAX())]
            
        else:
            raise Exception("Unsuported outer instance of %s" % i)

    return instructions


if __name__ == "__main__":
    p0 = '''x = 1 + 1'''
    flattener = flt.Flattener()
    machine_code = generate(flattener.flatten(exp.explicate(compiler.parse(p0))))
    for code in machine_code:
        print code
                    
