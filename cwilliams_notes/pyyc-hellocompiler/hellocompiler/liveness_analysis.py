import x86_ir as ir
import registers as r
import explicate as exp
import flattener as flt
import flattened_to_assembly as gen
import values_variables as vv


class LivenessData():
    def __init__(self, instruction, lbefore, lafter):
        self.instruction = instruction
        self.lbefore = lbefore 
        self.lafter = lafter

    def __repr__(self):
        return '''
{ins}
--after----> {after}'''.format(before=self.lbefore,
                               after=self.lafter,
                               ins=self.instruction)

    def __str__(self):
        return '''
{ins}
--after----> {after}'''.format(before=self.lbefore,
                               after=self.lafter,
                               ins=self.instruction)

class LivenessIfExpr():
    def __init__(self, lbefore, lafter, test_instrs, then_instrs, else_instrs):
        self.lbefore = lbefore
        self.lafter = lafter
        self.test_instrs = test_instrs
        self.then_instrs = then_instrs
        self.else_instrs = else_instrs

    def __repr__(self):
        return '''
--before---> {before}
{test_ins}
{then_ins}
{else_ins}
--after----> {after}'''.format(before=self.lbefore,
                               test_ins=str(self.test_instrs),                 
                               then_ins=str(self.then_instrs),                 
                               else_ins=str(self.else_instrs),                 
                               after=self.lafter)

    def __str__(self):
        return '''
--before---> {before}
{test_ins}
{then_ins}
{else_ins}
--after----> {after}'''.format(before=self.lbefore,
                               test_ins=str(self.test_instrs),                 
                               then_ins=str(self.then_instrs),                 
                               else_ins=str(self.else_instrs),                 
                               after=self.lafter)

def liveness(instructions, inlafter=None):
    if inlafter == None:
        inlafter = set()
    ins = list(instructions)
    ins.reverse()

    liveness_instrs = []

    lafter = inlafter
    for i in ins:
        reads = set()
        writes = set()

        if isinstance(i, ir.Cmp):
            if not isinstance(i.l, vv.Literal):
                reads.add(i.l)
            writes.add(r.EAX())

        elif isinstance(i, ir.Mov):
            if not isinstance(i.l, vv.Literal):
                reads.add(i.l)
            writes.add(i.r)

        elif isinstance(i, ir.MovZB):
            if not isinstance(i.l, vv.Literal):
                reads.add(i.l)
            writes.add(i.r)

        elif isinstance(i, ir.ShiftLeft):
            reads.add(i.reg)

        elif isinstance(i, ir.ShiftRight):
            reads.add(i.reg)

        elif isinstance(i, ir.Add):
            if not isinstance(i.l, vv.Literal):
                reads.add(i.l)
            reads.add(i.r)
            writes.add(i.r)

        elif isinstance(i, ir.SetE):
            writes.add(i.reg)

        elif isinstance(i, ir.SetNE):
            writes.add(i.reg)

        elif isinstance(i, ir.And):
            reads.add(i.reg)
            writes.add(i.reg)

        elif isinstance(i, ir.IfExp):
            else_la = liveness(i.else_, lafter)
            then_la = liveness(i.then, lafter)
            
            b = else_la[0].lbefore.union(then_la[0].lbefore)
            test_la = liveness(i.test_instructions, b)
            lbefore = test_la[0].lbefore
            liveness_instrs.append(LivenessIfExpr(lbefore, lafter, test_la, then_la, else_la))

            lafter = lbefore
            continue

        elif isinstance(i, ir.Neg):
            reads.add(i.v)
            writes.add(i.v)

        elif isinstance(i, ir.Print):
            # caller save registers
            pass

        elif isinstance(i, ir.CallFunc):
            # caller save registers
            pass

        elif isinstance(i, ir.CallStar):
            reads.add(i.fname)

        elif isinstance(i, ir.Input):
            # caller save registers
            pass

        elif isinstance(i, ir.Push):
            reads.add(i.register)

        elif isinstance(i, ir.Label):
            pass

        elif isinstance(i, ir.Jmp):
            pass

        elif isinstance(i, ir.JmpEq):
            pass

        else:
            raise Exception("Unsupported instruction %s" % i.__class__.__name__)

        lbefore = (lafter - writes).union(reads)
        liveness_instrs.append(LivenessData(i, lbefore, lafter))
        lafter = lbefore

    liveness_instrs.reverse()
    return liveness_instrs
            

if __name__ == '__main__':
    import compiler
    p0 = '''
x = 1'''
    flat = flt.Flattener()
    machine_code = gen.generate(flat.flatten(exp.explicate(compiler.parse(p0))))
    l = liveness(machine_code)
    print l







    













#
#def liveness_analysis(instructions):
#  liveness = [set()]
#  liveness_after = set()
#  for i in reversed(instructions):
#    liveness.append((set(liveness[-1]).difference(set(i.writes()))).union(set(i.reads())))
#    liveness_before = liveness[-1]
#    i.liveness_before = liveness_before
#    i.liveness_after = liveness_after
#    i.liveness_after = liveness_before
#
#  # Chop off the last element because it is always the empty set and
#  # it is inconvenient to have more items in the liveness analysis than instructions
#  liveness_less = liveness[:-1]
#  liveness_less.reverse()
#  return liveness_less
#
