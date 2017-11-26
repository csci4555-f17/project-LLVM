import x86_ir as ir
import registers as r
import values_variables as vv
import liveness_analysis as liveness
import explicate as exp
import flattener as flt
import flattened_to_assembly as gen
import register_allocation as ra

class UnspillableVar(vv.Variable):
    pass

def interference_graph(liveness_analysis):
    g = {}
    def add_edges(k, vs):
        g[k] = vs
        for v in vs:
            infs = g.get(v, set())
            infs.add(k)
            g[v] = infs

    def merge_dicts(a, b):
        for k, v in b.iteritems():
            a_s = a.get(k, set())
            a[k] = a_s.union(v)
        return a

    for la in liveness_analysis:
        if isinstance(la, liveness.LivenessData):
            ins = la.instruction
            if isinstance(ins, ir.Mov):
                interferences = g.get(ins.r, set())
                interferences = interferences.union(la.lafter) - set([ins.r])
                add_edges(ins.r, interferences)

            elif isinstance(ins, ir.MovZB):
                interferences = g.get(ins.r, set())
                interferences = interferences.union(la.lafter) - set([ins.r])
                add_edges(ins.r, interferences)

            elif isinstance(ins, ir.ShiftLeft):
                interferences = g.get(ins.reg, set())
                interferences = interferences.union(la.lafter) - set([ins.reg])
                add_edges(ins.reg, interferences)

            elif isinstance(ins, ir.ShiftRight):
                interferences = g.get(ins.reg, set())
                interferences = interferences.union(la.lafter) - set([ins.reg])
                add_edges(ins.reg, interferences)

            elif isinstance(ins, ir.Print):
                for i in la.lafter:
                    interferences = g.get(i, set())
                    interferences = interferences.union(set(r.caller_save_registers())) - set([i])
                    add_edges(i, interferences)

            elif isinstance(ins, ir.Input):
                for i in la.lafter:
                    interferences = g.get(i, set())
                    interferences = interferences.union(set(r.caller_save_registers())) - set([i])
                    add_edges(i, interferences)

            elif isinstance(ins, ir.CallFunc):
                for i in la.lafter:
                    interferences = g.get(i, set())
                    interferences = interferences.union(set(r.caller_save_registers())) - set([i])
                    add_edges(i, interferences)

            elif isinstance(ins, ir.CallStar):
                for i in la.lafter:
                    interferences = g.get(i, set())
                    interferences = interferences.union(set(r.caller_save_registers())) - set([i])
                    add_edges(i, interferences)
                    
            elif isinstance(ins, ir.Add):
                interferences = g.get(ins.r, set())
                interferences = interferences.union(la.lafter) - set([ins.r])
                add_edges(ins.r, interferences)

            elif isinstance(ins, ir.And):
                interferenes = g.get(ins.reg, set())
                interferences = interferences.union(la.lafter) - set([ins.reg])
                add_edges(ins.reg, interferences)

            elif isinstance(ins, ir.Neg):
                interferences = g.get(ins.v, set())
                interferences = interferences.union(la.lafter) - set([ins.v])
                add_edges(ins.v, interferences)

            elif isinstance(ins, ir.SetE):
                ins.reg
                if ins.reg == r.AL():
                    reg = r.EAX()
                elif ins.reg == r.CL():
                    reg = r.ECX()
                else:
                    raise Exception("Unknown register %s" % ins.reg)

                interferences = g.get(reg, set())
                interferences = interferences.union(la.lafter) - set([reg])
                add_edges(reg, interferences)

            elif isinstance(ins, ir.SetNE):
                ins.reg
                if ins.reg == r.AL():
                    reg = r.EAX()
                elif ins.reg == r.CL():
                    reg = r.ECX()
                else:
                    raise Exception("Unknown register %s" % ins.reg)

                interferences = g.get(reg, set())
                interferences = interferences.union(la.lafter) - set([reg])
                add_edges(reg, interferences)

            elif isinstance(ins, ir.Label):
                pass
            elif isinstance(ins, ir.Jmp):
                pass
            elif isinstance(ins, ir.JmpEq):
                pass
            elif isinstance(ins, ir.Cmp):
                pass
            elif isinstance(ins, ir.Push):
                pass
            else:
                raise Exception("interference graph does not support %s" % ins.__class__.__name__)

        elif isinstance(la, liveness.LivenessIfExpr):
            test_g = interference_graph(la.test_instrs)
            test_t = interference_graph(la.then_instrs)
            test_e = interference_graph(la.else_instrs)

            merge_dicts(g, test_g)
            merge_dicts(g, test_t)
            merge_dicts(g, test_e)

        else:
            raise Exception("interference graph does not support %s" % la.__class__.__name__)
    return g

def prioritized_keys(interference_graph):
    ks = interference_graph.keys()
    sorted_ks = []
    while len(ks) > 0:
        max_saturation = -1 
        max_sat_k = None
        for k in ks:
            if not isinstance(k, vv.Variable):
                ks.remove(k)
                continue

            if isinstance(k, UnspillableVar):
                sorted_ks.append(k)
                ks.remove(k)
                continue

            l = len(interference_graph[k])
            if l > max_saturation:
                max_saturation = l
                max_sat_k = k

        if max_sat_k:  
            sorted_ks.append(max_sat_k)
            ks.remove(max_sat_k)

    return sorted_ks
            
def first_assignable_loc(interferences):
    for reg in r.all_usable_registers():
        if not reg in interferences:
            return reg
    return None


def color_graph(interference_graph):
    ig = dict(interference_graph)
    spilled_vars = 0
    pks = prioritized_keys(ig)
    colors = {}
    def update_dict_with_color(d, k, c):
        '''We've colored a new variable, so we want to update
        our dictionary everywhere that variable appears and replace it with its
        color'''
        for ks, vs in d.iteritems():
            lvs = list(vs)    
            for i, v in enumerate(lvs):
                if v == k:
                    lvs[i] = c
            d[ks] = set(lvs)

    for pk in pks:
        loc = first_assignable_loc(ig[pk])
        if not loc:
            loc = r.OffsetEBP(spilled_vars)
            spilled_vars += 1

        update_dict_with_color(ig, pk, loc)
        colors[pk] = loc
    return (colors, spilled_vars)



if __name__ == '__main__':
    import compiler
    p0 = '''
l = []
print l
'''
    flat = flt.Flattener()
    print exp.explicate(compiler.parse(p0))
    machine_code = gen.generate(flat.flatten(exp.explicate(compiler.parse(p0))))
    for c in machine_code:
        print c
    l = liveness.liveness(machine_code)
    for k in l:
        print k
    g = interference_graph(l)
    print g
    cg = color_graph(g)
    print cg
    new_instructions = ra.colorize_instructions(machine_code, cg)
    print new_instructions
    p = ir.header() + new_instructions + ir.footer()
    for i in p:
        print i

