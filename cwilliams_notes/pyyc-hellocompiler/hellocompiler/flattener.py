from compiler.ast import *
from ast_types import *
import compiler
import explicate
import flattener_errors as errs
import assembly_types as t
import values_variables as vv
import registers
import x86_ir as ir



class Flattener():
    def __init__(self):
        self.next = 0
        self.next_string = 0
        self.instrucstions = []
        self.variable_mapping = {}
        self.bool_mapping = {}
        self.strings_mapping = {}

    def get_static_section(self, name):
        section = []
        section.append(ir.Section(name))
        for k, v in self.strings_mapping.iteritems():
            section += [ir.Label(str(v)[1:]),
                        ir.StringConstant(k)]
        return section

    def get_new_var(self):
        cur = self.next
        self.next = self.next + 1
        return vv.Variable(cur)

    def get_new_str(self):
        cur = self.next_string
        self.next_string += 1
        return vv.StrValue(cur)

    def assign_new(self, e):
        v = self.get_new_var()
        return ([t.Assign(v, e)], v)

    def descend(self, n):
        if isinstance(n, Module):
            if n.doc:
                raise errs.DocError
            self.instructions = self.descend(n.node)

        elif isinstance(n, Stmt):
            flat_expressions = []
            for stmt in n.nodes:
                (s, slast) = self.descend(stmt)
                flat_expressions += s 
            return flat_expressions

        elif isinstance(n, Function):
            def get_ebp(v, offset):
                try:
                    var = self.variable_mapping[v]
                    return v
                except KeyError:
                    var = registers.OffsetEBP(-offset)
                    self.variable_mapping[v] = var
                    return v
            start_offset = 2
            fname = get_ebp(n.name, start_offset)
            args = []
            for i, arg in enumerate(n.argnames):
                args.append(get_ebp(arg, i+1+start_offset))
            self.instructions = [t.Function(fname, args, self.descend(n.code))]

        elif isinstance(n, Return):
            (instrs, v) = self.descend(n.value)
            instrs.append(t.Return(v))
            return (instrs, v)

        elif isinstance(n, Assign):
            if len(n.nodes) > 1:
                raise errs.MultipleAssignmentError
            
            (sn, snlast) = self.descend(n.expr)
            assmt_node = n.nodes[0]
            if isinstance(assmt_node, AssName):
                v = n.nodes[0].name
                self.variable_mapping[v] = snlast
                return (sn, snlast)
            elif isinstance(assmt_node, Subscript):
                # get the variable for the list/dictionary
                (var_i, var) = self.descend(assmt_node.expr)
                # key
                sub = assmt_node.subs[0]
                (subi, subv) = self.descend(sub)
                return (var_i + sn + subi + [t.SubscriptAssign(var, subv, snlast)], var)
            
            elif isinstance(assmt_node, AssAttr):
                (var_i, var) = self.descend(assmt_node.expr)
                (i_attr, var_attr) = self.descend(assmt_node.attrname)
                (set_i, set_v) = self.assign_new(t.CallFunc('set_attr', [var, var_attr, snlast]))
                return (sn + var_i + i_attr + set_i, set_v)

            else:
                raise Exception("Assign unsupported for: %s" % n)
                
        
        elif isinstance(n, Discard):
            return self.descend(n.expr)

        elif isinstance(n, Subscript):
            # Get subscript
            (sn, snlast) = self.descend(n.expr)
            (si, silast) = self.descend(n.subs[0])
            (assmt_instrs, assmt_var) = self.assign_new(t.GetSubscript(snlast, silast))
            return (sn + si + assmt_instrs, assmt_var)

        elif isinstance(n, Add):
            stmts = []
            try:
                (sl, slLast) = self.descend(n.left)
            except Exception:
                raise Exception()
            (sr, srLast) = self.descend(n.right)
            stmts += sl + sr
            
            (assn_instrs, assn_var) = self.assign_new(t.Add(slLast, srLast))
            return (stmts + assn_instrs, assn_var)

        elif isinstance(n, UnarySub):
            (s, slast) = self.descend(n.expr)
            (assmt_instrs, assmt_var) = self.assign_new(t.Neg(slast))
            return (s + assmt_instrs, assmt_var)

        elif isinstance(n, Const):
            if isinstance(n.value, str):
                return self.descend(n.value)
            if n.value == None:
                return ([], None)
            (assmt_instrs_1, assmt_var) = self.assign_new(vv.Value(n.value))
            (assmt_instrs_2, assmt_var) = self.assign_new(t.InjectInt(assmt_var))
            return (assmt_instrs_1 + assmt_instrs_2, assmt_var)

        elif isinstance(n, AssName):
            try:
                var = self.variable_mapping[n.name]
            except KeyError:
                var = self.get_new_var()
                self.variable_mapping[n.name] = var
            return ([], var)

        elif isinstance(n, Name):
            try:
                var = self.variable_mapping[n.name]
                return ([], var)
            except KeyError:
                return ([], n)
                #raise Exception("usage of unassigned var: %s" % n.name)

        elif isinstance(n, Printnl):
            if len(n.nodes) > 1:
                raise errs.MultiplePrintError
            if n.dest:
                raise errs.PrintingOutputError
            (s, slast) = self.descend(n.nodes[0])
            s.append(t.Print(slast))
            return (s, slast)
    
        elif isinstance(n, CallUserFunc):
            args_instrs = []
            args = []
            for arg in n.args:
                (arg_instr, v) = self.descend(arg)
                args_instrs += arg_instr
                args.append(v)
            (instrs_name, v_name) = self.descend(n.node)
            (assn_f_ptr, v_f_ptr) = self.assign_new(t.CallFunc('get_fun_ptr', [v_name]))
            (assn_big, v_big) = self.assign_new(t.InjectBig(v_f_ptr))
            (instr_f_vars, v_f_vars) = self.assign_new(t.CallFunc('get_free_vars', 
                                                                  [v_name]))
            (assn_instrs, v) = self.assign_new(t.CallStar(v_f_ptr, [v_f_vars] + args))
            return (args_instrs+ \
                    instrs_name+ \
                    assn_f_ptr+ \
                    assn_big+ \
                    instr_f_vars + assn_instrs, v)

    
        elif isinstance(n, CallFunc):
            try:
                name = n.node.name
            except Exception:
                name = None

            if name == 'input':
                instrs = []
                (assn_instrs, assn_var) = self.assign_new(t.Input())
                instrs += assn_instrs
                (assn_instrs, assn_var) = self.assign_new(t.InjectInt(assn_var))
                instrs += assn_instrs
                return (instrs, assn_var)
            else:
                args_instrs = []
                args = []
                (name_instr, name) = self.descend(n.node)
                for arg in n.args:
                    (arg_instr, v) = self.descend(arg)
                    args_instrs += arg_instr
                    args.append(v)
                if isinstance(name, Name):
                    (assn_instrs, v) = self.assign_new(t.CallFunc(name.name, args))
                elif isinstance(name, vv.Variable):
                    (assn_instrs, v) = self.assign_new(t.CallStar(name, args))
                else:
                    raise Exception("Unsupported type %s" % name)

                return (name_instr + args_instrs + assn_instrs, v)

        elif isinstance(n, Bool):
            if n.value == None:
                return ([], None)
            (assmt_instrs_1, assmt_var) = self.assign_new(vv.BoolValue(n.value))
            (assmt_instrs_2, assmt_var) = self.assign_new(t.InjectBool(assmt_var))
            return (assmt_instrs_1 + assmt_instrs_2, assmt_var)

        elif isinstance(n, List):
            instrs = []
            nodes = n.nodes
            l = len(nodes)
            (instrs, v) = self.descend(Const(l))
            (assmt_instrs, assmt_var) = self.assign_new(t.List(v))
            (inj_instrs, inj_var) = self.assign_new(t.InjectBig(assmt_var))
            instrs += instrs + assmt_instrs + inj_instrs

            for i, n in enumerate(nodes):
                (s, slast) = self.descend(n)
                (si, silast) = self.descend(Const(i))
                instrs += s + si
                instrs.append(t.SubscriptAssign(inj_var, silast, slast))

            return (instrs, inj_var)


        
        elif isinstance(n, IfExp):
            (stest, stestlast) = self.descend(n.test)
            v = self.get_new_var()

            if isinstance(n.then, Stmt):
                sthen, thenvar = self.descend(n.then), stestlast
            else:
                (sthen, thenvar) = self.descend(n.then)
                sthen.append(t.Assign(v, thenvar))

            if isinstance(n.else_, Stmt):
                selse, elsevar = self.descend(n.else_), stestlast
            else:
                (selse, elsevar) = self.descend(n.else_)
                selse.append(t.Assign(v, elsevar))

            stest.append(t.IfExp(stestlast, sthen, selse))
            return (stest, v)

        elif isinstance(n, Let):
            var = n.var
            rhs = n.rhs
            body = n.body
            (s, last) = self.descend(rhs)
            self.variable_mapping[var.name] = last
            (sb, sblast) = self.descend(body)
            return (s + sb, sblast)

        elif isinstance(n, CompareExactly):
            (sl, sllast) = self.descend(n.l)
            (sr, srlast) = self.descend(n.r)
            (assign_instr, assn_var) = self.assign_new(t.CmpEq(sllast, srlast))
            return (sl + sr + assign_instr, assn_var)

        elif isinstance(n, Compare):
            (sl, sllast) = self.descend(n.expr)
            op = n.ops[0]
            (sr, srlast) = self.descend(op[1])
            cmp_ = None
            if op[0] == '==':
                cmp_ = t.CmpEq(sllast, srlast)
            elif op[0] == '!=':
                cmp_ = t.CmpNEq(sllast, srlast)
            (assn_instr, assn_var) = self.assign_new(cmp_)
            return (sl + sr + assn_instr, assn_var)

        elif isinstance(n, CompareTag):
            tag_type = n.tag_type
            var = n.var
            if tag_type == INT_TYPE:
                func = 'is_int'
            elif tag_type == BOOL_TYPE:
                func = 'is_bool'
            elif tag_type == BIG_TYPE:
                func = 'is_big'
            else:
                raise Exception("Unsupported tag type: %s " % tag_type)
            (arg_instrs, v) = self.descend(var)
            (assn_instrs, assn_var) = self.assign_new(t.CallFunc(func, [v]))
            return (arg_instrs + assn_instrs, assn_var)

        elif isinstance(n, InjectFrom):
            tag_type = n.typ
            arg = n.arg

            instrs = []
            (arg_instrs, last) = self.descend(arg)
            instrs += arg_instrs
            
            if tag_type == 'int':
                (assn_instrs, assn_var) = self.assign_new(t.InjectInt(last))
            elif tag_type == 'bool':
                (assn_instrs, assn_var) = self.assign_new(t.InjectBool(last))
            elif tag_type == 'big':
                (assn_instrs, assn_var) = self.assign_new(t.InjectBig(last))
            else:
                raise Exception("unsupported InjectFrom tag: %s" % tag_type)

            instrs += assn_instrs
            return (instrs, assn_var)

        elif isinstance(n, ProjectTo):
            tag_type = n.typ
            arg = n.arg

            instrs = []
            (arg_instrs, last) = self.descend(arg)
            instrs += arg_instrs
            
            if tag_type == 'int':
                (assn_instrs, assn_var) = self.assign_new(t.ProjectInt(last))
            elif tag_type == 'bool':
                (assn_instrs, assn_var) = self.assign_new(t.ProjectBool(last))
            elif tag_type == 'big':
                (assn_instrs, assn_var) = self.assign_new(t.ProjectBig(last))
            else:
                raise Exception("unsupported tag type: %s" % tag_type)

            instrs += assn_instrs
            return (instrs, assn_var)
        
        elif isinstance(n, Dict):
            instrs = []
            (assmt_instrs, assmt_var) = self.assign_new(t.Dict())
            (big_assmt_instrs, big_assmt_var) = self.assign_new(t.InjectBig(assmt_var))
            instrs += assmt_instrs + big_assmt_instrs
            for item in n.items:
                k, v = item[0], item[1]
                (k_instrs, k_var) = self.descend(k)
                (v_instrs, v_var) = self.descend(v)
                instrs += v_instrs
                instrs += k_instrs
                instrs.append(t.SubscriptAssign(big_assmt_var, k_var, v_var))
            return (instrs, big_assmt_var)

        elif isinstance(n, Class):
            instrs = []
            b_instrs = []
            b_values = []
            #Handle the potential base classes
            b = List(n.bases)
            (b_instrs, b_val) = self.descend(b)
            instrs += b_instrs

            (c_instrs, c_val) = self.assign_new(t.CallFunc('create_class', [b_val]))
            instrs += c_instrs
            (c_instrs, c_val) = self.assign_new(t.InjectBig(c_val))
            instrs += c_instrs
            # Register the the class name so subsequet calls to set_attr function
            # will resolve to the correct variable (c_val)
            self.variable_mapping[n.name] = c_val

            #Handle the body
            for stmt in n.code.nodes:
                (body_instrs, body_val) = self.descend(stmt)
                instrs += body_instrs

            return (instrs, c_val)

        elif isinstance(n, vv.LabelValue):
            return ([], n)

        elif isinstance(n, str):
            try:
                return ([], self.strings_mapping[n])
            except KeyError:
                s = self.get_new_str()
                self.strings_mapping[n] = s
                return ([], s)

        else:
            raise Exception("instance of %s is not supported" % n.__class__.__name__)

    def flatten(self, ast):
        self.descend(ast)
#        print "variable mappings: ", self.variable_mapping
#        print "flattened output: >>>>>>>>"
#        for f in self.instructions:
#            print f
#        print "<<<<<<<<<<<<<<<<<<<<<<<<<<"
        return self.instructions

if __name__ == "__main__":

    program = ''' 
x = 2
def f(a):
        return x + a
print f(4)
'''
    print program
    ast = explicate.explicate(compiler.parse(program))
    print ast
    print "------------------------"
    try:
        flattener = Flattener()
        flattener.flatten(ast)
    except SyntaxError as se:
        print "SyntaxError:", se
