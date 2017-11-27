class SimpleExpression():
    def __init__(self):
        pass
    
class Add(SimpleExpression):
    def __init__(self, left, right):
        self.left = left 
        self.right = right 

    def __str__(self):
        return "Add(%s, %s)" % (self.left, self.right)

    def __repr__(self):
        return "%s + %s" % (self.left, self.right)
    
class LLVMRuntimeAdd(SimpleExpression):
    def __init__(self, left, right):
        self.left = left 
        self.right = right 

    def __str__(self):
        return "LLVMRuntimeAdd(%s, %s)" % (self.left, self.right)

    def __repr__(self):
        return "LLVMRuntimeAdd(%s, %s)" % (self.left, self.right)

class LLVMRuntimeNeg(SimpleExpression):
    def __init__(self, val):
        self.val = val 

    def __str__(self):
        return "LLVMRuntimeNeg(%s)" % (self.val)

    def __repr__(self):
        return "LLVMRuntimeNeg(%s)" % (self.val)

class Sub(SimpleExpression):
    def __init__(self, left, right):
        self.left = left 
        self.right = right 

    def __str__(self):
        return "%s - %s" % (self.left, self.right)

    def __repr__(self):
        return "%s - %s" % (self.left, self.right)

class Neg(SimpleExpression):
    def __init__(self, val):
        self.val = val
 
    def __str__(self):
        return "- %s" % (self.val)

    def __repr__(self):
        return "- %s" % (self.val)

class StatementsAndAtom():
    def __init__(self, stmts, atom):
        self.stmts = stmts
        self.atom = atom

class Input(SimpleExpression):

    def __str__(self):
        return "input()"

class Print():
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return "print %s" % self.val

    def __repr__(self):
        return "print %s" % self.val

class Discard():
    def __init__(self, simple_expression):
        self.simple = simple_expression
    def __str__(self):
        return "%s" % self.simple

class Assign():
    def __init__(self, assmt, simple_expression):
        self.assmt = assmt
        self.simple = simple_expression

    def __str__(self):
        return "%s = %s" % (self.assmt, self.simple)

    def __repr__(self):
        return "%s = %s" % (self.assmt, self.simple)

class SubscriptAssign():
    def __init__(self, pyobj_var, key, assmt_var):
        self.pyobj_var = pyobj_var
        self.key = key
        self.assmt_var = assmt_var

    def __str__(self):
        return "%s[%s] = %s" % (self.pyobj_var, self.key, self.assmt_var)

    def __repr__(self):
        return "%s[%s] = %s" % (self.pyobj_var, self.key, self.assmt_var)

class GetSubscript():
    def __init__(self, pyobj_var, key):
        self.pyobj_var = pyobj_var
        self.key = key

    def __str__(self):
        return "%s[%s]" % (self.pyobj_var, self.key)

    def __repr__(self):
        return "%s[%s]" % (self.pyobj_var, self.key)
    
class Dict():
    def __repr__(self):
        return "{}"

    def __str__(self):
        return "{}"

class List():
    def __init__(self, length):
        self.length = length

    def __repr__(self):
        return "list(len=%s)" % (self.length)

    def __str__(self):
        return "list(len=%s)" % (self.length)

class IfExp():
    def __init__(self, test_var, then, else_):
        self.test_var = test_var
        self.then = then
        self.else_ = else_

    def __str__(self):
        return '''(if {test_var}: {{
    {then_stmts}
}}
else: {{
    {else_stmts}
}})'''.format(
            test_var=self.test_var, 
            then_stmts="\n    ".join([str(s) for s in self.then]),
            else_stmts="\n    ".join([str(s) for s in self.else_]))

    def __repr__(self):
        return '''(if {test_var}: {{
    {then_stmts}
}}
else: {{
    {else_stmts}
}})'''.format(
            test_var=self.test_var, 
            then_stmts="\n    ".join([str(s) for s in self.then]),
            else_stmts="\n    ".join([str(s) for s in self.else_]))

class CmpEq():
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "%s == %s" % (self.left, self.right)

    def __str__(self):
        return "%s == %s" % (self.left, self.right)

class CmpNEq():
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return "%s != %s" % (self.left, self.right)

    def __str__(self):
        return "%s != %s" % (self.left, self.right)

class InjectInt():
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return "inject_int(%s)" % self.val

    def __str__(self):
        return "inject_int(%s)" % self.val

class InjectBool():
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return "inject_bool(%s)" % self.val

    def __str__(self):
        return "inject_bool(%s)" % self.val
    
class InjectBig():
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return "inject_big(%s)" % self.val

    def __str__(self):
        return "inject_big(%s)" % self.val

class ProjectInt():
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return "project_int(%s)" % self.val

    def __str__(self):
        return "project_int(%s)" % self.val

class ProjectBool():
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return "project_bool(%s)" % self.val

    def __str__(self):
        return "project_bool(%s)" % self.val

class ProjectBig():
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return "project_big(%s)" % self.val

    def __str__(self):
        return "project_big(%s)" % self.val

class GetTag():
    def __init__(self, var):
        self.var = var

    def __repr__(self):
        return "get_tag(%s)" % self.var

    def __str__(self):
        return "get_tag(%s)" % self.var

class CallFunc():
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args

    def __repr__(self):
        return "%s(%s)" % (self.func_name, ", ".join([str(a) for a in self.args]))

    def __str__(self):
        return "%s(%s)" % (self.func_name, ", ".join([str(a) for a in self.args]))

class CallStar():
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args

    def __repr__(self):
        return "*%s(%s)" % (self.func_name, ", ".join([str(a) for a in self.args]))

    def __str__(self):
        return "*%s(%s)" % (self.func_name, ", ".join([str(a) for a in self.args]))

class Return():
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "return %s" % self.value

    def __str__(self):
        return "return %s" % self.value

class Function():
    def __init__(self, func_name, args, body):
        self.func_name = func_name
        self.args = args
        self.body = body

    def __repr__(self):
        return '''
def {fname}({args}):
    {body}'''.format(fname=self.func_name, 
                     args=", ".join([str(arg) for arg in self.args]),
                     body="\n".join(["\t"+str(i) for i in self.body]))

    def __str__(self):
        return '''
def {fname}({args}):
    {body}'''.format(fname=self.func_name, 
                     args=", ".join([str(arg) for arg in self.args]),
                     body="\n".join(["\t"+str(i) for i in self.body]))

