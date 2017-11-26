from compiler.ast import Node

INT_TYPE = 1
BOOL_TYPE = 2
BIG_TYPE = 3

class Bool(Node):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Bool(%s)" % self.value

    def __repr__(self):
        return "Bool(%s)" % self.value

class GetTag(Node):
    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return "GetTag(%s)" % self.arg

    def __repr__(self):
        return "GetTag(%s)" % self.arg

class InjectFrom(Node):
    def __init__(self, typ, arg):
        self.typ = typ
        self.arg = arg

    def getChildren(self):
        return self.typ, self.arg
        
    def getChildNodes(self):
        return self.typ, self.arg

    def __str__(self):
        return "InjectFrom(%s, %s)" % (self.typ, self.arg)

    def __repr__(self):
        return "InjectFrom(%s, %s)" % (self.typ, self.arg)

class ProjectTo(Node):
    def __init__(self, typ, arg):
        self.typ = typ
        self.arg = arg

    def getChildren(self):
        return self.typ, self.arg
        
    def getChildNodes(self):
        return self.typ, self.arg

    def __str__(self):
        return "ProjectTo(%s, %s)" % (self.typ, self.arg)

    def __repr__(self):
        return "ProjectTo(%s, %s)" % (self.typ, self.arg)

class Let(Node):
    def __init__(self, var, rhs, body):
        self.var = var
        self.rhs = rhs
        self.body = body

    def getChildren(self):
        return self.var, self.rhs, self.body
        
    def getChildNodes(self):
        return self.var, self.rhs, self.body

    def __repr__(self):
        return "Let(%s, %s, %s)" % (self.var, self.rhs, self.body)

    def __str__(self):
        return "Let(%s, %s, %s)" % (self.var, self.rhs, self.body)

class CompareExactly(Node):
    def __init__(self, l, r):
        self.l = l
        self.r = r
    
    def getChildren(self):
        return self.l, self.r
        
    def getChildNodes(self):
        return self.l, self.r

    def __repr__(self):
        return "CompareExactly(%s, %s)" % (self.l, self.r)

    def __str__(self):
        return "CompareExactly(%s, %s)" % (self.l, self.r)

class CompareTag(Node):
    def __init__(self, var, tag_type):
        self.var = var
        self.tag_type = tag_type
    
    def getChildren(self):
        return self.var, self.tag_type
        
    def getChildNodes(self):
        return self.var, self.tag_type

    def __repr__(self):
        return "CompareTag(%s, %s)" % (self.var, self.tag_type)

    def __str__(self):
        return "CompareTag(%s, %s)" % (self.var, self.tag_type)

class CallUserFunc(Node):
    def __init__(self, node, args):
        self.node = node
        self.args = args

    def getChildren(self):
        return self.node, self.args

    def getChildNodes(self):
        return self.node, self.args

    def __repr__(self):
        return "CallUserFunc(%s, %s)" % (self.node, self.args)

    def __str__(self):
        return "CallUserFunc(%s, %s)" % (self.node, self.args)

class LambdaHeapified(Node):
    def __init__(self, argnames, original_argnames, paraminits, localvars, localinits, code):
        self.argnames = argnames
        self.original_argnames = original_argnames
        self.paraminits = paraminits
        self.localvars = localvars
        self.localinits = localinits
        self.code = code

    def getChildren(self):
        return self.argnames, self.paraminits, self.localinits, self.code

    def getChildNodes(self):
        return self.argnames, self.paraminits, self.localinits, self.code

    def __repr__(self):
        return "LambdaHeapified(%s, %s, %s, %s)" % (self.argnames, self.paraminits, 
                                                    self.localinits, self.code)

    def __str__(self):
        return "LambdaHeapified(%s, %s, %s, %s)" % (self.argnames, self.paraminits, 
                                                    self.localinits, self.code)

class CreateClass(Node):
    def __init__(self, name, bases):
        self.name = name
        self.bases = bases
    
    def getChildren(self):
        return self.name, self.bases

    def getChildNodes(self):
        return self.name, self.bases

    def __repr__(self):
        return "CreateClass(%s, %s)" % (self.name, self.bases)

    def __str__(self):
        return "CreateClass(%s, %s)" % (self.name, self.bases)

class ClassCreation(Node):
    def __init__(self, name, bases, attrs, body):
        self.name = name
        self.bases = bases
        self.attrs = attrs
        self.body = body

    def getChildren(self):
        return self.name, self.bases, self.attrs, self.body

    def getChildNodes(self):
        return self.name, self.bases, self.attrs, self.body

    def __repr__(self):
        return "ClassCreation(%s, %s, %s, %s)" % (self.name, str(self.bases), 
                                                  str(self.attrs), str(self.body))

    def __str__(self):
        return "ClassCreation(%s, %s, %s, %s)" % (self.name, str(self.bases), 
                                                  str(self.attrs), str(self.body))

class SetAttr(Node):
    def __init__(self, obj, attr, expr):
        self.obj = obj
        self.attr = attr
        self.expr = expr

    def getChildren(self):
        return self.obj, self.attr, self.expr

    def getChildNodes(self):
        return self.obj, self.attr, self.expr

    def __repr__(self):
        return "SetAttr(%s, %s, %s)" % (self.obj, self.attr, self.expr)

    def __str__(self):
        return "SetAttr(%s, %s, %s)" % (self.obj, self.attr, self.expr)

class HasAttr(Node):
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr

    def getChildren(self):
        return self.obj, self.attr

    def getChildNodes(self):
        return self.obj, self.attr

    def __repr__(self):
        return "HasAttr(%s, %s)" % (self.obj, self.attr)

    def __str__(self):
        return "HasAttr(%s, %s)" % (self.obj, self.attr)

class GetAttr(Node):
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr

    def getChildren(self):
        return self.obj, self.attr

    def getChildNodes(self):
        return self.obj, self.attr

    def __repr__(self):
        return "GetAttr(%s, %s)" % (self.obj, self.attr)

    def __str__(self):
        return "GetAttr(%s, %s)" % (self.obj, self.attr)

class EitherVar():
    def __init__(self, var, this, that):
        self.var = var
        self.this = this
        self.that = that

    def __repr__(self):
        return "EitherVar(%s, %s, %s)" % (self.var, self.this, self.that)

class ParentScope():
    def __init__(self, n):
        self.n = n

    def __repr__(self):
        return "ParentScope(%s)" % self.n


class Method(Node):
    def __init__(self, name, c, argnames, code):
        self.name = name
        self.c = c
        self.argnames = argnames
        self.code = code

    def __repr__(self):
        return "Method(%s, %s, %s, %s)" % (self.name, self.c, self.argnames, self.code)

class LLVMRuntimeAdd(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def __repr__(self):
        return "llvm_runtime_add(%s, %s)" % (self.left, self.right)
    
    def __str__(self):
        return "llvm_runtime_add(%s, %s)" % (self.left, self.right)
