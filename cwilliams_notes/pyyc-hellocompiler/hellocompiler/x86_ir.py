import values_variables as vv
import liveness_analysis as la
import interference_graph as ig
import instruction_updater as iu
import registers as r


class Section():
    def __init__(self, section_name):
        self.section_name = section_name
    def __str__(self):
        return ".%s" % self.section_name

class StringConstant():
    def __init__(self, s):
        self.s = s
    def __str__(self):
        return "    .string \"%s\"" % self.s

class Label():
    def __init__(self, label_name):
        self.label_name = label_name
    def __str__(self):
        return "%s:" % self.label_name

class x86instruction():
    def __init__(self, arity, name, *args):
        self.arity = arity
        self.name = name
        self.args = args
        self.l_before = None
        self.l_after = None

    def reads(self):
        return list(self._reads)

    def writes(self):
        return list(self._writes)

    def update_var(*args):
        pass

    def _format_args(self):
        if self.arity == 0:
            return ""
        return ", ".join([str(a) for a in self.args])

    def __str__(self):
        return "    %s %s" % (self.name, self._format_args())

    def __repr__(self):
        return "    %s %s" % (self.name, self._format_args())

class Cmp(x86instruction):
    def __init__(self, l, r):
        x86instruction.__init__(self, 2, "cmpl", l, r)
        self.l = l
        self.r = r
    
    def set_l(self, newval):
        raise NotImplementedError

    def set_r(self, newval):
        raise NotImplementedError

    def update_var(self, var, to):
        raise NotImplementedError

class JmpEq(x86instruction):
    def __init__(self, label):
        x86instruction.__init__(self, 2, "je", label)
        self.label = label
    
    def set_l(self, newval):
        raise NotImplementedError

    def set_r(self, newval):
        raise NotImplementedError

    def update_var(self, var, to):
        raise NotImplementedError

class JmpNEq(x86instruction):
    def __init__(self, label):
        x86instruction.__init__(self, 2, "jne", label)
        self.label = label
    
    def set_l(self, newval):
        raise NotImplementedError

    def set_r(self, newval):
        raise NotImplementedError

    def update_var(self, var, to):
        raise NotImplementedError

class Jmp(x86instruction):
    def __init__(self, label):
        x86instruction.__init__(self, 2, "jmp", label)
        self.label = label
    
    def set_l(self, newval):
        raise NotImplementedError

    def set_r(self, newval):
        raise NotImplementedError

    def update_var(self, var, to):
        raise NotImplementedError

class MovZB(x86instruction):
    def __init__(self, l, r):
        x86instruction.__init__(self, 2, "movzbl", l, r)
        self.l = l
        self.r = r

class Mov(x86instruction):
    def __init__(self, l, r):
        x86instruction.__init__(self, 2, "movl", l, r)
        self.l = l        
        self.r = r
        self._writes = set()
        self._reads = set()
        if vv.is_variable(r):
            self._writes = set([r])
        if vv.is_variable(l):
            self._reads.add(l)

    def set_l(self, newval):
        self.l = newval
        self.reset_parent()

    def set_r(self, newval):
        self.r = newval
        self.reset_parent()

    def reset_parent(self):
        x86instruction.__init__(self, 2, "movl", self.l, self.r)

    def update_var(self, var, to):
        if vv.is_variable(self.l):
            if self.l == var:
	            self.l = to
        if vv.is_variable(self.r):
            if self.r == var:
	            self.r = to
        self.reset_parent() 

class Add(x86instruction):
    def __init__(self, l, r):
        x86instruction.__init__(self, 2, "addl", l, r)
        self.l = l
        self.r = r
        self._reads = set()
        self._writes = set()
        if vv.is_variable(r):
            self._reads = set([r])
            self._writes = set([r])
        if vv.is_variable(l):
            self._reads.add(l)

    def reset_parent(self):
        x86instruction.__init__(self, 2, "addl", self.l, self.r)

    def set_l(self, newval):
        self.l = newval
        self.reset_parent()

    def set_r(self, newval):
        self.r = newval
        self.reset_parent()

    def update_var(self, var, to):
        if vv.is_variable(self.l):
            if self.l == var:
                self.l = to
        if vv.is_variable(self.r):
            if self.r == var:
	            self.r = to
        self.reset_parent()

class Sub(x86instruction):
    def __init__(self, l, r):
        x86instruction.__init__(self, 2, "subl", l, r)
        self.l = l
        self.r = r
        self._reads = set([r])
        if vv.is_variable(l):
            self._reads.add(l)
        self._writes = set([r])

    def reset_parent(self):
        x86instruction.__init__(self, 2, "subl", self.l, self.r)

    def set_l(self, newval):
        self.l = newval
        self.reset_parent()

    def set_r(self, newval):
        self.r = newval
        self.reset_parent()
        
    def update_var(self, var, to):
        if vv.is_variable(self.l):
            if self.l == var:
	            self.l = to
        if vv.is_variable(self.r):
            if self.r == var:
	            self.r = to
        self.reset_parent()
        
class SubHeader(x86instruction):
    def __init__(self, l, r):
        x86instruction.__init__(self, 2, "subl", l, r)
        self.l = l
        self.r = r
        self._reads = set([r])
        if vv.is_variable(l):
            self._reads.add(l)
        self._writes = set([r])

    def reset_parent(self):
        x86instruction.__init__(self, 2, "subl", self.l, self.r)

    def set_l(self, newval):
        self.l = newval
        self.reset_parent()

    def set_r(self, newval):
        self.r = newval
        self.reset_parent()
        
    def update_var(self, var, to):
        if vv.is_variable(self.l):
            if self.l == var:
	            self.l = to
        if vv.is_variable(self.r):
            if self.r == var:
	            self.r = to
        self.reset_parent()

class Neg(x86instruction):
    def __init__(self, v):
        x86instruction.__init__(self, 1, "negl", v)
        self.v = v
        self._reads = set()
        self._writes = set()
        if vv.is_variable(v):
            self._reads.add(v)
            self._writes.add(v)

    def reset_parent(self):
        x86instruction.__init__(self, 1, "negl", self.v)

    def update_var(self, var, to):
        if vv.is_variable(self.v):
            if self.v == var:
	            self.v = to
        self.reset_parent()

class Print(x86instruction):
    def __init__(self):
        x86instruction.__init__(self, 1, "call", "print_any")
        self._reads = set()
        self._writes = set()

class Input(x86instruction):
    def __init__(self):
        x86instruction.__init__(self, 1, "call", "input")
        self._reads = set()
        self._writes = set()

class CallFunc(x86instruction):
    def __init__(self, fname):
        x86instruction.__init__(self, 1, "call", fname)
        self._reads = set()
        self._writes = set()

class CallStar(x86instruction):
    def __init__(self, fname):
        x86instruction.__init__(self, 1, "call *", fname)
        self.fname = fname

class Pop(x86instruction):
    def __init__(self, register):
        x86instruction.__init__(self, 1, "popl", register)
        self.register = register

class Push(x86instruction):
    def __init__(self, register):
        x86instruction.__init__(self, 1, "pushl", register) 
        self.register = register
        self._reads = set()
        self._writes = set()
        if vv.is_variable(register):
            self._reads.add(register)

    def reset_parent(self):
        x86instruction.__init__(self, 1, "pushl", self.register)

    def update_var(self, var, to):
        if vv.is_variable(self.register):
            if self.register == var:
	            self.register = to
        self.reset_parent()

class Leave(x86instruction):
    def __init__(self):
        x86instruction.__init__(self, 0, "leave", None) 
        self._reads = set()
        self._writes = set()

class ShiftRight(x86instruction):
    def __init__(self, shift_by, reg):
        shift = "$0x%s" % shift_by
        x86instruction.__init__(self, 2, "sarl", shift, reg)
        self.shift_by = shift_by
        self.reg = reg

class ShiftLeft(x86instruction):
    def __init__(self, shift_by, reg):
        shift = "$0x%s" % shift_by
        x86instruction.__init__(self, 2, "sall", shift, reg)
        self.shift_by = shift_by
        self.reg = reg

class Or(x86instruction):
    def __init__(self, mask, reg):
        self.mask = mask
        formatted_mask = "$0x%s" % mask
        x86instruction.__init__(self, 2, "orl", formatted_mask, reg)
        self.reg = reg

class And(x86instruction):
    def __init__(self, mask, reg):
        self.mask = mask
        formatted_mask = "$0x%s" % mask
        x86instruction.__init__(self, 2, "andl", formatted_mask, reg)
        self.reg = reg

class SetE(x86instruction):
    def __init__(self, reg):
        x86instruction.__init__(self, 1, "sete", reg)
        self.reg = reg

class SetNE(x86instruction):
    def __init__(self, reg):
        x86instruction.__init__(self, 1, "setne", reg)
        self.reg = reg

class Ret(x86instruction):
    def __init__(self):
        x86instruction.__init__(self, 0, "ret", None)
        self._reads = set()
        self._writes = set()

class IfExp():
    def __init__(self, test_var, then, else_, name):
        self.test_var = test_var
        self.else_label_name = '__ifexpr_else_branch_%s' % name
        self.done_label_name = '__ifexpr_done_%s' % name
        self.else_label = Label(self.else_label_name)
        self.done_label = Label(self.done_label_name)
        self.test_instructions = [
                Push(self.test_var),
                CallFunc('is_true'),
                Add(vv.Value(4), r.ESP()),
                Cmp(vv.Value(0), r.EAX()),
                JmpEq(self.else_label_name)]
        self.then = then
        self.then.append(Jmp(self.done_label_name))
        self.else_ = [self.else_label] + else_
        self.else_.append(self.done_label)
        self.name = name

    def __repr__(self):
        return '''
{test_instrs}
{then_instrs}
{else_instrs}'''.format(
                  test_instrs="\n".join([str(i) for i in self.test_instructions]),
                  then_instrs="\n".join([str(i) for i in self.then]),
                  else_instrs="\n".join([str(i) for i in self.else_])
                  )


    def __str__(self):
        return '''
{test_instrs}
{then_instrs}
{else_instrs}'''.format(
                  test_instrs="\n".join([str(i) for i in self.test_instructions]),
                  then_instrs="\n".join([str(i) for i in self.then]),
                  else_instrs="\n".join([str(i) for i in self.else_])
                  )


def header():
    return [".global main",
            "    main:",
            Push(r.EBP()),
            Mov(r.ESP(), r.EBP()) ]

def footer():
    return [Mov(vv.Value(0), r.EAX()),
            Leave(),
            Ret(),
            ""]
def function_push():
    return [Push(r.EBX()),
            Push(r.ESI()),
            Push(r.EDI())]

def function_header(fname):
    return [Label(fname),
            Push(r.EBP()),
            Mov(r.ESP(), r.EBP())]

def function_footer():
    return [Pop(r.EDI()),
            Pop(r.ESI()),
            Pop(r.EBX()),
            Leave(),
            Ret()]

def get_optimized_instructions(instructions, num_vars):
    lv = la.liveness_analysis(instructions)
    ifg = ig.interference_graph(instructions, lv, num_vars)
    cg = ig.color_graph(ifg)
    return iu.instructions_with_colors(instructions, cg, num_vars)

class Program():
    def __init__(self, instructions, num_vars):
        self.instructions = instructions
        self.complete = [
            ".global main",
            "main:",
            Push("%ebp"),
            Mov("%esp", "%ebp"),
            ""] + instructions + [
            Mov("$0", "%eax"),
            Leave(),
            Ret()
            ]
        #self.liveness = la.liveness_analysis(instructions)
        #self.interference_graph = ig.interference_graph(instructions, self.liveness, num_vars)
        #self.colored_graph = ig.color_graph(self.interference_graph)
        #self.optimized_instructions = iu.instructions_with_colors(self.instructions, self.colored_graph, num_vars)
        self.complete = [
            ".global main",
            "main:",
            Push("%ebp"),
            Mov("%esp", "%ebp"),
            ""] + self.optimized_instructions + [
            Mov("$0", "%eax"),
            Leave(),
            Ret()
            ]
        for i in self.complete:
            print i
     
    def __str__(self):
        return "\n".join([str(i) for i in self.complete])
