class Atom():
    pass

class Literal(Atom):
    pass

class Value(Literal):
    def __init__(self, v):
        self.v = v
        self.isvar = False

    def __str__(self):
        return "$%s" % self.v

    def __repr__(self):
        return "$%s" % self.v

    def __eq__(self,other):
        try:
        	return self.v == other.v and not other.isvar
        except Exception:
	        return False

    def __hash__(self):
        return hash(str(self))

class StrValue(Literal):
    def __init__(self, s):
        self.s = s
        self.isvar = False

    def __str__(self):
        return "$str_%s" % self.s

    def __repr__(self):
        return "$str_%s" % self.s

    def __eq__(self, other):
        return self.s == str(other)

    def __hash__(self):
        return hash(str(self))

class LabelValue(Literal):
    def __init__(self, v):
        self.v = v
        self.isvar = False

    def __str__(self):
        return "$%s" % self.v

    def __repr__(self):
        return "$%s" % self.v

    def __eq__(self,other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

class Variable(Atom):
    def __init__(self, v):
        self.v = v
        self.isvar = True
        self.unspillable = False
        self.name = str(self)

    def __str__(self):
        return "var%s" % str(self.v)

    def __repr__(self):
        return "var%s" % str(self.v)

    def __eq__(self,other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

class SubscriptVar(Atom):
    def __init__(self, v, idx):
        self.v = v
        self.idx = idx

    def __str__(self):
        return "%s[%s]" % (self.v, self.idx)

    def __repr__(self):
        return "%s[%s]" % (self.v, self.idx)

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

class BoolValue(Literal):
    def __init__(self, v):
        self.v = v
        self.isvar = False

    def __str__(self):
        return "$%s" % (1 if self.v else 0)

    def __repr__(self):
        return "$%s" % (1 if self.v else 0)


    def __eq__(self,other):
        try:
        	return self.v == other.v and not other.isvar
        except Exception:
	        return False

    def __hash__(self):
        return hash(str(self))

def is_variable(v):
  return isinstance(v, Variable)

