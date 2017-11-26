from llvmlite import ir
import assembly_types as T
import values_variables as vv

class Builder():
    integer = ir.IntType(32)
    void = ir.VoidType()
    fnty_main = ir.FunctionType(integer, ())
    zero = ir.Constant(integer, 0)
    int1 = ir.IntType(1)

    def __init__(self, ns):
        self.ns = ns
        self.variable_mapping = {}
        self.module = None
        

    def build(self):
        self.variable_mapping = {}
        self.module = None
        self.module = ir.Module(name=__file__)
        func_main  = ir.Function(self.module, Builder.fnty_main, name='main')
        block = func_main.append_basic_block(name='entry')
        builder = ir.IRBuilder(block)

        def iterate(builder, ns):
            for n in ns:
                if isinstance(n, T.Assign):
                    exp = n.simple
                    if isinstance(exp, vv.Value):
                        res = ir.Constant(Builder.integer, exp.v)
                    elif isinstance(exp, T.InjectInt):
                        func = self.create_inject_int(builder)
                        res = builder.call(func, [self.variable_mapping[exp.val]])
                    elif isinstance(exp, T.InjectBool):
                        func = self.create_inject_bool(builder)
                        res = builder.call(func, [self.variable_mapping[exp.val]])
                    elif isinstance(exp, T.InjectBig):
                        func = self.create_inject_big(builder)
                        res = builder.call(func, [self.variable_mapping[exp.val]])
                    elif isinstance(exp, T.ProjectInt):
                        func = self.create_project_int(builder)
                        res = builder.call(func, [self.variable_mapping[exp.val]])
                    elif isinstance(exp, T.ProjectBool):
                        func = self.create_project_bool(builder)
                        res = builder.call(func, [self.variable_mapping[exp.val]])
                    elif isinstance(exp, T.ProjectBig):
                        func = self.create_project_big(builder)
                        res = builder.call(func, [self.variable_mapping[exp.val]])
                    elif isinstance(exp, T.Input):
                        func = self.create_input(builder)
                        res = builder.call(func, [])
                    elif isinstance(exp, T.CallFunc) and exp.func_name == "is_int":
                        func = self.create_is_int(builder)
                        res = builder.call(func, [self.variable_mapping[exp.args[0]]])
                    elif isinstance(exp, T.CallFunc) and exp.func_name == "is_bool":
                        func = self.create_is_bool(builder)
                        res = builder.call(func, [self.variable_mapping[exp.args[0]]])
                    elif isinstance(exp, T.CallFunc) and exp.func_name == "add":
                        l = self.variable_mapping[exp.args[0]]
                        r = self.variable_mapping[exp.args[1]]
                        func = self.create_add(builder)
                        res = builder.call(func, [l, r])

                    elif isinstance(exp, T.Add):
                        l = self.variable_mapping[exp.left]
                        r = self.variable_mapping[exp.right]
                        res = builder.add(lhs=l, rhs=r)
                    elif isinstance(exp, vv.Variable):
                        res = self.variable_mapping[exp]
                    else:
                        raise Exception("unsupported ", exp)

                    self.variable_mapping[n.assmt] = res

                elif isinstance(n, T.Print):
                    func = self.create_print_any(builder)
                    res = builder.call(func, [self.variable_mapping[n.val]])
                elif isinstance(n, T.IfExp):
                    func = self.create_is_true(builder)
                    is_true = builder.call(func, [self.variable_mapping[n.test_var]])
                    bool_is_true = builder.icmp_unsigned('!=', lhs=is_true, rhs=Builder.zero)
                    with builder.if_else(bool_is_true) as (then, otherwise):
                        with then:
                            iterate(builder, n.then)
                        with otherwise:
                            iterate(builder, n.else_)
                else:
                    raise Exception("unsupported", n)

        iterate(builder, self.ns)
        builder.ret(Builder.zero)

    def create_inject_int(self, builder):
        try:
            return self.variable_mapping['inject_int'] 
        except KeyError:
            func_type = ir.FunctionType(Builder.integer, (Builder.integer,))
            func = ir.Function(self.module, func_type, name='inject_int')
            self.variable_mapping['inject_int'] = func 
            return func

    def create_inject_big(self, builder):
        try:
            return self.variable_mapping['inject_big'] 
        except KeyError:
            func_type = ir.FunctionType(Builder.integer, (Builder.integer,))
            func = ir.Function(self.module, func_type, name='inject_big')
            self.variable_mapping['inject_big'] = func 
            return func

    def create_project_int(self, builder):
        try:
            return self.variable_mapping['project_int'] 
        except KeyError:
            func_type = ir.FunctionType(Builder.integer, (Builder.integer,))
            func = ir.Function(self.module, func_type, name='project_int')
            self.variable_mapping['project_int'] = func 
            return func

    def create_project_big(self, builder):
        try:
            return self.variable_mapping['project_big'] 
        except KeyError:
            func_type = ir.FunctionType(Builder.integer, (Builder.integer,))
            func = ir.Function(self.module, func_type, name='project_big')
            self.variable_mapping['project_big'] = func 
            return func

    def create_project_bool(self, builder):
        try:
            return self.variable_mapping['project_bool'] 
        except KeyError:
            func_type = ir.FunctionType(Builder.integer, (Builder.integer,))
            func = ir.Function(self.module, func_type, name='project_bool')
            self.variable_mapping['project_bool'] = func 
            return func

    def create_inject_bool(self, builder):
        try:
            return self.variable_mapping['inject_bool'] 
        except KeyError:
            func_type = ir.FunctionType(Builder.integer, (Builder.integer,))
            func = ir.Function(self.module, func_type, name='inject_bool')
            self.variable_mapping['inject_bool'] = func 
            return func

    def create_print_any(self, builder):
        try:
            return self.variable_mapping['print_any'] 
        except KeyError:
            func_type = ir.FunctionType(Builder.void, (Builder.integer,))
            func = ir.Function(self.module, func_type, name='print_any')
            self.variable_mapping['print_any'] = func 
            return func

    def create_input(self, builder):
        try:
            return self.variable_mapping['input'] 
        except KeyError:
            func_type = ir.FunctionType(Builder.integer, ())
            func = ir.Function(self.module, func_type, name='input')
            self.variable_mapping['input'] = func 
            return func

    def create_is_true(self, builder):
        try:
            return self.variable_mapping['is_true']
        except KeyError:
            func_type = ir.FunctionType(Builder.integer, (Builder.integer,))
            func = ir.Function(self.module, func_type, name='is_true')
            self.variable_mapping['is_true'] = func 
            return func

    def create_is_int(self, builder):
        try:
            return self.variable_mapping['is_int']
        except KeyError:
            func_type = ir.FunctionType(Builder.integer, (Builder.integer,))
            func = ir.Function(self.module, func_type, name='is_int')
            self.variable_mapping['is_int'] = func 
            return func

    def create_is_bool(self, builder):
        try:
            return self.variable_mapping['is_bool']
        except KeyError:
            func_type = ir.FunctionType(Builder.integer, (Builder.integer,))
            func = ir.Function(self.module, func_type, name='is_bool')
            self.variable_mapping['is_bool'] = func 
            return func

    def create_add(self, builder):
        try:
            return self.variable_mapping['add']
        except KeyError:
            func_type = ir.FunctionType(Builder.integer, (Builder.integer, Builder.integer))
            func = ir.Function(self.module, func_type, name='add')
            self.variable_mapping['add'] = func
            return func
