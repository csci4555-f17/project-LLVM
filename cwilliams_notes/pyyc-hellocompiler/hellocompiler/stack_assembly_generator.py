import assembly_types as t
import x86_ir as ir
import registers as r
import values_variables as vv
import explicate
import flattener

def pop_stack(n=1):
    return ir.Add(vv.Value(4*n), r.ESP())

class StackAssemblyGenerator():
    def __init__(self, flattened_instructions, num_vars):
        self.flattened_instructions = flattened_instructions
        self.num_vars = num_vars
        self.scope = 0

    def next_scope(self):
        cur = self.scope
        self.scope += 1
        return cur
    
    def current_scope(self):
        return self.scope

    def convert_to_int(self):
        return [ir.Push(r.EAX()),
                ir.CallFunc("inject_int"),
                ir.Add(vv.Value(4), r.ESP())]

    def header(self):
        return [".global main",
                "    main:",
                ir.Push(r.EBP()),
                ir.Mov(r.ESP(), r.EBP()),
                ir.Sub(vv.Value(4*(self.num_vars + 1)), r.ESP())]

    def footer(self):
        return [ir.Mov(vv.Value(0), r.EAX()),
                ir.Leave(),
                ir.Ret(),
                ""]

    def generate(self):
        return self.header() + self.multi_handler(self.flattened_instructions) + self.footer()

    def handler(self, instr):
        if isinstance(instr, t.Assign):
            assmt = instr.assmt
            expr = instr.simple
            print assmt, type(expr)
            print self.handler(expr)
            print self.assign_handler(assmt)
            return self.handler(expr) + self.assign_handler(assmt)
        if isinstance(instr, vv.Value):
            return self.get_value_instructions(instr)
        if isinstance(instr, vv.Variable):
            return self.get_var_instructions(instr)
        if isinstance(instr, vv.BoolValue):
            return self.get_bool_instructions(instr)
        if isinstance(instr, t.Print):
            return self.handler(instr.val) + self.print_instructions()
        if isinstance(instr, t.Input):
            return self.input_instructions()
        if isinstance(instr, t.Neg):
            return self.get_neg_instructions(instr)
        if isinstance(instr, t.Add):
            return self.get_add_instructions(instr)
        if isinstance(instr, t.IfExp):
            return self.if_exp_instructions(instr)
        if isinstance(instr, t.CmpEq):
            return self.are_equal_instructions(instr)
        if isinstance(instr, t.List):
            return self.create_list_instructions(instr)
        if instr == None:
            return []

    def assign_handler(self, instr):
        if isinstance(instr, vv.Variable):
            return self.set_var_instructions(instr)
        else:
            raise Exception("%s not supported" % instr)

    def multi_handler(self, instructions):
        x86_instructions = []
        for instr in instructions:
            x86_instructions += self.handler(instr)
        return x86_instructions

    def are_equal_instructions(self, instr):
        return (self.handler(instr.left) +
                [ir.Push(r.EAX())] +
                 self.handler(instr.right) +
                [ir.Push(r.EAX()),
                 ir.CallFunc('equal_any'),
                 pop_stack(2),
                 ir.Push(r.EAX()),
                 ir.CallFunc('inject_int'),
                 pop_stack()])

    def if_exp_instructions(self, instr):
        scope = self.next_scope()
        test_var = instr.test_var
        then = instr.then[0] + [instr.then[1]]
        else_ = instr.else_[0] + [instr.else_[1]]
        test_instructions = self.handler(test_var)
        return (self.handler(test_var) + 
                [ir.Push(r.EAX()),
                 ir.CallFunc('is_true'),
                 pop_stack(),
                 ir.Cmp(vv.Value(0), r.EAX()),
                 ir.JmpEq("__else_branch_%s" % scope)] +
                 self.multi_handler(then) +
                [ir.Jmp("__if_exp_done_%s" % scope),
                 ir.Label("__else_branch_%s" % scope)] +
                 self.multi_handler(else_) + 
                [ir.Label("__if_exp_done_%s" % scope)])


    def is_int_instructions(self):
        return [ir.Push(r.EAX()),
                ir.CallFunc('is_int'),
                pop_stack()]

    def is_bool_instructions(self):
        return [ir.Push(r.EAX()),
                ir.CallFunc('is_bool'),
                pop_stack()]

    def is_big_instructions(self):
        return [ir.Push(r.EAX()),
                ir.CallFunc('is_big'),
                pop_stack()]

    def get_add_instructions(self, instr):
        scope = self.next_scope()
        left = instr.left
        right = instr.right
        return ( self.handler(left) + 
                [ir.Push(r.EAX())] + 
                 self.is_big_instructions() + 
                [ir.Cmp(vv.Value(0), r.EAX()),
                 ir.JmpNEq('__add_big_%s' % scope)] +
                 self.handler(right) + 
                [ir.Push(r.EAX())] + 
                 self.is_big_instructions() +
                [ir.Cmp(vv.Value(0), r.EAX()),
                 ir.JmpNEq('__add_type_error_%s' % scope),
                 ir.Mov(r.ESPDeref(), r.EAX()),
                 ir.ShiftRight(2, r.EAX()),
                 pop_stack(),
                 ir.Mov(r.EAX(), r.EBX()),
                 ir.Mov(r.ESPDeref(), r.EAX()),
                 ir.ShiftRight(2, r.EAX()),
                 pop_stack(),
                 ir.Add(r.EBX(), r.EAX()),
                 ir.Push(r.EAX()),
                 ir.CallFunc('inject_int'),
                 pop_stack(),
                 ir.Jmp('__add_done_%s' % scope),
                 ir.Label('__add_big_%s' % scope)] + 
                 self.handler(right) +
                [ir.Push(r.EAX())] + 
                 self.is_big_instructions() + 
                [ir.Cmp(vv.Value(0), r.EAX()),
                 ir.JmpEq('__add_type_error_%s' % scope),
                 ir.CallFunc('project_big'),
                 pop_stack(),
                 ir.Mov(r.EAX(), r.EBX()),
                 ir.CallFunc('project_big'),
                 pop_stack(),
                 ir.Push(r.EBX()),
                 ir.Push(r.EAX()),
                 ir.CallFunc('add'),
                 ir.Push(r.EAX()),
                 ir.CallFunc('inject_big'),
                 pop_stack(3),
                 ir.Jmp('__add_done_%s' % scope),
                 ir.Label('__add_type_error_%s' % scope),
                 pop_stack(2),
                 ir.CallFunc('abort'),
                 ir.Label('__add_done_%s' % scope)])

    def get_neg_instructions(self, instr):
        scope = self.next_scope()
        val_instructions = self.handler(instr.val)

        neg_instructions = (
               [ir.Push(r.EAX())] +
                self.is_big_instructions() + 
               [ir.Cmp(vv.Value(0), r.EAX()),
                ir.JmpNEq('___neg_abort_%s' % scope),
                ir.Mov(r.ESPDeref(), r.EAX()),
                ir.ShiftRight(2, r.EAX()),
                pop_stack(),
                ir.Neg(r.EAX()),
                ir.Push(r.EAX()),
                ir.CallFunc('inject_int'),
                pop_stack(),
                ir.Jmp('___neg_done_%s' % scope),
                ir.Label('___neg_abort_%s' % scope),
                pop_stack(),
                ir.CallFunc('abort'),
                ir.Label('___neg_done_%s' % scope)])
        return val_instructions + neg_instructions

    def input_instructions(self):
        return [ir.Input()]

    def print_instructions(self):
        return [ir.Push(r.EAX()),
                ir.Print(),
                pop_stack()]

    def get_bool_instructions(self, instr):
        return [ir.Mov(vv.Value(int(instr.v)), r.EAX()),
                ir.Push(r.EAX()),
                ir.CallFunc('inject_bool'),
                pop_stack()]

    def get_value_instructions(self, instr):
        return [ir.Mov(instr, r.EAX()),
                ir.Push(r.EAX()),
                ir.CallFunc('inject_int'),
                pop_stack()]

    def set_var_instructions(self, instr):
        return [ir.Mov(r.EAX(), r.OffsetEBP(instr.v))]

    def get_var_instructions(self, instr):
        return [ir.Mov(r.OffsetEBP(instr.v), r.EAX())]

    
    def assign_print(self, instr):
        var = instr.val
        return [ir.Mov(r.OffsetEBP(var.v), r.EAX()),
                ir.Push(r.EAX()),
                ir.Print(),
                pop_stack()]

    def assign_assembly(self, instr):
        e = instr.simple
        v = instr.var
        assign_instrs = []
        if isinstance(e, t.Input):
            assign_instrs.append(ir.Input())
        elif isinstance(e, vv.Value):
            assign_instrs += [
                    ir.Mov(e, r.EAX()),
                    ir.Push(r.EAX()),
                    ir.CallFunc('inject_int'),
                    pop_stack()]
        elif isinstance(e, vv.Variable):
            assign_instrs += [
                    ir.Mov(r.OffsetEBP(e.v), r.EAX())]
        elif isinstance(e, vv.BoolValue):
            assign_instrs += [
                    ir.Mov(e, r.EAX()),
                    ir.Push(r.EAX()),
                    ir.CallFunc('inject_bool'),
                    pop_stack()]
        elif isinstance(e, t.Add):
            assign_instrs += self.add_instructions(e)
        else:
            raise Exception("Nothing matched for type %s" % type(e))
        assign_instrs.append(ir.Mov(r.EAX(), r.OffsetEBP(v.v)))
        return assign_instrs


    def int_to_pyobj(self, i):
        return [ir.Push(vv.Value(i)),
                ir.CallFunc('inject_int'),
                pop_stack()]

    def set_subscript(self, idx, v):
        v_instrs = self.handler(v)
        idx_instrs = self.handler(idx)
        return (
               [ir.Push(r.EAX())] + 
                self.handler(v) + 
               [ir.Push(r.EAX())] +
                self.handler(idx) +
               [ir.Mov(r.ESPDeref(), r.EBX()),
                pop_stack(),
                ir.Mov(r.ESPDeref(), r.ECX()),
                pop_stack(),
                ir.Push(r.EBX()),
                ir.Push(r.EAX()),
                ir.Push(r.ECX()),
                ir.CallFunc('set_subscript'),
                pop_stack(3)])
               

    def create_list_instructions(self, instr):
        length = instr.length
        subs = instr.subscripts

        instrs = self.int_to_pyobj(length) + [
                  ir.Push(r.EAX()),
                  ir.CallFunc('create_list'),
                  pop_stack(),
                  ir.Push(r.EAX()),
                  ir.CallFunc('inject_big'),
                  ir.Push(r.EAX())]

        for i, sub in enumerate(subs):
            instrs += self.set_subscript(vv.Value(i), sub)
            instrs += [ir.Mov(r.ESPDeref(), r.EAX())]

        instrs += [pop_stack()]
        return instrs

    def assign_if_exp(self, instr):
        c = self.next_scope()
        result_var = instr.result_var
        test_var = instr.test_var
        then = instr.then.stmts
        else_ = instr.else_.stmts

        true_label = "__if_exp_then_%s" % c
        false_label = "__if_exp_else_%s" % c
        done_label = "__if_exp_done_%s" % c

        instrs = [ir.Mov(r.OffsetEBP(test_var.v), r.EAX())]
        instrs += self.is_truthy(true_label, false_label)

        print "then", then
        print "else_", else_
        false_logic = [ir.Label(false_label)] + self.multi_handler(else_) + [ir.Jmp(done_label)]
        true_logic = [ir.Label(true_label)] + self.multi_handler(then) + [ir.Label(done_label)]

        return instrs + false_logic + true_logic

    def is_truthy(self, true_jump, false_jump):
        return [ir.Push(r.EAX()),
                ir.CallFunc('is_int'),
                ir.Cmp(vv.Value(0), r.EAX()),
                ir.JmpEq('not_int_truthy_%s' % self.current_scope()),
                ir.CallFunc('project_int'),
                pop_stack(),
                ir.Cmp(vv.Value(0), r.EAX()),
                ir.JmpEq(false_jump),
                ir.Jmp(true_jump),
                ir.Label('not_int_truthy_%s' % self.current_scope()),
                ir.CallFunc('is_bool'),
                ir.Cmp(vv.Value(0), r.EAX()),
                ir.JmpEq('not_bool_truthy_%s' % self.current_scope()),
                ir.CallFunc('project_bool'),
                pop_stack(),
                ir.Cmp(vv.Value(0), r.EAX()),
                ir.JmpEq(false_jump),
                ir.Jmp(true_jump),
                ir.Label('not_bool_truthy_%s' % self.current_scope()),
                ir.CallFunc('project_big'),
                pop_stack(),
                ir.Cmp(vv.Value(0), r.EAX()),
                ir.JmpEq(false_jump),
                ir.Jmp(true_jump)]

if __name__ == "__main__":
    p = '''
a = 3
b = 7
x = a + b
print x'''
    
    import compiler
    ast = explicate.explicate(compiler.parse(p))
    f = flattener.Flattener()
    f.flatten(ast)
    g = StackAssemblyGenerator(f.instructions, f.next)
    x86 = g.generate()
    print "x86 instructions >>>>>>>>>>>>>>>>>>>>>>>>>"
    for i in x86:
        print i
